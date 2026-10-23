#!/usr/bin/env python3
"""Reproduce the fixed selection and audit NOT_RUN records; no model/network code.

--commands prints standard curl calls to the official HF metadata/rows API.
Those commands were not a successful acquisition in this run. Image payloads,
answers and a verified runtime are still prerequisites for actual inference.
"""
import argparse
import hashlib
import json
import shlex
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent


def selected_rows(manifest):
    return sorted(range(manifest['expected_population_rows']), key=lambda i:
        hashlib.sha256(f"{manifest['seed']}|{i}".encode()).hexdigest())[:12]


def row_url(manifest, index):
    return 'https://datasets-server.huggingface.co/rows?' + urlencode({
        'dataset': manifest['dataset'], 'config': manifest['config'],
        'split': manifest['split'], 'offset': index, 'length': 1})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commands', action='store_true')
    args = parser.parse_args()
    m = json.loads((ROOT / 'sample_manifest.json').read_text())
    selected = selected_rows(m)
    assert selected == m['selected_row_indices']
    assert len(set(selected)) == 12
    if args.commands:
        print('# Command listing only: do not pipe this output to a shell.')
        print('# First confirm live dataset revision equals the expected revision; otherwise stop.')
        print('# The rows API does not constitute proof of a pinned revision. Preserve headers/raw JSON.')
        print('# Use only these rows; no full parquet or replacement rows. Images require a later bounded acquisition.')
        requests = [('dataset_revision', 'https://huggingface.co/api/datasets/' + m['dataset'])]
        requests += [(f'row_{i}', row_url(m, i)) for i in selected]
        for name, url in requests:
            command = ['curl', '--fail', '--location', '--connect-timeout', '8',
                       '--max-time', '20', '--max-filesize', '1048576',
                       '--dump-header', str(ROOT / 'private' / (name + '.headers')),
                       '--output', str(ROOT / 'private' / (name + '.json')), url]
            print(shlex.join(command))
        return
    rows = [json.loads(line) for line in (ROOT / 'results.jsonl').read_text().splitlines()]
    assert [r['row_index'] for r in rows] == selected
    for row in rows:
        assert row['raw_input'] is None and row['raw_output'] is None
        assert row['answer'] is None and row['prediction'] is None
        assert row['status'] == 'NOT_RUN'
        assert row['correct'] is None
        assert row['error_category'] == 'UNASSESSABLE_NO_INPUT_OR_PREDICTION'
        assert row['request_url'] == row_url(m, row['row_index'])
    print(json.dumps({'selection_records_verified': len(rows),
        'real_sample_payloads_acquired': 0, 'predictions_run': 0,
        'model_accuracy': None, 'study_status': 'HOLD_RESOURCES'}, indent=2))


if __name__ == '__main__':
    main()
