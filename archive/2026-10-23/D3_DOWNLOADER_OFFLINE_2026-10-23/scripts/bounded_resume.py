"""Bounded single-file HTTP continuation. Offline by default; no automatic retries.

Exact metric: HTTP entity bytes delivered by read1(), not socket/TLS wire bytes.
Each request is durably reserved before connecting. An unsettled/failed request
keeps its whole reservation. Graceful stop drains just the current bounded range.
"""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import http.client
import ipaddress
import json
import os
from pathlib import Path
import signal
import ssl
import time
from urllib.parse import urlsplit

OFFICIAL_URL = 'https://data.bris.ac.uk/datasets/3cqb5b81wk2dc2379fx1mrxh47/Videos/P01/P01-20240202-110250.mp4'
OFFICIAL_SIZE = 357839862
OFFICIAL_MD5 = 'c981eab775c96858da313acef769b014'
OFFICIAL_PREFIX_SIZE = 17821696
OFFICIAL_PREFIX_SHA = '7639ef70768aba2c8af4652056bdf95183636e44b4738e22b2b2bb8c136fc6ee'

class GuardError(Exception):
    pass

def require(ok, message):
    if not ok:
        raise GuardError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with Path(path).open('rb') as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()

def disk_usage(roots):
    # Deduplicate overlapping roots and hard links; no symlink traversal.
    seen = set()
    total = 0
    for root in roots:
        root = Path(root)
        for p in ([root] if root.is_file() else root.rglob('*')):
            if p.is_file() and not p.is_symlink():
                st = p.stat()
                key = (st.st_dev, st.st_ino)
                if key not in seen:
                    seen.add(key)
                    total += st.st_size
    return total

class Journal:
    def __init__(self, path):
        self.path = Path(path)
        self.events = []
        self.previous = '0' * 64
        if self.path.exists():
            raw = self.path.read_bytes()
            require(not raw or raw.endswith(b'\n'), 'TRUNCATED_JOURNAL: do not repair automatically')
            for line in raw.splitlines():
                event = json.loads(line)
                claimed = event.pop('hash')
                require(event['seq'] == len(self.events), 'JOURNAL_SEQUENCE')
                require(event['previous'] == self.previous, 'JOURNAL_CHAIN')
                require(hashlib.sha256(canonical(event)).hexdigest() == claimed, 'JOURNAL_HASH')
                event['hash'] = claimed
                self.events.append(event)
                self.previous = claimed

    def append(self, kind, **fields):
        event = dict(seq=len(self.events), previous=self.previous, kind=kind,
                     utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **fields)
        event['hash'] = hashlib.sha256(canonical(event)).hexdigest()
        with self.path.open('ab', buffering=0) as f:
            payload = canonical(event) + b'\n'
            written = f.write(payload)
            require(written == len(payload), 'SHORT_JOURNAL_WRITE')
            os.fsync(f.fileno())
        self.events.append(event)
        self.previous = event['hash']
        return event

