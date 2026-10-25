"""Single-pass local Ollama baseline; uses pinned official pure prompt/scoring functions."""
import argparse
import ast
import base64
import hashlib
import json
import platform
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'ollama_run'
PRIVATE = ROOT / 'private/ollama_run'
MODEL = 'qwen3-vl:4b-instruct-q4_K_M'
DIGEST = 'sha256:84f7ed8042fa7cdbd902f7dcb7d0370e032095047cc3244179f263b77b5bc318'
BASE = 'http://127.0.0.1:11435'
OPTIONS = dict(temperature=0, seed=20261025, num_ctx=8192, num_predict=4096)
SOURCE_SHA = 'd4afdddcb9f027485b2dd0c9c1276e93359936bb6b6b7b1de2c39e438eff9555'


def official_functions():
    source = (ROOT / 'private/benchmark_qwen.py').read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA
    names = {'remove_tags', 'build_prompt', 'parse_mcq_answer', 'extract_choice_letter',
             'normalized_to_pixel', 'xywh_to_xyxy', 'calculate_iou_xyxy', 'calculate_iou',
             'parse_response', 'is_valid_bbox', 'is_valid_prediction', 'compute_score',
             'calculate_mcq_accuracy'}
    nodes = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == names
    namespace = {'re': re, 'Optional': Optional}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'pinned_official_functions', 'exec'), namespace)
    return namespace


def api(endpoint, payload=None, timeout=300):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(BASE + endpoint, data=data,
                                     headers={'Content-Type': 'application/json'})
    # Explicitly bypass environment proxies for the loopback-only service.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=timeout) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['first12', 'extra60'])
    args = parser.parse_args()
    examples_path = ROOT / ('private/fixed12.jsonl' if args.phase == 'first12'
                            else 'private/ollama_run/extra60.jsonl')
    examples = [json.loads(line) for line in examples_path.read_text().splitlines()]
    assert len(examples) == (12 if args.phase == 'first12' else 60)
    assert len({r['id'] for r in examples}) == len(examples)
    output = PUBLIC / (args.phase + '_predictions.jsonl')
    if output.exists():
        raise RuntimeError('Refusing to rerun or overwrite an existing batch')
    tags = api('/api/tags')
    installed = next(r for r in tags['models'] if r['name'] == MODEL)
    assert installed['digest'].removeprefix('sha256:') == DIGEST.removeprefix('sha256:'), installed
    metadata = dict(model=MODEL, digest=DIGEST, options=OPTIONS, runtime=api('/api/version'),
                    model_details=api('/api/show', {'model': MODEL}), platform=platform.platform(),
                    architecture=platform.machine(), python=platform.python_version(),
                    phase=args.phase, source_sha256=SOURCE_SHA,
                    examples_sha256=hashlib.sha256(examples_path.read_bytes()).hexdigest(),
                    started_utc=datetime.now(timezone.utc).isoformat(), max_attempts_per_id=1,
                    baseline='Ollama quantized base Qwen3-VL; NOT authors post-trained checkpoint')
    (PRIVATE / (args.phase + '_runtime.json')).write_text(json.dumps(metadata, indent=2)+'\n')
    funcs = official_functions()
    with output.open('x') as out:
        for index, row in enumerate(examples, 1):
            image_path = ROOT / 'private/images' / row['image_path']
            image_bytes = image_path.read_bytes()
            with Image.open(image_path) as image:
                width, height = image.size
            assert f'{width}x{height}' == row['image_resolution']
            prompt = funcs['build_prompt'](row.get('question_tag') or row['question'])
            # Only image, original question/options and the official format instruction enter the model.
            payload = {'model': MODEL, 'messages': [{'role': 'user', 'content': prompt,
                       'images': [base64.b64encode(image_bytes).decode()]}],
                       'stream': False, 'options': OPTIONS, 'keep_alive': '20m'}
            saved_input = dict(id=row['id'], phase=args.phase, model=MODEL, digest=DIGEST,
                               prompt=prompt, image_path=str(image_path), options=OPTIONS,
                               image_sha256=hashlib.sha256(image_bytes).hexdigest(),
                               stream=False, keep_alive='20m')
            request_path = PRIVATE / 'requests' / f"{row['id']}.json"
            with request_path.open('x') as f:
                json.dump(saved_input, f, ensure_ascii=False, indent=2)
            start = time.monotonic()
            result = dict(id=row['id'], phase=args.phase, hop=row['hop'], view=row['view'],
                          image_sha256=saved_input['image_sha256'], attempt=1,
                          raw_response=None, thinking=None, prediction=None, pred_bbox=None,
                          mcq_correct=False, iou=None, joint_correct=False,
                          mcq_parse_valid=False, bbox_valid=False, output_valid=False, error=None)
            fatal = False
            try:
                response = api('/api/chat', payload)
                (PRIVATE / 'responses' / f"{row['id']}.json").write_text(
                    json.dumps(response, ensure_ascii=False, indent=2)+'\n')
                result['raw_response'] = response.get('message', {}).get('content', '')
                result['thinking'] = response.get('message', {}).get('thinking')
                result['done_reason'] = response.get('done_reason')
                if not response.get('done'):
                    raise RuntimeError('Ollama returned an incomplete generation')
                result['duration_fields'] = {k: v for k, v in response.items()
                                             if k.endswith('_duration') or k.endswith('_count')}
                prediction = funcs['parse_mcq_answer'](result['raw_response'])
                result.update(prediction=prediction,
                              mcq_parse_valid=funcs['extract_choice_letter'](prediction) is not None,
                              mcq_correct=funcs['compute_score'](prediction, row['answer']))
                _, bbox = funcs['parse_response'](result['raw_response'])
                result.update(prediction=prediction, pred_bbox=bbox,
                              mcq_parse_valid=funcs['extract_choice_letter'](prediction) is not None,
                              bbox_valid=funcs['is_valid_bbox'](bbox),
                              output_valid=funcs['is_valid_prediction'](prediction, bbox),
                              mcq_correct=funcs['compute_score'](prediction, row['answer']),
                              iou=funcs['calculate_iou'](row['bbox'], bbox, width, height))
                result['joint_correct'] = bool(result['mcq_correct'] and result['iou'] is not None
                                               and result['iou'] >= 0.5)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                result['error'] = f'{type(exc).__name__}: {exc}'
                if isinstance(exc, urllib.error.HTTPError):
                    result['error_response'] = exc.read().decode(errors='replace')
                fatal = True
            except Exception as exc:
                result['error'] = f'{type(exc).__name__}: {exc}'
                fatal = result['raw_response'] is None
            result['wall_seconds'] = round(time.monotonic() - start, 4)
            result['outcome'] = ('runtime_error' if fatal else 'parse_failure' if not result['mcq_parse_valid']
                                 else 'bbox_invalid' if not result['bbox_valid']
                                 else 'answer_error' if not result['mcq_correct']
                                 else 'localization_error' if not result['joint_correct'] else 'correct')
            out.write(json.dumps(result, ensure_ascii=False)+'\n')
            out.flush()
            print(json.dumps(dict(index=index, id=row['id'], seconds=result['wall_seconds'],
                                  outcome=result['outcome'])), flush=True)
            if fatal:
                raise SystemExit('Stopped on runtime failure; no retry, replacement, or next batch')
    (PRIVATE / (args.phase + '_loaded_model.json')).write_text(json.dumps(api('/api/ps'), indent=2)+'\n')
    print('BATCH_COMPLETED', args.phase, len(examples), flush=True)


if __name__ == '__main__':
    main()
