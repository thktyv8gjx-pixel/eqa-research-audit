"""Bounded, pre-frozen ROI-blur diagnostic on existing MultihopSpatial samples."""
import argparse
import base64
import hashlib
import json
import time
import urllib.error
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import PIL
from PIL import Image, ImageDraw, ImageFilter

from run_ollama import ROOT, MODEL, DIGEST, OPTIONS, api, official_functions
from circular12 import split_choices

PUBLIC = ROOT/'ollama_run/constraint_blur'
PRIVATE = ROOT/'private/ollama_run/constraint_blur'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x') as out:
        json.dump(value,out,ensure_ascii=False,indent=2)
        out.write('\n')


def load_data():
    examples={r['id']:r for p in (ROOT/'private/fixed12.jsonl',ROOT/'private/ollama_run/extra60.jsonl')
              for r in map(json.loads,p.read_text().splitlines())}
    predictions={r['id']:r for p in (ROOT/'ollama_run/first12_predictions.jsonl',ROOT/'ollama_run/extra60_predictions.jsonl')
                 for r in map(json.loads,p.read_text().splitlines())}
    assert len(examples)==len(predictions)==72
    return examples,predictions


def history():
    names=['private/benchmark_qwen.py','ollama_run/run_ollama.py','ollama_run/first12_predictions.jsonl',
           'ollama_run/extra60_predictions.jsonl','ollama_run/environment.json',
           'ollama_run/circular12/predictions.jsonl']
    return {name:sha(ROOT/name) for name in names}


