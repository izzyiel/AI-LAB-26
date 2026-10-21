import csv, heapq, math, os, time
from collections import deque
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=os.path.join(ROOT,'all_datasets'); OUT=os.path.join(ROOT,'results','lab01');os.makedirs(OUT,exist_ok=True)
coords={}
with open(os.path.join(DATA,'lab01-03_airports.csv'),encoding='utf-8-sig',newline='') as f:
 for row in csv.reader(f):
  if len(row)<8: continue
  code=row[4].strip().upper()
  try: lat,lon=float(row[6]),float(row[7])
  except (ValueError,TypeError): continue
  if len(code)==3 and all(c.isalnum() for c in code) and -90<=lat<=90 and -180<=lon<=180 and code not in coords: coords[code]=(lat,lon)
def hav(a,b):
 lat1,lon1=map(math.radians,coords[a]);lat2,lon2=map(math.radians,coords[b]);dl=lat2-lat1;dn=lon2-lon1
 return 6371*2*math.asin(math.sqrt(math.sin(dl/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dn/2)**2))
graph={c:[] for c in coords}; edges=set(); raw=0
with open(os.path.join(DATA,'lab01-03_routes.csv'),encoding='utf-8-sig',newline='') as f:
 for row in csv.reader(f):
  raw+=1
  if len(row)<5: continue
  a,b=row[2].strip().upper(),row[4].strip().upper()
  if a in coords and b in coords and a!=b: edges.add((a,b))
for a,b in sorted(edges): graph[a].append((b,hav(a,b)))
def run(alg,s,g):
 started=time.perf_counter(); parent={s:None}; expanded=0; maxf=1
 if alg=='BFS' or alg=='DFS':
  fr=deque([s]) if alg=='BFS' else [s]
  while fr:
   u=fr.popleft() if alg=='BFS' else fr.pop()
   if u==g: break
   expanded+=1
   ns=graph.get(u,()) if alg=='BFS' else reversed(graph.get(u,()))
   for v,_ in ns:
    if v not in parent: parent[v]=u; fr.append(v)
   maxf=max(maxf,len(fr))
  found=g in parent and (s==g or expanded>=0)
  # failure/success state: paths are built from discovery even when goal hasn't yet been popped
  found=g in parent
 else:
  fr=[(0.0,0,s,0.0)];best={s:0.0};n=0;done=set()
  while fr:
   _,_,u,cost=heapq.heappop(fr)
   if u in done: continue
   if u==g: break
   done.add(u);expanded+=1
   for v,w in graph.get(u,()):
    nc=cost+w
    if v not in done and nc<best.get(v,float('inf')):
     best[v]=nc;parent[v]=u;n+=1;heapq.heappush(fr,(nc,n,v,nc))
   maxf=max(maxf,len(fr))
  found=g in parent
 path=[]
 if found:
  v=g
  while v is not None:path.append(v);v=parent[v]
  path.reverse()
 pathcost=sum(dict(graph[a])[b] for a,b in zip(path,path[1:])) if path else float('inf')
 return {'found':found,'path':path,'hops':len(path)-1 if path else -1,'path_cost_km':pathcost,'expanded':expanded,'max_frontier':maxf,'runtime_ms':(time.perf_counter()-started)*1000}
queries=list(csv.DictReader(open(os.path.join(ROOT,'all experiments','utils','search_queries.csv'),encoding='utf-8-sig',newline='')))[:3]
rows=[]; paths={}
for q in queries:
 for alg in ('BFS','DFS','UCS'):
  res=run(alg,q['start'],q['goal']);paths[(q['query_id'],alg)]=res['path']
  rows.append({'query_id':q['query_id'],'start':q['start'],'goal':q['goal'],'algorithm':alg,'hops':res['hops'],'path_cost_km':round(res['path_cost_km'],3),'expanded':res['expanded'],'max_frontier':res['max_frontier'],'runtime_ms':round(res['runtime_ms'],3),'path':' -> '.join(res['path'])})
with open(os.path.join(OUT,'metrics.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
with open(os.path.join(OUT,'route_data.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['query_id','algorithm','sequence','airport','latitude','longitude'])
 for (qid,alg),path in paths.items():
  for i,code in enumerate(path):w.writerow([qid,alg,i,code,*coords[code]])
print(f'usable_airports={len(coords)} unique_routes={len(edges)}; wrote {len(rows)} metrics')
for row in rows:print(row['query_id'],row['algorithm'],row['hops'],row['path_cost_km'],row['expanded'])
