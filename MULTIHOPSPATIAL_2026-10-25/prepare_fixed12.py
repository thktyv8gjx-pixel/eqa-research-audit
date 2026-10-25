"""Offline, answer-independent selection; no inference or network requests."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'private/multihop_test_4500.json'
EXPECTED_SHA256 = '26e20426052b49d97f8122c31deb1399d349a7e679e92632e951afd78dc8e32a'
SELECTION_KEY = 'MultihopSpatial-20261025-v1'

def group_key(row):
    # COCO image ID is an image group, not a verified independent physical scene.
    name = row['image_path']
    return name.split('_')[0] if '_' in name else name

def main():
    data = SOURCE.read_bytes()
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256
    rows = json.loads(data)
    assert len(rows) == 4500
    selected, used = [], set()
    for hop in ('1hop', '2hop', '3hop'):
        for view in ('ego', 'exo'):
            candidates = sorted(
                (r for r in rows if (r['hop'], r['view']) == (hop, view)),
                key=lambda r: hashlib.sha256(f"{SELECTION_KEY}:{r['id']}".encode()).hexdigest(),
            )
            count = 0
            for row in candidates:
                group = group_key(row)
                if group in used:
                    continue
                selected.append(row)
                used.add(group)
                count += 1
                if count == 2:
                    break
            assert count == 2
    manifest = {
        'source_code_commit': 'b1b6a7be261e3cde814e117eabe330d5ef47c1f0',
        'dataset_revision': '6c962f5227acc133d2196cbf89f09441c7ccb703',
        'test_json_bytes': len(data), 'test_json_sha256': EXPECTED_SHA256,
        'selection_key': SELECTION_KEY,
        'rule': 'Two lowest SHA256(key:id) per hop/view stratum, excluding used image/video filename groups; no answer or model-output filtering.',
        'independence_limit': 'COCO image IDs are distinct; physical scene independence is not annotated or established.',
        'samples': [dict(id=r['id'], image_path=r['image_path'], group=group_key(r),
                         hop=r['hop'], view=r['view'], image_resolution=r['image_resolution'],
                         tags=[t for t in ('ATT', 'POS', 'REL') if '<'+t+'>' in r['question_tag']])
                    for r in selected],
    }
    outputs = {
        ROOT / 'selection.json': json.dumps(manifest, ensure_ascii=False, indent=2)+'\n',
        ROOT / 'private/fixed12.jsonl': ''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in selected),
    }
    for path, content in outputs.items():
        if path.exists() and path.read_text() != content:
            raise RuntimeError(f'Refusing to replace different frozen selection: {path}')
    for path, content in outputs.items():
        if not path.exists():
            path.write_text(content)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
