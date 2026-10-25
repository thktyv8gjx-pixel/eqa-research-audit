"""Offline verification and descriptive controls; does not make inference calls."""
import collections
import json
from pathlib import Path

from run_ollama import DIGEST, OPTIONS, official_functions

ROOT = Path(__file__).resolve().parents[1]


def main():
    f = official_functions()
    all_examples = json.loads((ROOT/'private/multihop_test_4500.json').read_text())
    examples = {r['id']: r for r in all_examples}
    rows = [r for phase in ('first12', 'extra60') for r in map(json.loads,
            (ROOT/'ollama_run'/f'{phase}_predictions.jsonl').read_text().splitlines())]
    expected = [r['id'] for r in json.loads((ROOT/'selection.json').read_text())['samples']]
    expected += [r['id'] for r in json.loads((ROOT/'ollama_run/extra60_selection.json').read_text())['samples']]
    assert [r['id'] for r in rows] == expected and len(set(expected)) == 72
    assert len({examples[i]['image_path'].split('_')[0] for i in expected}) == 72
    c25 = cib = 0
    for r in rows:
        e = examples[r['id']]
        request = json.loads((ROOT/'private/ollama_run/requests'/f"{r['id']}.json").read_text())
        response = json.loads((ROOT/'private/ollama_run/responses'/f"{r['id']}.json").read_text())
        assert r['attempt'] == 1 and request['options'] == OPTIONS and request['digest'] == DIGEST
        assert request['prompt'] == f['build_prompt'](e['question_tag'])
        assert 'answer' not in request and 'bbox' not in request
        assert request['image_sha256'] == r['image_sha256']
        assert r['raw_response'] == response['message']['content'] and response['done']
        pred, box = f['parse_response'](r['raw_response'])
        assert pred == r['prediction'] and box == r['pred_bbox']
        w, h = map(int, e['image_resolution'].split('x'))
        iou = f['calculate_iou'](e['bbox'], box, w, h)
        assert iou == r['iou'] and f['compute_score'](pred, e['answer']) == r['mcq_correct']
        if r['mcq_correct']:
            c25 += iou is not None and iou >= .25
            if box:
                x, y, bw, bh = e['bbox']
                cx, cy = (box[0]+box[2])/2*w, (box[1]+box[3])/2*h
                cib += x <= cx <= x+bw and y <= cy <= y+bh
    log = (ROOT/'private/ollama_run/server.log').read_text(errors='replace')
    chats = sum('POST' in line and '/api/chat' in line for line in log.splitlines())
    assert chats == 72
    def labels(items):
        return dict(collections.Counter(f['extract_choice_letter'](r['answer']) for r in items))
    sample_labels = labels([examples[r['id']] for r in rows])
    result = dict(checked_items=72, chat_requests=chats, attempts_per_item=1,
                  all_outputs_preserved=True, same_options_all_items=True,
                  no_gt_fields_in_model_requests=True, official_rescoring_matches=True,
                  distinct_image_video_filename_groups=72, physical_scene_independence_established=False,
                  acc_at_025iou=dict(correct=c25,total=72),
                  acc_center_in_box=dict(correct=cib,total=72),
                  predicted_letter_counts=dict(collections.Counter(f['extract_choice_letter'](r['prediction']) for r in rows)),
                  sample_gt_letter_counts=sample_labels, full_test_gt_letter_counts=labels(all_examples),
                  full_test_gt_letter_counts_by_stratum={h+'_'+v:labels([r for r in all_examples if (r['hop'],r['view'])==(h,v)])
                                                       for h in ('1hop','2hop','3hop') for v in ('ego','exo')},
                  always_a_descriptive_correct=sample_labels['a'],
                  always_a_caveat='Post-hoc descriptive label-prior control, no bbox and no grounding score; not a proof of model position bias.',
                  model_vs_authors='Quantized base model with Ollama, not author post-training or full benchmark reproduction.')
    (ROOT/'ollama_run/verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('VERIFIED',len(rows),'items;',chats,'generation requests; no retries')


if __name__ == '__main__':
    main()
