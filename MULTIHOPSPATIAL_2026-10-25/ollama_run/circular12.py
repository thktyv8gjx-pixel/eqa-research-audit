"""Fixed-12 circular-choice diagnostic. No downloads, retries or baseline regeneration."""
import argparse
import base64
import csv
import hashlib
import itertools
import json
import re
import time
import urllib.error
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from run_ollama import ROOT, MODEL, DIGEST, OPTIONS, api, official_functions

IDS = [706, 403, 1193, 764, 1696, 1837, 2480, 2748, 3028, 3084, 4208, 4153]
LETTERS = 'abcd'
PUBLIC = ROOT / 'ollama_run/circular12'
PRIVATE = ROOT / 'private/ollama_run/circular12'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write('\n')


def split_choices(question):
    if question.count('<choice>') != 1 or question.count('</choice>') != 1:
        raise ValueError('Not exactly one explicit choice block')
    prefix, body, suffix = re.fullmatch(r'(.*?<choice>)(.*?)(</choice>.*)', question, re.S).groups()
    stem = prefix[:-len('<choice>')] + suffix[len('</choice>'):]
    references = r'\([a-d]\)|\b(?:option|choice|answer)\s+[a-d]\b|\b(?:former|latter)\b'
    if re.search(references, stem, re.I):
        raise ValueError('Question has a possible option-letter/order reference')
    labels = list(re.finditer(r'\(([a-d])\)', body))
    if [m.group(1) for m in labels] != list(LETTERS) or labels[0].start() != 0:
        raise ValueError('Choice labels do not have unique, ordered a/b/c/d boundaries')
    options = []
    for index, match in enumerate(labels):
        text = body[match.end():labels[index+1].start() if index < 3 else len(body)]
        if index < 3:
            if not text.endswith(', '):
                raise ValueError('Unexpected option separator')
            text = text[:-2]
        if not text.startswith(' ') or not text[1:] or text[1:] != text[1:].strip():
            raise ValueError('Ambiguous option whitespace/content')
        options.append(text[1:])
    if len(set(options)) != 4 or re.search(r'\b(?:all|none) of (?:the )?(?:above|others?)\b', body, re.I):
        raise ValueError('Duplicate or order-dependent options')
    assert ', '.join(f'({letter}) {text}' for letter, text in zip(LETTERS, options)) == body
    return prefix, options, suffix


def rotated(question, shift):
    prefix, options, suffix = split_choices(question)
    new_to_old = {letter: LETTERS[(index-shift) % 4] for index, letter in enumerate(LETTERS)}
    old_to_new = {old: new for new, old in new_to_old.items()}
    contents = [options[LETTERS.index(new_to_old[letter])] for letter in LETTERS]
    result = prefix + ', '.join(f'({letter}) {text}' for letter, text in zip(LETTERS, contents)) + suffix
    assert Counter(contents) == Counter(options)
    assert all(new_to_old[old_to_new[old]] == old for old in LETTERS)
    return result, options, contents, new_to_old, old_to_new


def normal_text(value):
    return re.sub(r'\s+', ' ', value).strip().rstrip('.').casefold()


def score(meta, raw, thinking, row, f):
    prediction = f['parse_mcq_answer'](raw)
    letter = f['extract_choice_letter'](prediction)
    mapped = meta['new_to_original'].get(letter)
    bbox, parse_error = None, None
    try:
        _, bbox = f['parse_response'](raw)
    except (ValueError, TypeError) as exc:
        parse_error = f'{type(exc).__name__}: {exc}'
    description = re.sub(r'^\([a-d]\)\s*', '', prediction, count=1, flags=re.I) if prediction else None
    matching = [LETTERS[i] for i, text in enumerate(meta['original_options'])
                if description is not None and normal_text(description) == normal_text(text)]
    description_id = matching[0] if len(matching) == 1 else None
    gt_original = f['extract_choice_letter'](row['answer'])
    gt_new = meta['original_to_new'][gt_original]
    width, height = map(int, row['image_resolution'].split('x'))
    iou = f['calculate_iou'](row['bbox'], bbox, width, height)
    correct = mapped is not None and mapped == gt_original
    assert correct == (letter is not None and letter == gt_new)
    return dict(id=row['id'], hop=row['hop'], view=row['view'], shift=meta['shift'],
                new_to_original=meta['new_to_original'], original_to_new=meta['original_to_new'],
                image_sha256=meta['image_sha256'], prompt_sha256=meta['prompt_sha256'],
                raw_response=raw, thinking=thinking, prediction=prediction,
                predicted_letter=letter, mapped_original_id=mapped,
                raw_object_description=description, description_literal_original_id=description_id,
                description_mapping_status=('unmatched' if description_id is None else
                                            'consistent' if mapped == description_id else 'CONFLICT'),
                gt_original_id=gt_original, gt_new_letter=gt_new, pred_bbox=bbox, iou=iou,
                mcq_correct=correct, joint_correct=bool(correct and iou is not None and iou >= .5),
                mcq_parse_valid=mapped is not None, bbox_valid=f['is_valid_bbox'](bbox),
                output_valid=f['is_valid_prediction'](prediction, bbox),
                parse_error=parse_error, error=None)


