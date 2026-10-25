"""Score every attempted fixed item; never discard invalid model outputs."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def metrics(rows):
    n = len(rows)
    correct = sum(r['mcq_correct'] for r in rows)
    joint = sum(r['joint_correct'] for r in rows)
    parsed = sum(r['mcq_parse_valid'] for r in rows)
    valid = sum(r['output_valid'] for r in rows)
    conditional = [r['iou'] or 0.0 for r in rows if r['mcq_correct']]
    return dict(n=n, mcq_correct=correct, mcq_accuracy=correct/n if n else None,
                mcq_parse_valid=parsed, mcq_parse_rate=parsed/n if n else None,
                full_output_valid=valid, full_output_valid_rate=valid/n if n else None,
                joint_correct=joint, acc_at_05iou=joint/n if n else None,
                official_parsed_denominator=parsed,
                official_mcq_accuracy=correct/parsed if parsed else None,
                official_acc_at_05iou=joint/parsed if parsed else None,
                mean_iou_mcq_correct=sum(conditional)/len(conditional) if conditional else None,
                runtime_errors=sum(r['outcome']=='runtime_error' for r in rows),
                wall_seconds=sum(r['wall_seconds'] for r in rows),
                outcomes=dict(Counter(r['outcome'] for r in rows)),
                truncated=sum(r.get('done_reason')=='length' for r in rows))


def main():
    rows = []
    expected = []
    for phase, selection in [('first12', ROOT.parent/'selection.json'),
                             ('extra60', ROOT/'extra60_selection.json')]:
        if not selection.exists():
            continue
        expected += [r['id'] for r in json.loads(selection.read_text())['samples']]
        p = ROOT / (phase + '_predictions.jsonl')
        if p.exists():
            rows += [json.loads(line) for line in p.read_text().splitlines()]
    assert len({r['id'] for r in rows}) == len(rows)
    assert {r['id'] for r in rows} <= set(expected)
    result = dict(denominator='All attempted fixed samples, including runtime/parse/bbox failures',
                  generations_per_item=1, configured_items=len(expected), attempted=len(rows),
                  unattempted_ids=[i for i in expected if i not in {r['id'] for r in rows}],
                  overall=metrics(rows),
                  phases={p:metrics([r for r in rows if r['phase']==p])
                          for p in sorted({r['phase'] for r in rows})},
                  strata={h+'_'+v:metrics([r for r in rows if (r['hop'],r['view'])==(h,v)])
                          for h in ('1hop','2hop','3hop') for v in ('ego','exo')})
    (ROOT/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
