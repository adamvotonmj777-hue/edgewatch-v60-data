import json, time, gzip, os, urllib.request
API='https://api.hyperliquid.xyz/info'
ASSETS=['BTC','ETH','SOL','HYPE','XRP','DOGE','SUI','LINK','AVAX','BNB']
DATA='data'; os.makedirs(DATA,exist_ok=True)
def call(p):
 b=json.dumps(p).encode();
 for i in range(4):
  try:
   r=urllib.request.urlopen(urllib.request.Request(API,b,{'Content-Type':'application/json','User-Agent':'EdgeWatchResearchCollector/1.0'}),timeout=20)
   return json.load(r)
  except Exception:
   if i==3: raise
   time.sleep(min(30,2**i))
def env(f):
 t=time.time()
 try:
  x=f()
  if x is None or x==[]: raise ValueError('empty payload')
  return {'success':True,'payload':x,'fetched_at':t,'error':None}
 except Exception as e: return {'success':False,'payload':None,'fetched_at':None,'attempted_at':t,'error':str(e)}
def main():
 n=time.time(); start=int((n-1200)*1000); out={'schema_version':'edgewatch.v6.public.v1','captured_at':n,'source':'PUBLIC_HYPERLIQUID_READ_ONLY','orders_enabled':False,'metadata':env(lambda:call({'type':'metaAndAssetCtxs'})),'assets':{}}
 for a in ASSETS:
  t=env(lambda a=a:call({'type':'recentTrades','coin':a})); t['payload']=t.get('payload',[])[-300:] if t['success'] else None
  out['assets'][a]={'l2':env(lambda a=a:call({'type':'l2Book','coin':a})),'recent_trades':t,'candles_1m':env(lambda a=a:call({'type':'candleSnapshot','req':{'coin':a,'interval':'1m','startTime':start,'endTime':int(n*1000)}}))}
 fn=os.path.join(DATA,time.strftime('snapshot_%Y%m%d_%H%M%S.json.gz',time.gmtime(n)))
 with gzip.open(fn,'wt',encoding='utf-8') as f: json.dump(out,f,separators=(',',':'))
 print('COLLECTED',fn)
if __name__=='__main__': main()