def prepare():
    f=official_functions();examples,predictions=load_data()
    spec=json.loads((PUBLIC/'selection_spec.json').read_text())
    (PRIVATE/'images').mkdir();(PRIVATE/'requests').mkdir();(PRIVATE/'responses').mkdir()
    records=[]
    for item in spec['selected']:
        ident=item['id'];row=examples[ident];old=predictions[ident]
        request=json.loads((ROOT/'private/ollama_run/requests'/f'{ident}.json').read_text())
        source=ROOT/'private/images'/row['image_path'];image=Image.open(source).convert('RGB')
        w,h=image.size;array=np.array(image)
        assert sha(source)==request['image_sha256']==old['image_sha256']
        assert f['build_prompt'](row['question_tag'])==request['prompt']
        assert request['model']==MODEL and request['options']==OPTIONS
        assert request['digest'].removeprefix('sha256:')==DIGEST.removeprefix('sha256:')
        assert (not old['mcq_correct']) if item['cohort']=='wrong_verified_distractor' else old['joint_correct']
        bx,by,bw,bh=row['bbox']
        protected=[dict(name='GT target',box=[bx,by,bx+bw,by+bh])]+item['protected']
        image_paths={'A':PRIVATE/'images'/f'{ident}_A.jpg'}
        image_paths['A'].write_bytes(source.read_bytes())
        edit_records={}
        for condition in ('B','C'):
            box=item[condition];x1,y1,x2,y2=box
            assert all(isinstance(v,int) for v in box) and 0<=x1<x2<=w and 0<=y1<y2<=h
            for region in protected:
                a,b,c,d=region['box']
                assert max(x1,a)>=min(x2,c) or max(y1,b)>=min(y2,d), (ident,condition,region)
            edited=image.copy();edited.paste(image.crop(box).filter(ImageFilter.GaussianBlur(spec['radius_px'])),(x1,y1))
            path=PRIVATE/'images'/f'{ident}_{condition}.png';edited.save(path)
            actual=np.array(Image.open(path).convert('RGB'))
            diff=np.abs(actual.astype(np.int16)-array.astype(np.int16));outside=diff.copy();outside[y1:y2,x1:x2]=0
            assert not np.any(outside), (ident,'pixel changes outside ROI')
            changed=int(np.count_nonzero(np.any(diff,axis=2)));assert changed>0,(ident,'null edit')
            area=(x2-x1)*(y2-y1)
            edit_records[condition]=dict(roi=box,area_px=area,image_sha256=sha(path),changed_pixels=changed,
                  patch_mean_absolute_rgb_change=float(diff[y1:y2,x1:x2].mean()),
                  image_mean_absolute_rgb_change=float(diff.mean()),outside_roi_unchanged=True,
                  protected_target_and_references_unchanged=True,format='PNG')
            image_paths[condition]=path
        assert edit_records['B']['area_px']==edit_records['C']['area_px']
        assert (item['B'][2]-item['B'][0],item['B'][3]-item['B'][1])==(item['C'][2]-item['C'][0],item['C'][3]-item['C'][1])
        record={k:v for k,v in item.items() if k!='protected'}
        record.update(hop=row['hop'],view=row['view'],source_image_sha256=sha(source),
                      prompt_sha256=hashlib.sha256(request['prompt'].encode()).hexdigest(),
                      baseline_correct=old['mcq_correct'],baseline_joint_correct=old['joint_correct'],
                      original_distractor_letter=f['extract_choice_letter'](old['prediction']) if item['cohort']=='wrong_verified_distractor' else None,
                      edits=edit_records)
        records.append(record)
    manifest=dict(spec_sha256=sha(PUBLIC/'selection_spec.json'),frozen_before_new_predictions=True,
                  model=MODEL,digest=DIGEST,options=OPTIONS,pillow=PIL.__version__,numpy=np.__version__,
                  radius_px=spec['radius_px'],historical_sha256=history(),records=records,
                  limitations=['A is a historical JPEG-input run; both new conditions use lossless PNG.',
                  'Equal ROI area and Gaussian radius do not imply equal texture energy, saliency or removed information.',
                  'Blur is not verified object erasure; some outlines, color and low-frequency features remain.',
                  'GT final box exists, but no complete intermediate or 3D truth.'])
    write(PUBLIC/'frozen_manifest.json',manifest)
    # Three-image rows, only for pre-inference visual inspection; these overlays are never model inputs.
    for start in range(0,len(records),3):
        page=Image.new('RGB',(960,960),'white');draw=ImageDraw.Draw(page)
        for j,r in enumerate(records[start:start+3]):
            for k,c in enumerate('ABC'):
                p=PRIVATE/'images'/f"{r['id']}_{c}.{'jpg' if c=='A' else 'png'}"
                im=Image.open(p).convert('RGB');im.thumbnail((320,275));page.paste(im,(k*320,j*320+35))
                draw.text((k*320+3,j*320+3),f"ID {r['id']} {c} {r['cohort'][:7]}",fill='black')
                if c!='A':draw.text((k*320+3,j*320+18),'ROI '+str(r[c]),fill='black')
        page.save(PRIVATE/f'edited_review_{start//3}.png')
    print('PREPARED',len(records),'paired edits; frozen sigma',spec['radius_px'],flush=True)


def evaluate(row,meta,condition,response,f):
    raw=response.get('message',{}).get('content','');prediction=f['parse_mcq_answer'](raw)
    letter=f['extract_choice_letter'](prediction);bbox=None;parse_error=None
    try:_,bbox=f['parse_response'](raw)
    except (ValueError,TypeError) as exc:parse_error=str(exc)
    w,h=map(int,row['image_resolution'].split('x'));iou=f['calculate_iou'](row['bbox'],bbox,w,h)
    correct=f['compute_score'](prediction,row['answer'])
    description=re_description(prediction)
    _,options,_=split_choices(row['question_tag'])
    matches=[chr(97+i) for i,text in enumerate(options) if description and description.casefold().strip().rstrip('.')==text.casefold()]
    pred_pixel=f['normalized_to_pixel'](bbox,w,h) if f['is_valid_bbox'](bbox) else None
    return dict(id=row['id'],cohort=meta['cohort'],constraint=meta['constraint'],hop=row['hop'],view=row['view'],condition=condition,
                prediction=prediction,predicted_letter=letter,raw_object_description=description,
                description_literal_letter=matches[0] if len(matches)==1 else None,
                raw_response=raw,thinking=response.get('message',{}).get('thinking'),pred_bbox=bbox,iou=iou,
                mcq_correct=correct,joint_correct=bool(correct and iou is not None and iou>=.5),
                output_valid=f['is_valid_prediction'](prediction,bbox),parse_error=parse_error,error=None,
                original_distractor_letter=meta['original_distractor_letter'],
                chooses_original_distractor=letter==meta['original_distractor_letter'] if meta['original_distractor_letter'] else None,
                pred_box_vs_B_roi_iou=f['calculate_iou_xyxy'](pred_pixel,meta['B']) if pred_pixel else None)