def history_paths():
    paths = [ROOT/'selection.json', ROOT/'private/fixed12.jsonl', ROOT/'private/benchmark_qwen.py']
    paths += [ROOT/'ollama_run'/n for n in ('run_ollama.py', 'environment.json',
              'first12_predictions.jsonl', 'extra60_predictions.jsonl')]
    paths += [ROOT/'private/ollama_run/requests'/f'{ident}.json' for ident in IDS]
    return paths


def chat_count():
    text = (ROOT/'private/ollama_run/server.log').read_text(errors='replace')
    return sum('POST' in line and '/api/chat' in line for line in text.splitlines())


def prepare(f):
    selection = json.loads((ROOT/'selection.json').read_text())
    rows = [json.loads(line) for line in (ROOT/'private/fixed12.jsonl').read_text().splitlines()]
    assert [r['id'] for r in rows] == IDS == [r['id'] for r in selection['samples']]
    old = [json.loads(line) for line in (ROOT/'ollama_run/first12_predictions.jsonl').read_text().splitlines()]
    assert [r['id'] for r in old] == IDS
    environment = json.loads((ROOT/'ollama_run/environment.json').read_text())
    assert environment['model'] == MODEL and environment['options'] == OPTIONS
    assert environment['digest'].removeprefix('sha256:') == DIGEST.removeprefix('sha256:')
    before = {str(p.relative_to(ROOT)):sha(p) for p in history_paths()}
    conditions, excluded, reused, checks = {}, [], [], []
    for row, legacy in zip(rows, old):
        ident = row['id']
        try:
            prompt0 = f['build_prompt'](rotated(row['question_tag'], 0)[0])
        except (ValueError, AttributeError) as exc:
            excluded.append(dict(id=ident, reason=str(exc)))
            continue
        old_request = json.loads((ROOT/'private/ollama_run/requests'/f'{ident}.json').read_text())
        image_path = ROOT/'private/images'/row['image_path']
        image_hash = sha(image_path)
        assert prompt0 == old_request['prompt'], f'Old prompt mismatch: {ident}'
        assert image_hash == old_request['image_sha256'] == legacy['image_sha256']
        assert Path(old_request['image_path']).resolve() == image_path.resolve()
        assert old_request['options'] == OPTIONS and old_request['model'] == MODEL
        assert old_request['digest'].removeprefix('sha256:') == DIGEST.removeprefix('sha256:')
        assert old_request['stream'] is False and old_request['keep_alive'] == '20m'
        old_response = json.loads((ROOT/'private/ollama_run/responses'/f'{ident}.json').read_text())
        assert old_response['message']['content'] == legacy['raw_response']
        assert f['parse_response'](legacy['raw_response']) == (legacy['prediction'], legacy['pred_bbox'])
        for shift in range(4):
            question, options, contents, forward, backward = rotated(row['question_tag'], shift)
            prompt = f['build_prompt'](question)
            assert prompt.split('<choice>')[0] == prompt0.split('<choice>')[0]
            assert prompt.split('</choice>')[1] == prompt0.split('</choice>')[1]
            conditions[ident, shift] = dict(id=ident, hop=row['hop'], view=row['view'], shift=shift,
                original_options=options, rotated_options=contents, new_to_original=forward,
                original_to_new=backward, image_sha256=image_hash,
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                payload=dict(model=MODEL, messages=[dict(role='user', content=prompt,
                    images=[base64.b64encode(image_path.read_bytes()).decode()])],
                    stream=False, options=dict(OPTIONS), keep_alive='20m'))
        record = score(conditions[ident, 0], legacy['raw_response'], legacy.get('thinking'), row, f)
        assert record['mcq_correct'] == legacy['mcq_correct'] and record['iou'] == legacy['iou']
        record.update(source='reused_shift0', additional_generations=0, wall_seconds=0.0,
                      original_wall_seconds=legacy['wall_seconds'], attempt=1,
                      done_reason=legacy['done_reason'], duration_fields=legacy['duration_fields'])
        reused.append(record)
        checks.append(dict(id=ident, option_boundaries_valid=True, question_letter_references=False,
                           shift0_prompt_byte_identical=True, image_sha256=image_hash,
                           historical_request_sha256=sha(ROOT/'private/ollama_run/requests'/f'{ident}.json')))
    version = api('/api/version')
    assert version == environment['runtime'], version
    installed = next(r for r in api('/api/tags')['models'] if r['name'] == MODEL)
    assert installed['digest'].removeprefix('sha256:') == DIGEST.removeprefix('sha256:')
    if PUBLIC.exists() or PRIVATE.exists():
        raise RuntimeError('Refusing to overwrite or repeat a circular experiment')
    PUBLIC.mkdir()
    (PRIVATE/'requests').mkdir(parents=True)
    (PRIVATE/'responses').mkdir()
    for (ident, shift), meta in conditions.items():
        save(PRIVATE/'requests'/f'{ident}_s{shift}.json', meta)
        if shift == 0:
            source = ROOT/'private/ollama_run/responses'/f'{ident}.json'
            save(PRIVATE/'responses'/f'{ident}_s0.json', json.loads(source.read_text()))
    # Balance 1/2/3 execution positions across questions, fixed before new outputs.
    order = []
    for index, ident in enumerate(IDS):
        for offset in range(3):
            shift = 1 + (index+offset) % 3
            if (ident, shift) in conditions:
                order.append(dict(id=ident, shift=shift))
    manifest = dict(model=MODEL, digest=DIGEST, options=OPTIONS, runtime=version,
                    created_utc=datetime.now(timezone.utc).isoformat(), ids=IDS,
                    expected_new_generations=len(order), checks=checks, excluded=excluded,
                    execution_order=order, historical_sha256=before, initial_chat_requests=chat_count(),
                    change_definition='Adjacent mapped-ID transitions along shifts 0->1->2->3; not temporal order; no closing 3->0 edge.',
                    bbox_stability_definition='Pairwise predicted-box IoU; report continuous values and >=0.5 diagnostic threshold.',
                    decision_rule='INCONCLUSIVE if incomplete/invalid/conflicting; STABLE if all paired semantic IDs and boxes stable; SENSITIVE if every paired item changes semantic ID; MIXED otherwise.',
                    restriction='No GT answer or bbox in payload; shift0 reused, no identical-input repeats.')
    save(PUBLIC/'manifest.json', manifest)
    print('PREFLIGHT',len(checks),'exact reusable baselines;',len(order),'new conditions;',len(excluded),'excluded',flush=True)
    return rows, conditions, reused, manifest


