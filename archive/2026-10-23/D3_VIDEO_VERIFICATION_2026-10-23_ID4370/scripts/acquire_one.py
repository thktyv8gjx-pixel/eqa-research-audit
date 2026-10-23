from pathlib import Path
import datetime, hashlib, json, socket, time, urllib.request, urllib.error

OUT = Path(__file__).resolve().parent.parent
URL = 'https://data.bris.ac.uk/datasets/3cqb5b81wk2dc2379fx1mrxh47/Videos/P01/P01-20240202-110250.mp4'
N = 357839862
MD5 = 'c981eab775c96858da313acef769b014'
ETAG = '"664fd8fc-155433f6"'
LIMIT = 359937014
DISK_LIMIT = 536870912
ledger_path = OUT/'logs/TRANSFER_LEDGER.json'
assert not ledger_path.exists(), 'No automatic repeat of this acquisition script'
ledger = {'started_at':datetime.datetime.now().astimezone().isoformat(), 'url':URL,
          'media_response_body_bytes':0, 'range_probe_body_bytes':0, 'attempts':[],
          'automatic_retries':0, 'wire_bytes':'NOT_MEASURED', 'status':'RUNNING'}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Redirect forbidden for the fixed source')

opener = urllib.request.build_opener(NoRedirect)
def save():
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2)+'\n')
def disk_bytes():
    return sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
def fetch(path, first=None, last=None):
    expected = N if first is None else last-first+1
    assert ledger['media_response_body_bytes']+expected <= LIMIT
    assert disk_bytes()+expected+1024*1024 <= DISK_LIMIT
    assert not path.exists()
    h={'Accept-Encoding':'identity','User-Agent':'EQA-bounded-single-file-audit/1.0'}
    if first is not None: h['Range']=f'bytes={first}-{last}'
    rec={'method':'GET','range':h.get('Range'),'body_bytes':0,'path':str(path.relative_to(OUT)),
         'started_at':datetime.datetime.now().astimezone().isoformat(),'complete':False}
    ledger['attempts'].append(rec); save()
    deadline=time.monotonic()+1800
    with opener.open(urllib.request.Request(URL,headers=h), timeout=60) as response:
        rec['status']=response.status
        rec['headers']={k.lower():v for k,v in response.headers.items() if k.lower() in ['content-length','content-type','content-range','etag','last-modified','accept-ranges','date']}
        save()
        assert response.geturl()==URL, 'Source URL changed'
        assert response.status==(200 if first is None else 206), 'Unexpected response status'
        assert response.headers.get('ETag')==ETAG, 'Resource version changed'
        assert response.headers.get_content_type()=='video/mp4', 'Unexpected content type'
        assert int(response.headers['Content-Length'])==expected, 'Content-Length changed'
        if first is not None:
            assert response.headers.get('Content-Range')==f'bytes {first}-{last}/{N}'
        milestone=0
        with path.open('xb') as f:
            while rec['body_bytes'] < expected:
                assert time.monotonic()<deadline, 'Transfer deadline'
                block=response.read(min(262144,expected-rec['body_bytes']))
                if not block: raise RuntimeError('Premature EOF')
                f.write(block)
                rec['body_bytes']+=len(block); ledger['media_response_body_bytes']+=len(block)
                if first is not None: ledger['range_probe_body_bytes']+=len(block)
                assert ledger['media_response_body_bytes']<=LIMIT
                if rec['body_bytes']//(16*1024*1024)>milestone:
                    milestone=rec['body_bytes']//(16*1024*1024)
                    save(); print(json.dumps({'downloaded_bytes':rec['body_bytes'],'expected':expected}),flush=True)
            f.flush()
    rec['complete']=True; rec['finished_at']=datetime.datetime.now().astimezone().isoformat(); save()
    return path

try:
    save()
    fetch(OUT/'media/range_head_0_65535.bin',0,65535)
    original=fetch(OUT/'media/P01-20240202-110250.mp4')
    md5=hashlib.md5(); sha=hashlib.sha256()
    with original.open('rb') as f:
        while block:=f.read(1024*1024): md5.update(block); sha.update(block)
    ledger['file_verification']={'bytes':original.stat().st_size,'md5':md5.hexdigest(),'sha256':sha.hexdigest()}
    assert original.stat().st_size==N and md5.hexdigest()==MD5, 'FILE IDENTITY MISMATCH: STOP'
    ledger['local_bytes_after_acquisition']=disk_bytes()
    assert ledger['local_bytes_after_acquisition']<=DISK_LIMIT
    ledger['status']='VERIFIED'; save(); print(json.dumps(ledger['file_verification']),flush=True)
except Exception as e:
    ledger['status']='STOPPED'; ledger['error']=repr(e); save()
    print(json.dumps({'status':'STOPPED','error':repr(e),'body_bytes':ledger['media_response_body_bytes']}),flush=True)
    raise
