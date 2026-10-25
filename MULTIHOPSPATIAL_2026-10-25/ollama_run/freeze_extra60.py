"""Freeze 10 additional items per hop/view stratum without reading predictions."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = 'MultihopSpatial-20261025-extra60-v1'


def group(row):
    return row['image_path'].split('_')[0]


def main():
    source = (ROOT / 'private/multihop_test_4500.json').read_bytes()
    assert hashlib.sha256(source).hexdigest() == '26e20426052b49d97f8122c31deb1399d349a7e679e92632e951afd78dc8e32a'
    first = json.loads((ROOT / 'selection.json').read_text())['samples']
    used_ids, used_groups = {r['id'] for r in first}, {group(r) for r in first}
    rows = json.loads(source)
    selected = []
    for hop in ('1hop', '2hop', '3hop'):
        for view in ('ego', 'exo'):
            candidates = sorted((r for r in rows if (r['hop'], r['view']) == (hop, view)),
                                key=lambda r: hashlib.sha256(f"{KEY}:{r['id']}".encode()).hexdigest())
            count = 0
            for row in candidates:
                if row['id'] in used_ids or group(row) in used_groups:
                    continue
                selected.append(row)
                used_ids.add(row['id'])
                used_groups.add(group(row))
                count += 1
                if count == 10:
                    break
            assert count == 10
    assert len(selected) == 60
    manifest = dict(selection_key=KEY, frozen_utc=datetime.now(timezone.utc).isoformat(),
                    rule='Lowest SHA256(key:id) per hop/view; exclude all first12 and already selected image/video groups; no prediction/answer filtering.',
                    dataset_revision='6c962f5227acc133d2196cbf89f09441c7ccb703',
                    physical_scene_independence_established=False,
                    samples=[{k: r[k] for k in ('id', 'image_path', 'hop', 'view', 'image_resolution')}
                             for r in selected])
    with (ROOT / 'ollama_run/extra60_selection.json').open('x') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')
    with (ROOT / 'private/ollama_run/extra60.jsonl').open('x') as f:
        for row in selected:
            f.write(json.dumps(row, ensure_ascii=False)+'\n')
    print('FROZEN', [r['id'] for r in selected])


if __name__ == '__main__':
    main()
