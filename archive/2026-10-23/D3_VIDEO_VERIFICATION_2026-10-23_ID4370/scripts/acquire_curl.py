from pathlib import Path
import datetime,hashlib,json,subprocess,time

O=Path(__file__).resolve().parent.parent
U='https://data.bris.ac.uk/datasets/3cqb5b81wk2dc2379fx1mrxh47/Videos/P01/P01-20240202-110250.mp4'
N=357839862;LIMIT=359937014;DISK=536870912;E='"664fd8fc-155433f6"'
prior=json.loads((O/'logs/TRANSFER_LEDGER.json').read_text())
assert prior['media_response_body_bytes']==0 and prior['status']=='STOPPED'
ledger=O/'logs/TRANSFER_LEDGER_CURL.json'
assert not ledger.exists()
L={'prior_attempt_ledger':'TRANSFER_LEDGER.json','prior_body_bytes':0,'media_response_body_bytes':0,'range_probe_body_bytes':0,'attempts':[],'status':'RUNNING','wire_bytes':'NOT_MEASURED','automatic_curl_retries':0}
def save(): ledger.write_text(json.dumps(L,indent=2)+'\n')
def localbytes():return sum(p.stat().st_size for p in O.rglob('*') if p.is_file())
def get(name,n,range_spec=None):
    target=O/'media'/name
    assert not target.exists()
    assert L['media_response_body_bytes']+n<=LIMIT and localbytes()+n+1048576<=DISK
    index=len(L['attempts']);tag=f'curl_{index}'
    args=['curl','--silent','--show-error','--fail','--retry','0','--proto','=https','--connect-timeout','20','--max-time','1800','--max-filesize',str(n),'--header','Accept-Encoding: identity','--header',f'If-Match: {E}','--dump-header',str(O/'logs'/f'{tag}_headers.txt'),'--output',str(target),'--write-out','%{json}']
    if range_spec:args+=['--range',range_spec]
    args+=[U]
    rec={'name':name,'range':range_spec,'started_at':datetime.datetime.now().astimezone().isoformat(),'complete':False};L['attempts'].append(rec);save()
    run=subprocess.run(args,capture_output=True,text=True)
    raw=json.loads(run.stdout)
    stats={k:raw.get(k) for k in ['exitcode','http_code','size_download','size_header','content_type','time_total','speed_download','num_redirects','url_effective','errormsg']}
    (O/'logs'/f'{tag}_stats.json').write_text(json.dumps(stats,indent=2)+'\n')
    (O/'logs'/f'{tag}_stderr.txt').write_text(run.stderr)
    rec['curl']=stats;rec['body_bytes']=int(stats['size_download']);L['media_response_body_bytes']+=rec['body_bytes']
    if range_spec:L['range_probe_body_bytes']+=rec['body_bytes']
    save()
    assert run.returncode==0,(run.returncode,run.stderr)
    headers={}
    for line in (O/'logs'/f'{tag}_headers.txt').read_text().splitlines():
        if ':' in line:
            k,v=line.split(':',1);headers[k.lower()]=v.strip()
    assert stats['http_code']==(206 if range_spec else 200)
    assert stats['url_effective']==U and stats['num_redirects']==0
    assert headers.get('etag')==E and headers.get('content-type')=='video/mp4'
    assert int(headers['content-length'])==n==rec['body_bytes']==target.stat().st_size
    if range_spec:assert headers.get('content-range')==f'bytes {range_spec}/{N}'
    assert L['media_response_body_bytes']<=LIMIT and L['range_probe_body_bytes']<=2097152 and localbytes()<=DISK
    rec['complete']=True;save();print(json.dumps(rec),flush=True)
    return target

try:
    save();get('range_head_0_65535.bin',65536,'0-65535')
    file=get('P01-20240202-110250.mp4',N)
    md=hashlib.md5();sh=hashlib.sha256()
    with file.open('rb') as f:
        while b:=f.read(1024*1024):md.update(b);sh.update(b)
    L['file_verification']={'bytes':file.stat().st_size,'md5':md.hexdigest(),'sha256':sh.hexdigest()}
    assert md.hexdigest()=='c981eab775c96858da313acef769b014','HASH MISMATCH: STOP'
    L['status']='VERIFIED';L['local_bytes_after_acquisition']=localbytes();save();print(json.dumps(L['file_verification']),flush=True)
except Exception as e:
    L['status']='STOPPED';L['error']=repr(e);save();print(json.dumps({'status':'STOPPED','error':repr(e)}),flush=True);raise
