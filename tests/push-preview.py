#!/usr/bin/env python3
"""Run the actual zsh CLI on fake keys/files. Never invokes macOS Keychain.
A Python audit hook aborts preview if a file mutation is attempted. All external
commands are shims, and complete before/after snapshots catch shell mutations.
"""
import os,sys,json,subprocess,tempfile,hashlib
from pathlib import Path
COO=Path(__file__).resolve().parents[1]/'coo'
CAN='sk-ant-api03-FAKE_CANONICAL_VALUE_FOR_TEST_ONLY_0123456789'
OLD='sk-ant-api03-FAKE_OLD_VALUE_FOR_TEST_ONLY_9876543210'
def snapshot(root):
 return {str(p.relative_to(root)):(p.read_bytes(),p.stat().st_mtime_ns,p.stat().st_mode) for p in root.rglob('*') if p.is_file()}
with tempfile.TemporaryDirectory(prefix='pigeon-preview-') as tmp:
 root=Path(tmp);home=root/'home';home.mkdir();bin=root/'bin';bin.mkdir();audit=root/'audit';audit.mkdir();calls=root/'calls'
 (audit/'sitecustomize.py').write_text('''import os,sys
if os.environ.get('PREVIEW_AUDIT')=='1':
 def guard(event,args):
  if event=='open' and (args[2] & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):
   raise RuntimeError('AUDIT BLOCK: write attempted in preview')
  if event in ('os.remove','os.rename','os.mkdir','os.rmdir','os.chmod','os.truncate'):
   raise RuntimeError('AUDIT BLOCK: mutation attempted in preview')
 sys.addaudithook(guard)
''')
 (bin/'python3').write_text('#!/bin/sh\nexec '+sys.executable+' "$@"\n')
 (bin/'security').write_text('''#!/bin/sh
printf '%s\n' "$1" >> "$FAKE_CALLS"
if [ "$1" = find-generic-password ]; then printf '%s' "$FAKE_CAN"; exit 0; fi
exit 99
''')
 for name in ['curl','npx','vercel','pbpaste','open']:
  (bin/name).write_text('#!/bin/sh\nprintf "FORBIDDEN '+name+'\\n" >> "$FAKE_CALLS"\nexit 99\n')
 for p in bin.iterdir():p.chmod(0o755)
 env={'HOME':str(home),'XDG_DATA_HOME':str(home/'data'),'PATH':str(bin)+':/usr/bin:/bin:/usr/sbin:/sbin','FAKE_CAN':CAN,'FAKE_CALLS':str(calls),'PYTHONPATH':str(audit),'PYTHONDONTWRITEBYTECODE':'1','PREVIEW_AUDIT':'1'}
 # Prove the mutation trap actually fires before trusting a green dry-run.
 red=subprocess.run([str(bin/'python3'),'-c',"open('"+str(root/'must-not-exist')+"','w').write('x')"],env=env,capture_output=True,text=True)
 assert red.returncode and 'AUDIT BLOCK' in red.stderr and not (root/'must-not-exist').exists()
 def run(*args,write=False):
  e={**env,'PREVIEW_AUDIT':'0' if write else '1'}
  p=subprocess.run(['/bin/zsh',str(COO),'push',*args],env=e,capture_output=True,text=True)
  assert p.returncode==0,(p.returncode,p.stdout,p.stderr)
  assert CAN not in p.stdout+p.stderr and OLD not in p.stdout+p.stderr
  assert 'FORBIDDEN' not in calls.read_text()
  assert set(calls.read_text().splitlines())=={'find-generic-password'}
  return p.stdout
 # No setup files are created when a preview starts with no state.
 before=snapshot(home);out=run('anthropic/API_KEY','--dry-run');assert snapshot(home)==before and not (home/'data').exists();assert 'no sites declared' in out
 nest=home/'data/pigeon';nest.mkdir(parents=True);(nest/'index').write_text('anthropic/API_KEY\n')
 a=home/'app.env';a.write_text('ANTHROPIC_API_KEY='+OLD+'\nUNCHANGED=yes\n');a.chmod(0o600)
 same=home/'same.env';same.write_text('ANTHROPIC_API_KEY='+CAN+'\n')
 absent=home/'missing.env';other=home/'other-project.env';other.write_text('ANTHROPIC_API_KEY='+OLD+'\n')
 sites={'anthropic/API_KEY':[{'path':str(a),'var':'ANTHROPIC_API_KEY'},{'path':str(a),'var':'SECOND_KEY'},{'path':str(a),'var':'ANTHROPIC_API_KEY'},{'path':str(same),'var':'ANTHROPIC_API_KEY'},{'path':str(absent),'var':'API_KEY'},{'type':'vercel','cwd':str(home),'var':'ANTHROPIC_API_KEY','env':'production'}]}
 sf=nest/'sites.json';sf.write_text(json.dumps(sites));before=snapshot(home)
 out=run('--dry-run','anthropic/API_KEY','--redeploy');assert snapshot(home)==before;assert '2 planned changes' in out and '2 already-canonical' in out and '1 unreachable' in out;assert 'would set; remote value not checked' in out;assert not absent.exists();assert not list(home.glob('*.bak-pigeon'))
 # Actual write uses the same planner. Remote targets are removed from the fake
 # config first: this acceptance never permits a Vercel invocation.
 sites['anthropic/API_KEY']=[x for x in sites['anthropic/API_KEY'] if x.get('type')!='vercel'];sf.write_text(json.dumps(sites));original=a.read_bytes();run('anthropic/API_KEY',write=True)
 assert a.read_text()=='ANTHROPIC_API_KEY='+CAN+'\nUNCHANGED=yes\nSECOND_KEY='+CAN+'\n';assert Path(str(a)+'.bak-pigeon').read_bytes()==original;assert (a.stat().st_mode&0o777)==0o600;assert other.read_text()=='ANTHROPIC_API_KEY='+OLD+'\n';assert not absent.exists()
 before=snapshot(home);out=run('anthropic/API_KEY','--dry-run');assert snapshot(home)==before;assert '0 planned changes' in out
 print('PASS: mutation trap fired; empty-state preview; changed/same/missing/duplicate variables; no backups/writes/remote/redeploy; no key values; real write matches plan; pristine backup; undeclared project untouched; repeat preview zero changes.')