def re_description(prediction):
    import re
    return re.sub(r'^\([a-d]\)\s*','',prediction,count=1,flags=re.I) if prediction else None


def summarize():
    rows=[json.loads(line) for line in (PUBLIC/'predictions.jsonl').read_text().splitlines()]
    by={(r['id'],r['condition']):r for r in rows};manifest=json.loads((PUBLIC/'frozen_manifest.json').read_text())
    def metrics(group):
        n=len(group);return dict(n=n,mcq_correct=sum(r['mcq_correct'] for r in group),joint_correct=sum(r['joint_correct'] for r in group),
          invalid_outputs=sum(not r['output_valid'] for r in group),mean_gt_iou=sum(r['iou'] or 0 for r in group)/n if n else None)
    comparisons=[]
    for meta in manifest['records']:
        ident=meta['id'];group=[by.get((ident,c)) for c in 'ABC']
        if any(r is None for r in group):continue
        a,b,c=group
        comparisons.append(dict(id=ident,cohort=meta['cohort'],constraint=meta['constraint'],hop=meta['hop'],
          letters=[r['predicted_letter'] for r in group],mcq=[r['mcq_correct'] for r in group],joint=[r['joint_correct'] for r in group],
          gt_ious=[r['iou'] for r in group],B_changed=b['predicted_letter']!=a['predicted_letter'],C_changed=c['predicted_letter']!=a['predicted_letter'],
          selective_rescue=not a['mcq_correct'] and b['mcq_correct'] and not c['mcq_correct'],
          selective_harm=a['mcq_correct'] and not b['mcq_correct'] and c['mcq_correct']))
    groups={}
    for name in ('wrong_verified_distractor','correct_background_control'):
        items=[p for p in comparisons if p['cohort']==name]
        groups[name]=dict(n_items=len(items),by_condition={c:metrics([r for r in rows if r['cohort']==name and r['condition']==c]) for c in 'ABC'},
          selective_B_rescue_C_not=sum(p['selective_rescue'] for p in items),selective_B_harm_C_preserved=sum(p['selective_harm'] for p in items),
          both_changed=sum(p['B_changed'] and p['C_changed'] for p in items),both_unchanged=sum(not p['B_changed'] and not p['C_changed'] for p in items),
          B_only_changed=sum(p['B_changed'] and not p['C_changed'] for p in items),C_only_changed=sum(not p['B_changed'] and p['C_changed'] for p in items),
          by_hop={h:{c:metrics([r for r in rows if r['cohort']==name and r['hop']==h and r['condition']==c]) for c in 'ABC'} for h in ('1hop','2hop','3hop')},
          by_constraint={t:{c:metrics([r for r in rows if r['cohort']==name and r['constraint']==t and r['condition']==c]) for c in 'ABC'} for t in sorted({p['constraint'] for p in items})})
    summary=dict(n_items=len(comparisons),new_generations=sum(r['condition']!='A' for r in rows),
                 new_wall_seconds=sum(r['wall_seconds'] for r in rows if r['condition']!='A'),groups=groups,paired=comparisons,
                 note='Exploratory post-baseline selection; cohorts have different ROI selection mechanisms and are not pooled for treatment effects.')
    write(PUBLIC/'summary.json',summary);print(json.dumps(summary,indent=2))


