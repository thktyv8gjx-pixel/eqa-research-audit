from pathlib import Path
import hashlib, http.server, json, os, signal, socket, subprocess, sys, threading, time, unittest

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'scripts'))
from bounded_resume import Downloader, GuardError, digest, Journal

DATA=bytes((i*37+i//251)%256 for i in range(65536+123))
CASES={}
REQUEST_LOG=[]
RUN_ID=os.environ.get('EQA_OFFLINE_RUN_ID','run2')
ROOT=BASE/'results/test_runs'/RUN_ID

class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,*args): pass
    def do_GET(self):
        case=CASES[self.path]
        start,end=map(int,self.headers['Range'].removeprefix('bytes=').split('-'))
        record={'path':self.path,'range':self.headers['Range'],'if_match':self.headers.get('If-Match'),'mode':case['mode']}
        REQUEST_LOG.append(record)
        mode=case['mode'];n=end-start+1
        status=200 if mode=='ignore_range' else (302 if mode=='redirect' else (412 if mode=='precondition' else 206))
        self.send_response(status)
        self.send_header('Content-Range',f'bytes {start+1 if mode=="wrong_range" else start}-{end}/{len(DATA)+1 if mode=="wrong_total" else len(DATA)}')
        self.send_header('Content-Length',str(len(DATA) if mode=='ignore_range' else (n+1 if mode=='wrong_length' else n)))
        self.send_header('ETag','"other"' if mode=='etag_change' else ('W/"fixture"' if mode=='weak_etag' else '"fixture"'))
        self.send_header('Content-Type','text/html' if mode=='wrong_type' else 'application/octet-stream')
        if mode=='gzip':self.send_header('Content-Encoding','gzip')
        if mode=='chunked':self.send_header('Transfer-Encoding','chunked')
        if mode=='redirect':self.send_header('Location','https://invalid.example/not-followed')
        self.send_header('Connection','close');self.end_headers()
        payload=DATA if mode=='ignore_range' else DATA[start:end+1]
        if mode=='short':payload=payload[:3072]
        if mode=='timeout':payload=payload[:1024]
        if mode=='corrupt':payload=bytes([payload[0]^1])+payload[1:]
        if mode=='delayed':time.sleep(.3)
        sent=0
        try:
            for i in range(0,len(payload),512):
                b=payload[i:i+512];self.wfile.write(b);self.wfile.flush();sent+=len(b)
                if mode=='slow':time.sleep(.002)
            if mode=='timeout':time.sleep(.3)
        except (BrokenPipeError,ConnectionResetError):pass
        record['server_body_written']=sent
        self.close_connection=True

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ROOT.mkdir(parents=True,exist_ok=False)
        cls.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.server.daemon_threads=True
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.port=cls.server.server_address[1]
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
        (BASE/'results'/f'LOOPBACK_REQUEST_LOG_{RUN_ID}.json').write_text(json.dumps(REQUEST_LOG,indent=2)+'\n')
    def make(self,name=None,mode='good',extra_budget=0):
        name=name or self._testMethodName
        p=ROOT/name;p.mkdir();prefix=p/'original-prefix.bin';prefix.write_bytes(DATA[:4096])
        path='/'+name;CASES[path]={'mode':mode}
        c={'mode':'offline','url':f'http://127.0.0.1:{self.port}{path}','total_bytes':len(DATA),
           'expected_md5':hashlib.md5(DATA).hexdigest(),'etag':'"fixture"','content_type':'application/octet-stream',
           'prefix':str(prefix),'prefix_bytes':4096,'prefix_sha256':hashlib.sha256(DATA[:4096]).hexdigest(),
           'work_dir':str(p/'work'),'request_bytes':16384,'read_bytes':1024,'timeout_seconds':1,
           'body_budget_bytes':len(DATA)-4096+extra_budget,'disk_budget_bytes':4*1024*1024,
           'metadata_reserve_bytes':32768,'disk_roots':[str(p)]}
        return c,path,p
    def run_child(self,c,p,phase,action='signal',sig=signal.SIGINT):
        cfg=p/'config.json';cfg.write_text(json.dumps(c));marker=p/'marker'
        proc=subprocess.Popen([sys.executable,str(BASE/'tests/worker.py'),str(cfg),phase,action,str(marker)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        deadline=time.monotonic()+8
        while not marker.exists() and proc.poll() is None and time.monotonic()<deadline:time.sleep(.005)
        self.assertTrue(marker.exists(),f'child hook not reached: {proc.poll()}')
        if action=='signal':os.kill(proc.pid,sig)
        stdout,stderr=proc.communicate(timeout=10)
        (p/'child.stdout').write_text(stdout);(p/'child.stderr').write_text(stderr)
        if action=='signal':
            self.assertEqual(proc.returncode,0,stderr)
            return json.loads(stdout)
        self.assertEqual(proc.returncode,87,stderr)
        return None
    def assert_prefix(self,c):self.assertEqual(digest(c['prefix']),c['prefix_sha256'])
    def test_complete_accounting(self):
        c,path,p=self.make();r=Downloader(c).run();self.assertEqual(r['status'],'VERIFIED')
        self.assertEqual(r['observed_body_bytes'],len(DATA)-4096);self.assertEqual(r['charged_upper_bytes'],r['observed_body_bytes'])
        self.assertEqual((p/'work/candidate.mp4.partial').read_bytes(),DATA);self.assert_prefix(c)
        events=Journal(p/'work/journal.jsonl').events
        self.assertTrue(any(e['kind']=='BODY' for e in events));self.assertEqual(sum(e['bytes'] for e in events if e['kind']=='BODY'),r['observed_body_bytes'])
        for i,e in enumerate(events):
            if e['kind']=='COMMIT':self.assertEqual(events[i-1]['kind'],'BODY')
    def test_stop_and_resume(self):
        c,path,p=self.make()
        def hook(phase,d):
            if phase=='after_body':d.stop()
        r=Downloader(c,hook).run();self.assertEqual(r['status'],'STOPPED_CLEANLY');self.assertEqual(r['observed_body_bytes'],16384)
        count=len(REQUEST_LOG);r2=Downloader(c).run();self.assertEqual(r2['status'],'VERIFIED')
        self.assertEqual(REQUEST_LOG[count]['range'],'bytes=20480-36863');self.assertEqual(r2['observed_body_bytes'],len(DATA)-4096);self.assert_prefix(c)
    def test_signals_transaction_stages(self):
        for sig in [signal.SIGINT,signal.SIGTERM]:
            for phase in ['after_begin','after_headers','after_read','after_body','after_write','after_commit']:
                with self.subTest(signal=sig,phase=phase):
                    c,path,p=self.make(f'signal_{sig}_{phase}',mode='delayed' if phase=='after_headers' else 'good')
                    r=self.run_child(c,p,phase,sig=sig)
                    self.assertEqual(r['status'],'STOPPED_CLEANLY');self.assertEqual(r['uncertain_requests'],0)
                    self.assertEqual(r['observed_body_bytes'],16384);self.assertEqual(r['durable_offset'],20480)
                    self.assertEqual(Downloader(c).run()['status'],'VERIFIED');self.assert_prefix(c)
    def test_signal_during_blocking_read(self):
        for sig in [signal.SIGINT,signal.SIGTERM]:
            c,path,p=self.make(f'blocking_{sig}',mode='delayed')
            cfg=p/'config.json';cfg.write_text(json.dumps(c))
            proc=subprocess.Popen([sys.executable,str(BASE/'scripts/bounded_resume.py'),str(cfg)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            journal=p/'work/journal.jsonl';deadline=time.monotonic()+8
            while time.monotonic()<deadline:
                if journal.exists() and '"kind":"HEADERS"' in journal.read_text():break
                time.sleep(.005)
            os.kill(proc.pid,sig);stdout,stderr=proc.communicate(timeout=8);self.assertEqual(proc.returncode,0,stderr)
            r=json.loads(stdout);self.assertEqual(r['status'],'STOPPED_CLEANLY');self.assertEqual(r['observed_body_bytes'],16384)
            self.assert_prefix(c)
    def test_short_response_and_resume(self):
        c,path,p=self.make(mode='short',extra_budget=16384)
        r=Downloader(c).run();self.assertEqual(r['status'],'STOPPED_ERROR');self.assertEqual(r['observed_body_bytes'],3072)
        self.assertEqual(r['charged_upper_bytes'],16384);self.assertEqual(r['durable_offset'],7168)
        CASES[path]['mode']='good';count=len(REQUEST_LOG);r2=Downloader(c).run()
        self.assertEqual(r2['status'],'VERIFIED');self.assertEqual(REQUEST_LOG[count]['range'],'bytes=7168-23551')
        self.assertEqual(r2['charged_upper_bytes'],len(DATA)-4096+(16384-3072));self.assert_prefix(c)
    def test_timeout_preserves_reservation(self):
        c,path,p=self.make(mode='timeout',extra_budget=16384);c['timeout_seconds']=.05
        r=Downloader(c).run();self.assertEqual(r['status'],'STOPPED_ERROR');self.assertEqual(r['charged_upper_bytes'],16384)
        self.assertGreaterEqual(r['observed_body_bytes'],0);self.assertLessEqual(r['observed_body_bytes'],1024);self.assert_prefix(c)
    def test_protocol_rejections(self):
        for mode in ['ignore_range','wrong_range','wrong_total','wrong_length','etag_change','weak_etag','gzip','chunked','redirect','precondition','wrong_type']:
            with self.subTest(mode=mode):
                c,path,p=self.make(mode,mode=mode);n=len(REQUEST_LOG)
                r=Downloader(c).run();self.assertEqual(r['status'],'STOPPED_ERROR');self.assertEqual(r['observed_body_bytes'],0)
                self.assertEqual(r['durable_offset'],4096);self.assertEqual(len(REQUEST_LOG),n+1);self.assert_prefix(c)
    def test_body_budget_before_network(self):
        c,path,p=self.make();c['body_budget_bytes']-=1;n=len(REQUEST_LOG)
        r=Downloader(c).run();self.assertEqual(r['status'],'STOPPED_ERROR');self.assertIn('BUDGET',r['error']);self.assertEqual(len(REQUEST_LOG),n)
    def test_disk_budget_before_network(self):
        c,path,p=self.make();c['disk_budget_bytes']=5000;n=len(REQUEST_LOG)
        with self.assertRaisesRegex(GuardError,'DISK_BUDGET'):Downloader(c)
        self.assertEqual(len(REQUEST_LOG),n);self.assert_prefix(c)
    def test_disk_budget_during_body(self):
        c,path,p=self.make();c['disk_budget_bytes']=200000
        def hook(phase,d):
            if phase=='after_body':(p/'other-local-growth.bin').write_bytes(b'x'*180000)
        r=Downloader(c,hook).run();self.assertEqual(r['status'],'STOPPED_ERROR');self.assertIn('DISK_BUDGET',r['error'])
        self.assertEqual(r['durable_offset'],4096);self.assertGreater(r['observed_body_bytes'],0);self.assert_prefix(c)
    def test_crash_before_body_record(self):
        c,path,p=self.make(extra_budget=16384);self.run_child(c,p,'after_read','crash')
        d=Downloader(c);s=d.state();self.assertEqual(s['observed_body_bytes'],0);self.assertEqual(s['charged_upper_bytes'],16384)
        self.assertEqual(d.run()['status'],'VERIFIED');self.assert_prefix(c)
    def test_crash_after_body_record_retry_counted(self):
        c,path,p=self.make(extra_budget=16384);self.run_child(c,p,'after_body','crash')
        d=Downloader(c);s=d.state();self.assertGreater(s['observed_body_bytes'],0);self.assertEqual(s['charged_upper_bytes'],16384)
        prior=s['observed_body_bytes'];r=d.run();self.assertEqual(r['status'],'VERIFIED')
        self.assertEqual(r['observed_body_bytes'],len(DATA)-4096+prior);self.assertEqual(r['charged_upper_bytes'],len(DATA)-4096+16384)
        self.assert_prefix(c)
    def test_crash_after_write_refuses_ambiguous_tail(self):
        c,path,p=self.make(extra_budget=16384);self.run_child(c,p,'after_write','crash');n=len(REQUEST_LOG)
        with self.assertRaisesRegex(GuardError,'UNCOMMITTED_DISK_TAIL'):Downloader(c)
        self.assertEqual(len(REQUEST_LOG),n);self.assert_prefix(c)
    def test_crash_after_commit_recovery(self):
        c,path,p=self.make(extra_budget=16384);self.run_child(c,p,'after_commit','crash');n=len(REQUEST_LOG)
        d=Downloader(c);offset=d.state()['durable_offset'];self.assertGreater(offset,4096)
        self.assertEqual(d.run()['status'],'VERIFIED');self.assertTrue(REQUEST_LOG[n]['range'].startswith(f'bytes={offset}-'));self.assert_prefix(c)
    def test_no_retry_when_uncertainty_exhausts_budget(self):
        c,path,p=self.make(mode='short');Downloader(c).run();CASES[path]['mode']='good';n=len(REQUEST_LOG)
        r=Downloader(c).run();self.assertEqual(r['status'],'STOPPED_ERROR');self.assertEqual(len(REQUEST_LOG),n)
    def test_corruption_fails_final_hash(self):
        c,path,p=self.make(mode='corrupt');r=Downloader(c).run();self.assertEqual(r['status'],'STOPPED_ERROR');self.assertIn('FINAL_MD5_MISMATCH',r['error'])
    def test_original_prefix_tamper_refused(self):
        c,path,p=self.make();Path(c['prefix']).write_bytes(b'bad');n=len(REQUEST_LOG)
        with self.assertRaisesRegex(GuardError,'PREFIX_SIZE_CHANGED'):Downloader(c)
        self.assertEqual(len(REQUEST_LOG),n)
    def test_candidate_tamper_refused(self):
        c,path,p=self.make();d=Downloader(c);d.close();f=p/'work/candidate.mp4.partial';f.write_bytes(b'x'*4096);n=len(REQUEST_LOG)
        with self.assertRaisesRegex(GuardError,'CANDIDATE_PREFIX_CHANGED'):Downloader(c)
        self.assertEqual(len(REQUEST_LOG),n);self.assert_prefix(c)
    def test_journal_truncation_refused(self):
        c,path,p=self.make();d=Downloader(c);d.close();j=p/'work/journal.jsonl'
        with j.open('ab') as f:f.write(b'{"interrupted":')
        n=len(REQUEST_LOG)
        with self.assertRaisesRegex(GuardError,'TRUNCATED_JOURNAL'):Downloader(c)
        self.assertEqual(len(REQUEST_LOG),n);self.assert_prefix(c)
    def test_journal_modification_refused(self):
        c,path,p=self.make();d=Downloader(c);d.close();j=p/'work/journal.jsonl';t=j.read_text();j.write_text(t.replace('PREFIX_READY','ALTERED_READY'))
        with self.assertRaisesRegex(GuardError,'JOURNAL_HASH'):Downloader(c)
    def test_concurrent_instance_refused(self):
        c,path,p=self.make();d=Downloader(c);n=len(REQUEST_LOG)
        with self.assertRaisesRegex(GuardError,'WORK_ALREADY_LOCKED'):Downloader(c)
        self.assertEqual(len(REQUEST_LOG),n);d.close();self.assert_prefix(c)
    def test_candidate_links_refused(self):
        for typ in ['symbolic','hard']:
            c,path,p=self.make('link_'+typ);d=Downloader(c);d.close();f=p/'work/candidate.mp4.partial';f.unlink()
            if typ=='symbolic':f.symlink_to(c['prefix'])
            else:os.link(c['prefix'],f)
            n=len(REQUEST_LOG)
            with self.assertRaisesRegex(GuardError,'SYMLINK_CANDIDATE|HARDLINK_CANDIDATE'):Downloader(c)
            self.assertEqual(len(REQUEST_LOG),n);self.assert_prefix(c)
    def test_work_directory_symlink_refused(self):
        c,path,p=self.make();real=p/'actual';real.mkdir();link=p/'link';link.symlink_to(real,target_is_directory=True);c['work_dir']=str(link)
        with self.assertRaisesRegex(GuardError,'SYMLINK_WORK_PATH'):Downloader(c)
    def test_negative_metadata_reserve_refused(self):
        c,path,p=self.make();c['metadata_reserve_bytes']=-1
        with self.assertRaisesRegex(GuardError,'NONNEGATIVE_INTEGER'):Downloader(c)
    def test_remote_disabled(self):
        c,path,p=self.make();c['url']='https://data.bris.ac.uk/datasets/3cqb5b81wk2dc2379fx1mrxh47/Videos/P01/P01-20240202-110250.mp4';n=len(REQUEST_LOG)
        with self.assertRaises(GuardError):Downloader(c)
        c['mode']='approved_single_video';c['approved']=False
        with self.assertRaisesRegex(GuardError,'REMOTE_NOT_APPROVED'):Downloader(c)
        self.assertEqual(len(REQUEST_LOG),n)
    def test_non_loopback_offline_refused(self):
        c,path,p=self.make();c['url']='http://192.0.2.1/file'
        with self.assertRaisesRegex(GuardError,'OFFLINE_NON_LOOPBACK'):Downloader(c)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    summary={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),
             'fixture_bytes':len(DATA),'fixture_sha256':hashlib.sha256(DATA).hexdigest(),'loopback_request_count':len(REQUEST_LOG),
             'external_requests':0,'media_requests':0,'real_video_prefix_used_as_test_payload':False,
             'note':'Fixture-only HTTP at numeric 127.0.0.1; production gate tested by refusal without connection; subtests include 14 real SIGINT/SIGTERM cases.'}
    (BASE/'results'/f'TEST_SUMMARY_{RUN_ID}.json').write_text(json.dumps(summary,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
