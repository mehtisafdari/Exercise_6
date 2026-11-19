import threading,time,csv
from pathlib import Path
class Dekker:
 def __init__(s): s.flag=[False,False]; s.turn=0
 def acquire(s,i):
  j=1-i; s.flag[i]=True
  while s.flag[j]:
   if s.turn==j:
    s.flag[i]=False
    while s.turn==j: time.sleep(0)
    s.flag[i]=True
 def release(s,i): s.turn=1-i; s.flag[i]=False
class Peterson:
 def __init__(s): s.flag=[False,False]; s.turn=0
 def acquire(s,i):
  j=1-i; s.flag[i]=True; s.turn=j
  while s.flag[j] and s.turn==j: time.sleep(0)
 def release(s,i): s.flag[i]=False
class Semaphore:
 def __init__(s): s.x=threading.Semaphore(1)
 def acquire(s,i=None): s.x.acquire()
 def release(s,i=None): s.x.release()
class Monitor:
 def __init__(s): s.cv=threading.Condition(); s.busy=False
 def acquire(s,i=None):
  with s.cv:
   while s.busy: s.cv.wait()
   s.busy=True
 def release(s,i=None):
  with s.cv: s.busy=False; s.cv.notify()
def run(cls,label):
 lock=cls(); cv=threading.Condition(); nxt=[0]; active=[0]; bad=[]
 jobs=[("P1",.06),("P2",.06),("P3",.06),("P4",.06)]; rows=[]
 def work(k,name,d):
  with cv:
   while k!=nxt[0]: cv.wait()
  i=k%2; lock.acquire(i); st=time.perf_counter(); active[0]+=1
  if active[0]>1: bad.append(name)
  time.sleep(d); active[0]-=1; en=time.perf_counter(); lock.release(i)
  with cv: nxt[0]+=1; cv.notify_all()
  rows.append((k,name,d,st,en))
 ts=[threading.Thread(target=work,args=(k,n,d)) for k,(n,d) in enumerate(jobs)]
 for t in ts:t.start()
 for t in ts:t.join()
 rows.sort(); origin=rows[0][3]; out=[]; elapsed=0
 for k,n,d,st,en in rows:
  out.append({"method":label,"process":n,"fcfs_order":k+1,"burst":d,
   "waiting":round(max(0,st-origin-elapsed),4),"turnaround":round(en-origin,4)})
  elapsed+=d
 return out,bool(bad)
def main():
 all=[]
 for name,cls in [("Dekker",Dekker),("Peterson",Peterson),("Semaphore",Semaphore),("Monitor",Monitor)]:
  rows,bad=run(cls,name); all+=rows
  print(name, "PASS" if not bad else "FAIL", "FCFS:", " -> ".join(r["process"] for r in rows))
  for r in rows: print(r)
 Path("results").mkdir(exist_ok=True)
 with open("results/comparison.csv","w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=all[0].keys()); w.writeheader(); w.writerows(all)
if __name__=="__main__": main()