class Downloader:
    def __init__(self, config, hook=None):
        self.c = dict(config)
        self.hook = hook or (lambda phase, downloader: None)
        self.stop_requested = False
        self.last_error = None
        self._validate_config()
        self.prefix = Path(self.c['prefix']).resolve()
        raw_work = Path(self.c['work_dir']).absolute()
        require(not any(p.is_symlink() for p in [raw_work, *raw_work.parents]), 'SYMLINK_WORK_PATH')
        self.work = raw_work.resolve()
        self.work.mkdir(parents=True, exist_ok=True)
        self._lock = os.fdopen(os.open(self.work/'run.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600), 'r+b')
        try:
            fcntl.flock(self._lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._lock.close()
            raise GuardError('WORK_ALREADY_LOCKED')
        self.candidate = self.work / 'candidate.mp4.partial'
        require(self.prefix != self.candidate, 'NEVER_APPEND_TO_ORIGINAL_PREFIX')
        require(not (self.work/'journal.jsonl').is_symlink(), 'SYMLINK_JOURNAL')
        self.journal = Journal(self.work / 'journal.jsonl')
        identity = hashlib.sha256(canonical(self.c)).hexdigest()
        if self.journal.events:
            require(self.journal.events[0]['kind'] == 'INIT', 'MISSING_INIT')
            require(self.journal.events[0]['config_sha256'] == identity, 'CONFIG_CHANGED')
        else:
            require(not self.candidate.exists(), 'UNJOURNALED_CANDIDATE')
            self._check_disk(self.c['prefix_bytes'] + self.c['metadata_reserve_bytes'])
            self.journal.append('INIT', config_sha256=identity, prefix_sha256=self.c['prefix_sha256'],
                                prefix_bytes=self.c['prefix_bytes'], byte_definition='HTTP read1 delivered bytes')
            with self.prefix.open('rb') as source, self.candidate.open('xb', buffering=0) as target:
                while block := source.read(1024 * 1024):
                    require(target.write(block) == len(block), 'SHORT_PREFIX_COPY')
                os.fsync(target.fileno())
            self.journal.append('PREFIX_READY', bytes=self.c['prefix_bytes'])
        self._verify_candidate()
        # A hard exit never releases the last request's reservation.
        for request_id, item in self.state()['requests'].items():
            if item['end'] is None:
                self.journal.append('END', request_id=request_id, exact=False,
                                    reason='RECOVERED_UNSETTLED_RESERVATION')

    def _validate_config(self):
        c = self.c
        for field in ['prefix_bytes','total_bytes','request_bytes','read_bytes','body_budget_bytes','disk_budget_bytes','metadata_reserve_bytes']:
            require(type(c[field]) is int and c[field] >= 0, 'NONNEGATIVE_INTEGER_'+field)
        parsed = urlsplit(c['url'])
        require(not parsed.username and not parsed.password and not parsed.fragment, 'URL_SHAPE')
        if c['mode'] == 'offline':
            require(parsed.scheme == 'http', 'OFFLINE_SCHEME')
            try:
                address = ipaddress.ip_address(parsed.hostname or '')
            except ValueError:
                raise GuardError('OFFLINE_REQUIRES_NUMERIC_LOOPBACK')
            require(address.is_loopback, 'OFFLINE_NON_LOOPBACK_FORBIDDEN')
        else:
            require(c['mode'] == 'approved_single_video', 'MODE')
            require(c.get('approved') is True and bool(c.get('approval_reference')), 'REMOTE_NOT_APPROVED')
            require(c['url'] == OFFICIAL_URL, 'ONLY_FIXED_VIDEO_ALLOWED')
            require(c['total_bytes'] == OFFICIAL_SIZE and c['expected_md5'] == OFFICIAL_MD5, 'FIXED_FILE_IDENTITY')
            require(c['prefix_bytes'] == OFFICIAL_PREFIX_SIZE and c['prefix_sha256'] == OFFICIAL_PREFIX_SHA, 'FIXED_PREFIX_IDENTITY')
        require(c['etag'] and not c['etag'].startswith('W/') and c['etag'].startswith('"'), 'STRONG_ETAG_REQUIRED')
        require(0 <= c['prefix_bytes'] <= c['total_bytes'], 'PREFIX_SIZE')
        require(1 <= c['request_bytes'] <= 1048576, 'REQUEST_MAX_1_MIB')
        require(1 <= c['read_bytes'] <= 65536, 'READ_MAX_64_KIB')
        require(0 < c['timeout_seconds'] <= 60, 'BOUNDED_READ_TIMEOUT')
        require(c['body_budget_bytes'] >= 0 and c['disk_budget_bytes'] > 0, 'BUDGETS')
        p = Path(c['prefix'])
        require(p.is_file() and not p.is_symlink(), 'PREFIX_FILE')
        require(p.stat().st_size == c['prefix_bytes'], 'PREFIX_SIZE_CHANGED')
        require(digest(p) == c['prefix_sha256'], 'PREFIX_HASH_CHANGED')
        roots = [Path(x).resolve() for x in c['disk_roots']]
        work = Path(c['work_dir']).resolve()
        require(any(work == r or r in work.parents for r in roots), 'DISK_ROOT_MUST_COVER_WORK')
        require(any(p.resolve() == r or r in p.resolve().parents for r in roots), 'DISK_ROOT_MUST_COVER_PREFIX')

    def state(self):
        requests = {}
        offset = self.c['prefix_bytes']
        committed = []
        for e in self.journal.events:
            k = e['kind']
            if k == 'BEGIN':
                requests[e['request_id']] = dict(reserved=e['reserved'], observed=0, end=None)
            elif k == 'BODY':
                requests[e['request_id']]['observed'] += e['bytes']
            elif k == 'COMMIT':
                require(e['offset'] == offset, 'NONCONTIGUOUS_COMMIT')
                offset += e['bytes']
                committed.append(e)
            elif k == 'END':
                item = requests[e['request_id']]
                require(item['end'] is None, 'DUPLICATE_END')
                item['end'] = e
        observed = sum(x['observed'] for x in requests.values())
        charged = sum(x['observed'] if x['end'] and x['end']['exact'] else x['reserved'] for x in requests.values())
        return dict(requests=requests, observed_body_bytes=observed, charged_upper_bytes=charged,
                    durable_offset=offset, committed=committed,
                    uncertain_requests=sum(1 for x in requests.values() if not x['end'] or not x['end']['exact']))

    def close(self):
        if hasattr(self, '_lock') and not self._lock.closed:
            fcntl.flock(self._lock.fileno(), fcntl.LOCK_UN)
            self._lock.close()

    def _candidate_handle(self, writable=False):
        require(not self.candidate.is_symlink(), 'SYMLINK_CANDIDATE')
        fd = os.open(self.candidate, (os.O_RDWR if writable else os.O_RDONLY) | os.O_NOFOLLOW)
        st = os.fstat(fd)
        original = self.prefix.stat()
        if st.st_nlink != 1 or (st.st_dev, st.st_ino) == (original.st_dev, original.st_ino):
            os.close(fd)
            raise GuardError('HARDLINK_CANDIDATE_ORIGINAL')
        return os.fdopen(fd, 'r+b' if writable else 'rb', buffering=0)

    def _verify_candidate(self):
        s = self.state()
        require(self.candidate.exists() and self.candidate.stat().st_size == s['durable_offset'],
                'UNCOMMITTED_DISK_TAIL_OR_MISSING_DATA: preserve file and stop')
        with self._candidate_handle() as f:
            h = hashlib.sha256()
            left = self.c['prefix_bytes']
            while left:
                block = f.read(min(left, 1048576)); require(block, 'SHORT_CANDIDATE_PREFIX')
                h.update(block); left -= len(block)
            require(h.hexdigest() == self.c['prefix_sha256'], 'CANDIDATE_PREFIX_CHANGED')
            for e in s['committed']:
                b = f.read(e['bytes'])
                require(len(b) == e['bytes'] and hashlib.sha256(b).hexdigest() == e['sha256'], 'COMMITTED_CHUNK_CHANGED')

    def _check_disk(self, added):
        require(disk_usage(self.c['disk_roots']) + added <= self.c['disk_budget_bytes'], 'DISK_BUDGET')

    def _headers(self, response, start, end):
        require(response.status == 206, 'EXPECTED_206_NO_REDIRECT_OR_200_FALLBACK')
        require(response.getheader('Content-Range') == f'bytes {start}-{end}/{self.c["total_bytes"]}', 'CONTENT_RANGE')
        require(response.getheader('Content-Length') == str(end - start + 1), 'CONTENT_LENGTH')
        require(response.getheader('ETag') == self.c['etag'], 'ETAG_CHANGED')
        require(response.getheader('Content-Encoding', 'identity').lower() == 'identity', 'CONTENT_ENCODING')
        require(response.getheader('Transfer-Encoding') is None, 'TRANSFER_ENCODING')
        require(response.getheader('Content-Type', '').split(';')[0] == self.c['content_type'], 'CONTENT_TYPE')

    def _request(self, start, end):
        n = end - start + 1
        s = self.state()
        require(s['charged_upper_bytes'] + n <= self.c['body_budget_bytes'], 'BODY_BUDGET')
        self._check_disk(n + self.c['metadata_reserve_bytes'])
        request_id = len(s['requests'])
        self.journal.append('BEGIN', request_id=request_id, start=start, end=end, reserved=n)
        self.hook('after_begin', self)
        u = urlsplit(self.c['url'])
        connection = (http.client.HTTPSConnection(u.hostname, u.port, timeout=self.c['timeout_seconds'], context=ssl.create_default_context())
                      if u.scheme == 'https' else http.client.HTTPConnection(u.hostname, u.port, timeout=self.c['timeout_seconds']))
        got = 0
        try:
            path = u.path or '/'
            if u.query:
                path += '?' + u.query
            connection.request('GET', path, headers={'Range':f'bytes={start}-{end}',
                'If-Match':self.c['etag'], 'Accept-Encoding':'identity', 'Connection':'close'})
            response = connection.getresponse()
            self.journal.append('HEADERS', request_id=request_id, status=response.status,
                                headers={k:v for k,v in response.getheaders() if k.lower() in
                                         ['content-range','content-length','etag','content-encoding','content-type','transfer-encoding']})
            self._headers(response, start, end)
            self.hook('after_headers', self)
            with self._candidate_handle(writable=True) as target:
                target.seek(start)
                while got < n:
                    block = response.read1(min(self.c['read_bytes'], n - got))
                    require(block, 'SHORT_RESPONSE')
                    self.hook('after_read', self)
                    chunk_sha = hashlib.sha256(block).hexdigest()
                    # Durable received-byte record precedes any file mutation.
                    self.journal.append('BODY', request_id=request_id, bytes=len(block), sha256=chunk_sha)
                    self.hook('after_body', self)
                    self._check_disk(len(block) + self.c['metadata_reserve_bytes'])
                    require(target.write(block) == len(block), 'SHORT_FILE_WRITE')
                    os.fsync(target.fileno())
                    self.hook('after_write', self)
                    self.journal.append('COMMIT', request_id=request_id, offset=start+got,
                                        bytes=len(block), sha256=chunk_sha)
                    got += len(block)
                    self.hook('after_commit', self)
            self.journal.append('END', request_id=request_id, exact=True, reason='COMPLETE_BOUNDED_RESPONSE')
            return True
        except Exception as error:
            self.last_error = f'{type(error).__name__}: {error}'
            self.journal.append('END', request_id=request_id, exact=False, reason=self.last_error)
            return False
        finally:
            connection.close()

    def stop(self, signum=None, frame=None):
        self.stop_requested = True

    def run(self):
        handlers = {sig:signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
        for sig in handlers:
            signal.signal(sig, self.stop)
        status = 'ERROR'
        try:
            self._verify_candidate()
            while self.state()['durable_offset'] < self.c['total_bytes']:
                if self.stop_requested:
                    status = 'STOPPED_CLEANLY'
                    break
                s = self.state()
                start = s['durable_offset']
                # An uncertain request may have spent the retry allowance. Do not
                # start another request if completion cannot fit the proven budget.
                require(s['charged_upper_bytes'] + self.c['total_bytes'] - start <= self.c['body_budget_bytes'], 'INSUFFICIENT_COMPLETION_BUDGET')
                end = min(start+self.c['request_bytes'], self.c['total_bytes'])-1
                if not self._request(start, end):
                    status = 'STOPPED_ERROR'
                    break
            else:
                require(self.candidate.stat().st_size == self.c['total_bytes'], 'FINAL_SIZE')
                md5 = digest(self.candidate, 'md5')
                require(md5 == self.c['expected_md5'], 'FINAL_MD5_MISMATCH')
                self.journal.append('VERIFIED', bytes=self.c['total_bytes'], md5=md5,
                                    sha256=digest(self.candidate))
                status = 'VERIFIED'
        except Exception as error:
            self.last_error = f'{type(error).__name__}: {error}'
            self.journal.append('STOP', reason=self.last_error)
            status = 'STOPPED_ERROR'
        finally:
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
        state = self.state()
        result = {k:v for k,v in state.items() if k not in ['requests','committed']}
        result.update(status=status, error=self.last_error, stop_requested=self.stop_requested,
                      request_count=len(state['requests']), candidate=str(self.candidate),
                      body_metric='Durably recorded HTTP read1-delivered bytes; a lower bound after an unsettled request; TLS/TCP/socket prefetch not measured',
                      original_prefix_unchanged=digest(self.prefix)==self.c['prefix_sha256'])
        result_file = self.work / f'result_{len(list(self.work.glob("result_*.json"))):04d}.json'
        with result_file.open('x') as f:
            json.dump(result, f, indent=2); f.write('\n')
        self.close()
        return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text())
        result = Downloader(config).run()
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result['status'] in ['VERIFIED','STOPPED_CLEANLY'] else 2
    except Exception as error:
        print(json.dumps({'status':'REFUSED_BEFORE_RUN','error':str(error)}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