def run():
    f=official_functions();examples,old=load_data();manifest=json.loads((PUBLIC/'frozen_manifest.json').read_text())
    assert sha(PUBLIC/'selection_spec.json')==manifest['spec_sha256'] and history()==manifest['historical_sha256']
    review=json.loads((PRIVATE/'post_edit_review.json').read_text());assert review['accepted_ids']==[r['id'] for r in manifest['records']]
    assert review['original_answer_and_references_preserved'] and review['manifest_sha256']==sha(PUBLIC/'frozen_manifest.json')
    environment=json.loads((ROOT/'ollama_run/environment.json').read_text());assert api('/api/version')==environment['runtime']
    installed=next(r for r in api('/api/tags')['models'] if r['name']==MODEL)
    assert installed['digest'].removeprefix('sha256:')==DIGEST.removeprefix('sha256:')
    log=PRIVATE/'server.log'
    initial=sum('POST' in line and '/api/chat' in line for line in log.read_text().splitlines())
    with (PUBLIC/'predictions.jsonl').open('x') as out:
        for index,meta in enumerate(manifest['records']):
            ident=meta['id'];row=examples[ident];request=json.loads((ROOT/'private/ollama_run/requests'/f'{ident}.json').read_text())
            response=json.loads((ROOT/'private/ollama_run/responses'/f'{ident}.json').read_text())
            a=evaluate(row,meta,'A',response,f);a.update(wall_seconds=0,source='reused_original_72',image_sha256=meta['source_image_sha256'])
            assert a['mcq_correct']==old[ident]['mcq_correct'] and a['iou']==old[ident]['iou']
            out.write(json.dumps(a,ensure_ascii=False)+'\n');out.flush()
            write(PRIVATE/'requests'/f'{ident}_A.json',request);write(PRIVATE/'responses'/f'{ident}_A.json',response)
            order=('B','C') if index%2==0 else ('C','B')
            for condition in order:
                path=PRIVATE/'images'/f'{ident}_{condition}.png';assert sha(path)==meta['edits'][condition]['image_sha256']
                payload=dict(model=MODEL,messages=[dict(role='user',content=request['prompt'],images=[base64.b64encode(path.read_bytes()).decode()])],
                             stream=False,options=dict(OPTIONS),keep_alive='20m')
                write(PRIVATE/'requests'/f'{ident}_{condition}.json',payload)
                start=time.monotonic();response=None;error=None
                try:
                    response=api('/api/chat',payload);write(PRIVATE/'responses'/f'{ident}_{condition}.json',response)
                    if not response.get('done') or response.get('error') or 'message' not in response:raise RuntimeError('Incomplete/erroneous response')
                except Exception as exc:
                    error=f'{type(exc).__name__}: {exc}'
                    if isinstance(exc,urllib.error.HTTPError):write(PRIVATE/'responses'/f'{ident}_{condition}_error.json',dict(error_body=exc.read().decode(errors='replace')))
                result=evaluate(row,meta,condition,response or {},f)
                result.update(wall_seconds=round(time.monotonic()-start,4),error=error,source='new_generation',image_sha256=sha(path),
                              duration_fields={k:v for k,v in (response or {}).items() if k.endswith('_duration') or k.endswith('_count')})
                out.write(json.dumps(result,ensure_ascii=False)+'\n');out.flush()
                print('GENERATED',ident,condition,result['prediction'],result['mcq_correct'],error,flush=True)
                if error:raise SystemExit('Stopped without retry; all partial outputs retained')
    assert history()==manifest['historical_sha256']
    final=sum('POST' in line and '/api/chat' in line for line in log.read_text().splitlines())
    assert final-initial==2*len(manifest['records'])
    write(PUBLIC/'verification.json',dict(new_generation_requests=final-initial,historical_files_unchanged=True,
                  frozen_before_inference=True,post_edit_review_passed=True,identical_prompt_and_options=True))
    summarize()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);args=p.parse_args()
    prepare() if args.mode=='prepare' else run()