def aggregate(rows):
    n = len(rows)
    return dict(n_conditions=n, mcq_correct=sum(r['mcq_correct'] for r in rows),
                joint_correct=sum(r['joint_correct'] for r in rows),
                mcq_accuracy=sum(r['mcq_correct'] for r in rows)/n if n else None,
                acc_at_05iou=sum(r['joint_correct'] for r in rows)/n if n else None,
                answer_parse_failures=sum(not r['mcq_parse_valid'] for r in rows),
                invalid_full_outputs=sum(not r['output_valid'] for r in rows),
                mean_gt_iou=sum(r['iou'] or 0 for r in rows)/n if n else None,
                mean_gt_iou_denominator='All conditions; missing boxes contribute zero',
                predicted_letter_counts={c:sum(r['predicted_letter']==c for r in rows) for c in LETTERS})


def analyze(f):
    manifest = json.loads((PUBLIC/'manifest.json').read_text())
    results = [json.loads(line) for line in (PUBLIC/'predictions.jsonl').read_text().splitlines()]
    keyed = {(r['id'],r['shift']):r for r in results}
    assert len(keyed) == len(results)
    paired, comparisons = [], []
    for ident in IDS:
        group = [keyed.get((ident,s)) for s in range(4)]
        if any(r is None for r in group):
            paired.append(dict(id=ident, category='incomplete_or_excluded'))
            continue
        original = [r['mapped_original_id'] for r in group]
        letters = [r['predicted_letter'] for r in group]
        reliable = all(r['mcq_parse_valid'] and r['description_mapping_status']!='CONFLICT' for r in group)
        changes = sum(a!=b for a,b in zip(original,original[1:])) if reliable else None
        box_pairs = []
        for a,b in itertools.combinations(group,2):
            if a['mapped_original_id'] is not None and a['mapped_original_id']==b['mapped_original_id']:
                iou = f['calculate_iou_xyxy'](a['pred_bbox'],b['pred_bbox']) if a['bbox_valid'] and b['bbox_valid'] else None
                box_pairs.append(dict(shift_a=a['shift'],shift_b=b['shift'],original_id=a['mapped_original_id'],bbox_pair_iou=iou,
                                      exact_coordinates=a['pred_bbox']==b['pred_bbox']))
        category = ('invalid_or_conflicting' if not reliable else 'all_same' if changes==0
                    else 'one_adjacent_change' if changes==1 else 'multiple_adjacent_changes')
        counts = sorted(Counter(original).values(),reverse=True)
        paired.append(dict(id=ident, letters=letters, mapped_original_ids=original,
                           description_literal_ids=[r['description_literal_original_id'] for r in group],
                           category=category, adjacent_changes=changes,
                           one_condition_outlier=reliable and counts==[3,1],
                           changed_from_shift0=sum(v!=original[0] for v in original[1:]) if reliable else None,
                           letter_stable=all(letters) and len(set(letters))==1,
                           semantic_stable=reliable and len(set(original))==1,
                           mcq_by_shift=[r['mcq_correct'] for r in group],joint_by_shift=[r['joint_correct'] for r in group],
                           gt_iou_by_shift=[r['iou'] for r in group],same_semantic_box_pairs=box_pairs,
                           all_same_semantic_boxes_iou_ge_05=bool(box_pairs) and all(p['bbox_pair_iou'] is not None and p['bbox_pair_iou']>=.5 for p in box_pairs)))
        for r in group[1:]:
            comparisons.append(dict(id=ident,shift=r['shift'],semantic_changed=r['mapped_original_id']!=original[0],
                                    letter_changed=r['predicted_letter']!=letters[0],
                                    mcq_0=group[0]['mcq_correct'],mcq_shift=r['mcq_correct'],
                                    joint_0=group[0]['joint_correct'],joint_shift=r['joint_correct'],
                                    gt_iou_delta=(r['iou'] or 0)-(group[0]['iou'] or 0),
                                    bbox_vs_shift0_iou=f['calculate_iou_xyxy'](r['pred_bbox'],group[0]['pred_bbox'])))
    complete = [p for p in paired if 'semantic_stable' in p]
    semantic_stable = sum(p['semantic_stable'] for p in complete)
    letter_stable = sum(p['letter_stable'] for p in complete)
    invalid = any(p.get('category') in ('incomplete_or_excluded','invalid_or_conflicting') for p in paired)
    if invalid or len(results)!=48 or any(not r['output_valid'] for r in results): decision='INCONCLUSIVE'
    elif semantic_stable==12 and all(p['all_same_semantic_boxes_iou_ge_05'] for p in complete): decision='POSITION_STABLE'
    elif semantic_stable==0: decision='POSITION_SENSITIVE'
    else: decision='MIXED'
    transition_summary = {}
    for shift in (1,2,3):
        c=[r for r in comparisons if r['shift']==shift]
        transition_summary[str(shift)] = dict(n_pairs=len(c),semantic_changes=sum(r['semantic_changed'] for r in c),
          mcq_gained=sum(not r['mcq_0'] and r['mcq_shift'] for r in c),mcq_lost=sum(r['mcq_0'] and not r['mcq_shift'] for r in c),
          joint_gained=sum(not r['joint_0'] and r['joint_shift'] for r in c),joint_lost=sum(r['joint_0'] and not r['joint_shift'] for r in c))
    summary=dict(decision=decision,n_independent_question_units=12,n_conditions=len(results),
      completed_new_generations=sum(r['source']=='new_generation' for r in results),
      reused_shift0=sum(r['source']=='reused_shift0' for r in results),excluded=manifest['excluded'],
      letter_stable_items=letter_stable,letter_stable_rate=letter_stable/12,
      semantic_stable_items=semantic_stable,semantic_stable_rate=semantic_stable/12,
      categories=dict(Counter(p['category'] for p in paired)),
      description_conflicts=sum(r['description_mapping_status']=='CONFLICT' for r in results),
      unmatched_descriptions=sum(r['description_mapping_status']=='unmatched' for r in results),
      new_wall_seconds=sum(r['wall_seconds'] for r in results if r['source']=='new_generation'),
      overall_condition_average=aggregate(results),
      by_shift={str(s):aggregate([r for r in results if r['shift']==s]) for s in range(4)},
      by_gt_new_position={c:aggregate([r for r in results if r['gt_new_letter']==c]) for c in LETTERS},
      all_four_mcq_correct=sum(all(p.get('mcq_by_shift',[])) and len(p.get('mcq_by_shift',[]))==4 for p in paired),
      all_four_joint_correct=sum(all(p.get('joint_by_shift',[])) and len(p.get('joint_by_shift',[]))==4 for p in paired),
      paired_vs_shift0=transition_summary,per_question=paired,paired_conditions=comparisons,
      limitations=['48 conditions are paired within 12 questions, not 48 independent questions.',
                  'No identical-input repeat control: fixed seed and temperature do not establish absolute determinism.',
                  'Shift0 is from the earlier run; numeric/session/time variation cannot be separated completely.',
                  'Mapped semantic IDs follow letters; descriptions never repair a letter selection.',
                  'Choice-position sensitivity is an existing diagnostic, not a novelty claim.'])
    for name, value in [('summary.json',summary)]:
        path=PUBLIC/name
        if path.exists(): raise RuntimeError('Refusing to replace analysis')
        save(path,value)
    with (PUBLIC/'paired_choices.csv').open('x',newline='') as out:
        writer=csv.writer(out,lineterminator='\n');writer.writerow(['id','s0_original_id','s1_original_id','s2_original_id','s3_original_id','s0_letter','s1_letter','s2_letter','s3_letter','category','letter_stable','semantic_stable'])
        for p in paired: writer.writerow([p['id'],*p.get('mapped_original_ids',[None]*4),*p.get('letters',[None]*4),p['category'],p.get('letter_stable'),p.get('semantic_stable')])
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--analyze-only',action='store_true');args=parser.parse_args()
    f=official_functions()
    if args.analyze_only:
        print(json.dumps(analyze(f),indent=2));return
    rows,conditions,reused,manifest=prepare(f);by_id={r['id']:r for r in rows}
    with (PUBLIC/'predictions.jsonl').open('x') as out:
        for r in reused: out.write(json.dumps(r,ensure_ascii=False)+'\n')
        out.flush()
        for index,condition in enumerate(manifest['execution_order'],1):
            ident,shift=condition['id'],condition['shift'];meta=conditions[ident,shift]
            save(PRIVATE/f'attempt_{ident}_s{shift}.json',dict(started_utc=datetime.now(timezone.utc).isoformat(),attempt=1))
            start=time.monotonic();response=None;fatal=None
            try:
                response=api('/api/chat',meta['payload'])
                save(PRIVATE/'responses'/f'{ident}_s{shift}.json',response)
                if not response.get('done') or 'message' not in response or response.get('error'):
                    raise RuntimeError('Incomplete or erroneous Ollama response')
                result=score(meta,response['message']['content'],response['message'].get('thinking'),by_id[ident],f)
            except Exception as exc:
                fatal=f'{type(exc).__name__}: {exc}'
                result=score(meta,'',None,by_id[ident],f);result['error']=fatal
                if isinstance(exc,urllib.error.HTTPError):
                    save(PRIVATE/'responses'/f'{ident}_s{shift}_error.json',{'error_body':exc.read().decode(errors='replace')})
            result.update(source='new_generation',additional_generations=1,attempt=1,
                          wall_seconds=round(time.monotonic()-start,4),
                          done_reason=response.get('done_reason') if response else None,
                          duration_fields={k:v for k,v in (response or {}).items() if k.endswith('_duration') or k.endswith('_count')})
            out.write(json.dumps(result,ensure_ascii=False)+'\n');out.flush()
            print(json.dumps(dict(completed=index,id=ident,shift=shift,letter=result['predicted_letter'],original_id=result['mapped_original_id'],error=fatal)),flush=True)
            if fatal: raise SystemExit('Stopped after external/runtime failure; retained all outputs; no retry')
    summary=analyze(f)
    history_after={str(p.relative_to(ROOT)):sha(p) for p in history_paths()}
    assert history_after==manifest['historical_sha256']
    assert chat_count()-manifest['initial_chat_requests']==len(manifest['execution_order'])
    save(PUBLIC/'verification.json',dict(historical_files_unchanged=True,additional_chat_requests=chat_count()-manifest['initial_chat_requests'],
                                       reused_shift0=12,preflight_checked_items=len(manifest['checks']),
                                       completed_new_generations=summary['completed_new_generations']))
    print('COMPLETE',summary['decision'],summary['completed_new_generations'],'new generations',flush=True)


if __name__=='__main__':
    main()
