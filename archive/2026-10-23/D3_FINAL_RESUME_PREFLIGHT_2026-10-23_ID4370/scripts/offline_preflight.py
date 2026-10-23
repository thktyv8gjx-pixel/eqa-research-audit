"""No network: verify frozen prefix/ledger and exercise real arithmetic guards.

These guard checks do NOT establish a bound for socket/TLS response prefetch.
The downloader itself and all historical files are read-only inputs.
"""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import unittest.mock as mock

OUT = Path(__file__).resolve().parent.parent
ROOT = OUT.parent
OLD = ROOT/'D3_VIDEO_RESUME_ID4370'
SOURCE = ROOT/'D3_DOWNLOADER_OFFLINE_2026-10-23/scripts/bounded_resume.py'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while b := f.read(1048576): h.update(b)
    return h.hexdigest()


def main():
    assert sha(SOURCE) == '9375e83a8cd043ae9d93eb61415979ec2000650b012a47a2737ebe319f425d30'
    spec = importlib.util.spec_from_file_location('reviewed_downloader', SOURCE)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    config = json.loads((OLD/'APPROVED_CONFIG.json').read_text())
    events = mod.Journal(OLD/'journal.jsonl').events  # read/verify only; no append
    assert len(events) == 9924
    assert events[0]['config_sha256'] == hashlib.sha256(mod.canonical(config)).hexdigest()
    holder = mod.Downloader.__new__(mod.Downloader)
    holder.c = config; holder.journal = type('FrozenJournal', (), {'events':events})()
    state = holder.state()
    assert state['observed_body_bytes'] == 77053660
    assert state['charged_upper_bytes'] == 77594624
    assert state['durable_offset'] == 94875356
    candidate = OLD/'candidate.mp4.partial'
    assert candidate.stat().st_size == state['durable_offset']
    assert sha(candidate) == '93a895270832fc42d1a4f447f748c3d1bb4750f8041a671ec07dddc51bf8006f'
    with candidate.open('rb') as f:
        assert hashlib.sha256(f.read(config['prefix_bytes'])).hexdigest() == config['prefix_sha256']
        offset = config['prefix_bytes']
        for e in state['committed']:
            assert e['offset'] == offset
            b = f.read(e['bytes'])
            assert len(b) == e['bytes'] and hashlib.sha256(b).hexdigest() == e['sha256']
            offset += len(b)
        assert not f.read(1)
    assert offset == 94875356
    missing = config['total_bytes']-offset
    remaining = config['body_budget_bytes']-state['charged_upper_bytes']
    assert (missing,remaining,remaining-missing) == (262964506,264520694,1556188)

    # Synthetic state exercises the existing run() preflight; intercepted
    # request calls are recorded in memory and can never reach transport.
    checks = []
    class NullJournal:
        def append(self, *a, **kw): pass
    for name,budget,expected_calls in [
        ('current_balance',342115318,1),
        ('exact_completion_balance',77594624+missing,1),
        ('completion_short_by_one',77594624+missing-1,0),
    ]:
        d = mod.Downloader.__new__(mod.Downloader)
        d.c = dict(config,body_budget_bytes=budget)
        d.stop_requested = False; d.last_error = None; d.journal = NullJournal()
        d._verify_candidate = lambda:None
        d.state = lambda:state
        d.prefix = Path(config['prefix']); d.candidate = candidate
        d.work = OUT/'logs'/name; d.work.mkdir()
        calls = []
        def intercept(start,end):
            calls.append([start,end]); return False
        d._request = intercept
        with mock.patch.object(mod.http.client,'HTTPSConnection',side_effect=AssertionError('NETWORK_FORBIDDEN')) as network:
            result = d.run()
            assert network.call_count == 0
        assert len(calls) == expected_calls
        if expected_calls:
            assert calls == [[94875356,95923931]]
        else:
            assert 'INSUFFICIENT_COMPLETION_BUDGET' in result['error']
        checks.append({'case':name,'passed':True,'intercepted_request_calls':calls,'network_calls':0})

    d = mod.Downloader.__new__(mod.Downloader)
    d.c = dict(config,body_budget_bytes=77594624+1048576-1)
    d.state = lambda:state
    with mock.patch.object(mod.http.client,'HTTPSConnection',side_effect=AssertionError('NETWORK_FORBIDDEN')) as network:
        try:
            d._request(94875356,95923931)
        except mod.GuardError as e:
            assert str(e) == 'BODY_BUDGET'
        else:
            raise AssertionError('budget guard did not reject')
        assert network.call_count == 0
    checks.append({'case':'single_request_short_by_one','passed':True,'network_calls':0})
    oldtests=json.loads((ROOT/'D3_DOWNLOADER_OFFLINE_2026-10-23/results/LOOPBACK_REQUEST_LOG_run3.json').read_text())
    fallback=[x for x in oldtests if x.get('mode')=='ignore_range']
    report={
        'timestamp':datetime.datetime.now().astimezone().isoformat(),
        'decision':'HOLD_PREFLIGHT_RECEIVE_BOUND_UNPROVEN',
        'journal_hash_chain_passed':True,'journal_events':len(events),
        'journal_sha256':sha(OLD/'journal.jsonl'),
        'committed_chunks_verified':len(state['committed']),
        'prefix_bytes':offset,'prefix_sha256':sha(candidate),
        'original_prefix_bytes':config['prefix_bytes'],
        'original_prefix_sha256':sha(Path(config['prefix'])),
        'previous_observed_body_bytes':state['observed_body_bytes'],
        'previous_conservative_charge':state['charged_upper_bytes'],
        'previous_failed_request_reserved':1048576,
        'previous_failed_request_observed':507612,
        'previous_failed_request_uncertainty':540964,
        'missing_file_bytes':missing,'budget_remaining':remaining,'margin_bytes':remaining-missing,
        'original_resume_body_cap':342115318,'combined_historical_upper':435500022,'combined_authorized_cap':700020716,
        'new_media_requests':0,'new_media_body_bytes':0,'new_request_reservations':0,
        'server_identity_revalidated_live':False,
        'last_recorded_etag':config['etag'],'last_valid_response_utc':'2026-10-23T07:17:33Z',
        'timeout_seconds':config['timeout_seconds'],
        'last_commit_utc':'2026-10-23T07:17:51Z','timeout_utc':'2026-10-23T07:18:21Z',
        'timeout_root_cause':'Unknown; consistent with 30-second blocking read timeout, not a total-request deadline.',
        'guard_checks':checks,'guard_check_limit':'Arithmetic/control flow only; no live connection, actual server response, or receive-prefetch bound tested.',
        'existing_ignore_range_fixture':fallback,
        'fallback_fixture_limit':'Server write is not client receive. Existing test does not measure actual client prefetch or prove its upper bound.',
        'strict_receive_budget_proved':False,
        'decode_executed':False,'pts_verified':False,'frames_created':0,
        'evidence_judgments':{k:'无法判断' for k in 'ABCDE'},
    }
    with (OUT/'PREFLIGHT_RESULT.json').open('x') as f:
        json.dump(report,f,ensure_ascii=False,indent=2); f.write('\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
