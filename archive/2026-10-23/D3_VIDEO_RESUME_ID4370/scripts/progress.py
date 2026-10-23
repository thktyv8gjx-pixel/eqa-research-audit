"""Read-only transfer progress; it cannot initiate media requests."""
from pathlib import Path
import json

w = Path(__file__).resolve().parent.parent
raw = (w / 'journal.jsonl').read_bytes()
lines = raw.splitlines()
if raw and not raw.endswith(b'\n'):
    lines.pop()  # A concurrent append may be in progress; never repair the file.
events = [json.loads(x) for x in lines]
received = sum(x['bytes'] for x in events if x['kind'] == 'BODY')
ends = [x for x in events if x['kind'] == 'END']
print(json.dumps({
    'received_bytes': received,
    'percent_of_missing': round(100 * received / 340018166, 2),
    'completed_ranges': sum(x['exact'] for x in ends),
    'failed_ranges': sum(not x['exact'] for x in ends),
    'last_kind': events[-1]['kind'], 'last_utc': events[-1]['utc'],
    'candidate_bytes': (w/'candidate.mp4.partial').stat().st_size,
    'results': [json.loads(p.read_text()) for p in w.glob('result_*.json')],
}))
