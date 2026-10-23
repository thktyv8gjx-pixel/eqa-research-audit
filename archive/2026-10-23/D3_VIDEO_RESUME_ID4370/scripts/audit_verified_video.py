"""Local-only timing/decode audit; no network, installations, or model calls."""
from pathlib import Path
from fractions import Fraction
import csv
import hashlib
import json
import subprocess
import sys

OUT = Path(__file__).resolve().parent.parent
ROOT = OUT.parent
VIDEO = OUT / 'candidate.mp4.partial'
NATIVE = ROOT / 'D3_VIDEO_VERIFICATION_2026-10-23_ID4370/tmp/av_audit'


def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with path.open('rb') as f:
        while block := f.read(1048576):
            h.update(block)
    return h.hexdigest()


def main():
    results = sorted(OUT.glob('result_*.json'))
    if not results:
        raise SystemExit('REFUSED: completed transfer result is absent')
    result = json.loads(results[-1].read_text())
    if result['status'] != 'VERIFIED':
        raise SystemExit('REFUSED: full-size/MD5 transfer gate has not passed')
    if VIDEO.stat().st_size != 357839862:
        raise SystemExit('REFUSED: full size differs')
    if digest(VIDEO, 'md5') != 'c981eab775c96858da313acef769b014':
        raise SystemExit('REFUSED: full MD5 differs')
    if digest(NATIVE) != 'fb40c5adbcdb93088b790811d4513a21184150cfad8faba66cbacccc28dae714':
        raise SystemExit('REFUSED: existing native audit executable differs')
    logs = OUT / 'logs'
    with (logs / 'MP4_PARSER_RUN.log').open('x') as f:
        subprocess.run([sys.executable, '-B', str(OUT/'scripts/mp4_timing.py')],
                       check=True, stdout=f, stderr=subprocess.STDOUT)
    with (logs / 'AV_METADATA_RUN.log').open('x') as f:
        subprocess.run([str(NATIVE), 'metadata', str(VIDEO), str(logs/'AV_METADATA')],
                       check=True, stdout=f, stderr=subprocess.STDOUT)
    with (logs/'MP4_SAMPLE_TIMELINE.csv').open() as f:
        raw = list(csv.DictReader(f))
    with (logs/'AV_METADATA.csv').open() as f:
        native = list(csv.DictReader(f))
    raw_pts = [Fraction(int(r['movie_pts_numerator']), int(r['movie_pts_denominator'])) for r in raw]
    native_pts = [Fraction(int(r['pts_value']), int(r['pts_scale'])) for r in native]
    report = {
        'container_sample_count': len(raw), 'native_sample_count': len(native),
        'pts_exact_in_sample_order': raw_pts == native_pts,
        'pts_exact_as_multiset': sorted(raw_pts) == sorted(native_pts),
        'container_first_pts': float(min(raw_pts)),
        'native_first_pts': float(min(native_pts)),
        'container_last_pts': float(max(raw_pts)),
        'native_last_pts': float(max(native_pts)),
        'comparison': 'Exact rational movie presentation timestamps, after parsing edit list; no frame-index/fps substitution',
    }
    with (logs/'PTS_CROSSCHECK.json').open('x') as f:
        json.dump(report, f, indent=2); f.write('\n')
    if not report['pts_exact_as_multiset']:
        raise SystemExit('HOLD: independent PTS reconstructions disagree; no pixel decode')
    metadata = json.loads((logs/'AV_METADATA.json').read_text())
    if metadata['reader_status'] != 2 or metadata['reader_error'] is not None:
        raise SystemExit('HOLD: compressed sample reader incomplete')
    with (logs/'AV_DECODE_RUN.log').open('x') as f:
        subprocess.run([str(NATIVE), 'decode_prefix', str(VIDEO), str(logs/'AV_DECODE_PREFIX.json')],
                       check=True, stdout=f, stderr=subprocess.STDOUT)
    print(json.dumps(report, indent=2))
    print((logs/'AV_DECODE_PREFIX.json').read_text())


if __name__ == '__main__':
    main()
