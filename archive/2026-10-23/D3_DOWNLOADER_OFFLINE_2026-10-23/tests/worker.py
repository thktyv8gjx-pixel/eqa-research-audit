import json, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from bounded_resume import Downloader

config=json.loads(Path(sys.argv[1]).read_text())
phase=sys.argv[2]
action=sys.argv[3]
marker=Path(sys.argv[4])
fired=False
def hook(current, downloader):
    global fired
    if not fired and current==phase:
        fired=True
        marker.write_text(current)
        if action=='crash':
            os._exit(87)
        deadline=time.monotonic()+8
        while not downloader.stop_requested:
            if time.monotonic()>deadline:
                raise RuntimeError('TEST_SIGNAL_NOT_DELIVERED')
            time.sleep(.005)

d=Downloader(config,hook=hook)
result=d.run()
print(json.dumps(result),flush=True)
