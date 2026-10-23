from pathlib import Path
import csv, json, struct
from fractions import Fraction

OUT=Path(__file__).resolve().parent.parent
ledger=json.loads((OUT/'logs/TRANSFER_LEDGER_CURL.json').read_text())
assert ledger['status']=='VERIFIED', 'Hash verification required first'
FILE=OUT/'media/P01-20240202-110250.mp4'
F=FILE.open('rb'); SIZE=FILE.stat().st_size

def boxes(start,end):
    p=start
    while p<end:
        assert end-p>=8, (p,end)
        F.seek(p); size,kind=struct.unpack('>I4s',F.read(8)); header=8
        if size==1: size=struct.unpack('>Q',F.read(8))[0]; header=16
        if size==0: size=end-p
        assert size>=header and p+size<=end,(p,size,end)
        yield {'type':kind.decode('latin1'),'offset':p,'size':size,'payload':p+header,'end':p+size}
        p+=size
def children(b): return list(boxes(b['payload'],b['end']))
def one(bs,kind):
    values=[b for b in bs if b['type']==kind]; assert len(values)==1,(kind,len(values)); return values[0]
def data(b):
    assert b['size']<16*1024*1024
    F.seek(b['payload']);return F.read(b['end']-b['payload'])
def scale_duration(b):
    d=data(b)
    if d[0]==0: scale,duration=struct.unpack_from('>II',d,12)
    elif d[0]==1: scale,duration=struct.unpack_from('>IQ',d,20)
    else: raise ValueError('unsupported version')
    return {'version':d[0],'timescale':scale,'duration_ticks':duration,'duration_seconds':duration/scale}
def runs(b,signed=False):
    d=data(b); count=struct.unpack_from('>I',d,4)[0]
    assert len(d)==8+count*8
    return [struct.unpack_from('>Ii' if signed and d[0]==1 else '>II',d,8+i*8) for i in range(count)]

top=list(boxes(0,SIZE));moov=one(top,'moov');mc=children(moov)
movie=scale_duration(one(mc,'mvhd'))
info={'top_level_boxes':top,'movie':movie,'tracks':[]}
for trak in [b for b in mc if b['type']=='trak']:
    tc=children(trak);tk=data(one(tc,'tkhd'));tid=struct.unpack_from('>I',tk,12 if tk[0]==0 else 20)[0]
    mdia=children(one(tc,'mdia'));handler=data(one(mdia,'hdlr'))[8:12].decode()
    mdhd=scale_duration(one(mdia,'mdhd'))
    edits=[]
    edts=[b for b in tc if b['type']=='edts']
    if edts:
        d=data(one(children(edts[0]),'elst')); n=struct.unpack_from('>I',d,4)[0]; cursor=8
        for i in range(n):
            fmt='>Iihh' if d[0]==0 else '>Qqhh'; size=struct.calcsize(fmt)
            dur,media,ri,rf=struct.unpack_from(fmt,d,cursor);cursor+=size
            edits.append({'segment_duration_movie_ticks':dur,'media_time_track_ticks':media,'rate_integer':ri,'rate_fraction':rf})
    rec={'track_id':tid,'handler':handler,'media_header':mdhd,'edit_list':edits}; info['tracks'].append(rec)
    if handler!='vide': continue
    stbl=children(one(children(one(mdia,'minf')),'stbl'))
    stts=runs(one(stbl,'stts')); cttsbox=[b for b in stbl if b['type']=='ctts']
    ctts=runs(cttsbox[0],True) if cttsbox else [(sum(a for a,b in stts),0)]
    offsets=[v for n,v in ctts for _ in range(n)]
    durations=[v for n,v in stts for _ in range(n)]
    assert len(offsets)==len(durations)
    syncbox=[b for b in stbl if b['type']=='stss']
    if syncbox:
        d=data(syncbox[0]); n=struct.unpack_from('>I',d,4)[0];sync=set(struct.unpack_from('>'+str(n)+'I',d,8))
    else: sync=set(range(1,len(offsets)+1))
    sd=data(one(stbl,'stsd'));rec['codec_entry']=sd[12:16].decode('latin1')
    sz=data(one(stbl,'stsz'));default_size,ns=struct.unpack_from('>II',sz,4)
    sizes=[default_size]*ns if default_size else list(struct.unpack_from('>'+str(ns)+'I',sz,12))
    assert ns==len(offsets)
    rec.update({'sample_count':ns,'stts_runs':stts,'ctts_runs_count':len(ctts),'sync_sample_count':len(sync),'compressed_video_bytes':sum(sizes)})
    # Map the actual edit list. This file must have one nonempty rate-1 segment.
    active=[e for e in edits if e['media_time_track_ticks']!=-1]
    assert len(active)==1 and active[0]['rate_integer']==1 and active[0]['rate_fraction']==0, 'Ambiguous edit mapping'
    lead=Fraction(0); selected=active[0]
    for e in edits:
        if e is selected: break
        assert e['media_time_track_ticks']==-1
        lead+=Fraction(e['segment_duration_movie_ticks'],movie['timescale'])
    origin=selected['media_time_track_ticks'];scale=mdhd['timescale'];dts=0;rows=[]
    for i,(dur,off,sz) in enumerate(zip(durations,offsets,sizes)):
        pts=dts+off; presentation=lead+Fraction(pts-origin,scale)
        rows.append({'decode_index':i,'raw_dts_ticks':dts,'raw_pts_ticks':pts,'track_timescale':scale,'movie_pts_seconds':float(presentation),'movie_pts_numerator':presentation.numerator,'movie_pts_denominator':presentation.denominator,'sample_bytes':sz,'sync':i+1 in sync})
        dts+=dur
    with (OUT/'logs/MP4_SAMPLE_TIMELINE.csv').open('x') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    ordered=sorted(rows,key=lambda r:r['movie_pts_seconds'])
    rec['presentation_first']=ordered[0];rec['presentation_last']=ordered[-1]
    rec['boundaries']={}
    for q in [187.89,200.78,224.65,288.65]:
        rec['boundaries'][str(q)]={'last_at_or_before':max((r for r in ordered if r['movie_pts_seconds']<=q),key=lambda r:r['movie_pts_seconds']),'first_after':min((r for r in ordered if r['movie_pts_seconds']>q),key=lambda r:r['movie_pts_seconds'])}
    for name,a,b in [('old',187.89,200.78),('between',200.78,224.65),('recent',224.65,288.65),('prefix',0,288.65)]:
        inrange=[r for r in ordered if a<=r['movie_pts_seconds']<=b]
        rec[name]={'frame_count':len(inrange),'compressed_sample_bytes':sum(r['sample_bytes'] for r in inrange),'first':inrange[0]['movie_pts_seconds'],'last':inrange[-1]['movie_pts_seconds']}
with (OUT/'logs/MP4_CONTAINER_AUDIT.json').open('x') as f: json.dump(info,f,indent=2);f.write('\n')
print(json.dumps(info,indent=2))
