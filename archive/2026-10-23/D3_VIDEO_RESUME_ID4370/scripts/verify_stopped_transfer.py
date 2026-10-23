"""Read-only verification of a stopped transfer, with new local audit outputs."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess

OUT = Path(__file__).resolve().parent.parent
ROOT = OUT.parent


def digest(path, kind='sha256'):
    h = hashlib.new(kind)
    with path.open('rb') as f:
        while b := f.read(1048576):
            h.update(b)
    return h.hexdigest()


def main():
    config = json.loads((OUT/'APPROVED_CONFIG.json').read_text())
    result = json.loads((OUT/'result_0000.json').read_text())
    payload = (OUT/'journal.jsonl').read_bytes()
    assert payload.endswith(b'\n')
    events = [json.loads(x) for x in payload.splitlines()]
    previous = '0' * 64
    for i, e in enumerate(events):
        body = {k:v for k,v in e.items() if k != 'hash'}
        raw = json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
        assert e['seq'] == i and e['previous'] == previous
        assert hashlib.sha256(raw).hexdigest() == e['hash']
        previous = e['hash']
    canonical_config = json.dumps(config,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    assert events[0]['config_sha256'] == hashlib.sha256(canonical_config).hexdigest()
    requests = {}
    for e in events:
        k = e['kind']
        if k == 'BEGIN':
            requests[e['request_id']] = {'start':e['start'],'end':e['end'],'reserved':e['reserved'],'observed':0,'committed':0}
        elif k == 'HEADERS':
            r = requests[e['request_id']]
            h = {k.lower():v for k,v in e['headers'].items()}
            assert e['status'] == 206
            assert h['content-range'] == f"bytes {r['start']}-{r['end']}/357839862"
            assert h['content-length'] == str(r['reserved'])
            assert h['etag'] == config['etag'] and h['content-type'] == 'video/mp4'
            assert h.get('content-encoding','identity') == 'identity'
            assert 'transfer-encoding' not in h
            r['headers_valid'] = True
        elif k in ['BODY','COMMIT']:
            requests[e['request_id']]['observed' if k=='BODY' else 'committed'] += e['bytes']
        elif k == 'END':
            requests[e['request_id']]['exact'] = e['exact']
            requests[e['request_id']]['reason'] = e['reason']
    for r in requests.values():
        assert r['headers_valid'] and r['observed'] == r['committed']
        assert r['observed'] <= r['reserved']
        if r['exact']:
            assert r['observed'] == r['reserved']
    prefix = Path(config['prefix'])
    candidate = OUT/'candidate.mp4.partial'
    assert prefix.stat().st_size == config['prefix_bytes']
    assert digest(prefix) == config['prefix_sha256']
    bodies = [e for e in events if e['kind']=='BODY']
    commits = [e for e in events if e['kind']=='COMMIT']
    assert len(bodies) == len(commits)
    offset = config['prefix_bytes']
    with candidate.open('rb') as f:
        assert hashlib.sha256(f.read(offset)).hexdigest() == config['prefix_sha256']
        for b,c in zip(bodies,commits):
            assert (b['request_id'],b['bytes'],b['sha256']) == (c['request_id'],c['bytes'],c['sha256'])
            assert c['offset'] == offset
            chunk = f.read(c['bytes'])
            assert len(chunk) == c['bytes'] and hashlib.sha256(chunk).hexdigest() == c['sha256']
            offset += c['bytes']
        assert not f.read(1)
    assert offset == candidate.stat().st_size == result['durable_offset']
    observed = sum(r['observed'] for r in requests.values())
    upper = sum(r['observed'] if r['exact'] else r['reserved'] for r in requests.values())
    assert observed == result['observed_body_bytes'] and upper == result['charged_upper_bytes']
    assert result['status'] == 'STOPPED_ERROR' and result['request_count'] == 74
    assert upper <= config['body_budget_bytes']
    protected = json.loads((OUT/'PROTECTION_BEFORE.json').read_text())['files']
    changes = []
    for rel, record in protected.items():
        p = ROOT / rel
        if record['type'] == 'symlink':
            good = p.is_symlink() and os.readlink(p) == record['target']
        else:
            good = p.is_file() and not p.is_symlink() and p.stat().st_size==record['bytes'] and digest(p)==record['sha256']
        if not good:
            changes.append(rel)
    assert not changes
    tracked_diff = subprocess.check_output(['git','diff','HEAD','--'],cwd=ROOT,text=True)
    assert not tracked_diff
    seen = set(); logical = allocated = 0
    for base in config['disk_roots']:
        for p in Path(base).rglob('*'):
            if not p.is_file() or p.is_symlink():
                continue
            st = p.stat(); key = (st.st_dev,st.st_ino)
            if key in seen:
                continue
            seen.add(key); logical += st.st_size; allocated += st.st_blocks*512
    report = {
        'timestamp':datetime.datetime.now().astimezone().isoformat(),
        'status':'HOLD_TRANSFER_TIMEOUT_NO_RETRY',
        'journal_events':len(events),'journal_hash_chain_valid':True,'journal_sha256':digest(OUT/'journal.jsonl'),
        'config_identity_matches_journal':True,'valid_206_responses':len(requests),
        'completed_responses':sum(r['exact'] for r in requests.values()),
        'failed_responses':sum(not r['exact'] for r in requests.values()),
        'first_request_utc':next(e['utc'] for e in events if e['kind']=='BEGIN'),
        'last_event_utc':events[-1]['utc'],'last_response':requests[max(requests)],
        'new_body_observed_bytes':observed,'new_body_conservative_upper':upper,
        'new_body_exact_total':None,'uncertainty_bytes':upper-observed,
        'body_definition':'read1-delivered bytes are exact observations; after timeout, full bounded response reservation is retained; TLS/TCP and socket prefetch are not measured.',
        'historical_body_lower':17887232,'historical_body_upper':357905398,
        'combined_body_lower':17887232+observed,'combined_body_upper':357905398+upper,
        'new_budget':342115318,'combined_authorized_cap':700020716,
        'conservative_new_budget_remaining':342115318-upper,
        'original_prefix_bytes':prefix.stat().st_size,'original_prefix_sha256':digest(prefix),
        'candidate_bytes':offset,'candidate_md5_partial_only':digest(candidate,'md5'),'candidate_sha256':digest(candidate),
        'candidate_all_committed_chunks_match':True,'candidate_uncommitted_tail_bytes':0,
        'full_expected_bytes':357839862,'full_expected_md5':'c981eab775c96858da313acef769b014',
        'full_md5_obtained':None,'full_hash_gate_passed':False,
        'remaining_file_bytes':357839862-offset,'next_unrequested_or_uncommitted_offset':offset,
        'logical_disk_bytes_before_this_record':logical,'allocated_disk_bytes_before_this_record':allocated,
        'local_budget_bytes':536870912,'disk_free_bytes':shutil.disk_usage(ROOT).free,
        'protected_existing_entries':len(protected),'changed_existing_entries':changes,
        'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'tracked_diff':tracked_diff,'native_decode_executed':False,'pts_audit_executed':False,
        'frames_created':0,'external_retry_after_timeout':False,
    }
    assert max(logical,allocated) < 536870912
    with (OUT/'TRANSFER_ACCOUNTING.json').open('x') as f:
        json.dump(report,f,indent=2,ensure_ascii=False); f.write('\n')
    with (OUT/'REQUEST_AUDIT.json').open('x') as f:
        json.dump(requests,f,indent=2); f.write('\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__ == '__main__':
    main()
