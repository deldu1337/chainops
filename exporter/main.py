import os
import time
import threading
import requests
from flask import Flask, Response, jsonify
from prometheus_client import Gauge, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

RPC_URL = os.getenv('RPC_URL', 'http://geth.chainops.svc.cluster.local:8545')
app = Flask(__name__)
up = Gauge('chainops_rpc_up', 'Successful RPC probe (1 or 0)')
height = Gauge('chainops_block_height', 'Latest block height')
latency = Histogram('chainops_rpc_latency_seconds', 'RPC latency seconds', buckets=(.01,.025,.05,.1,.25,.5,1,2,5,10))
errors = Counter('chainops_rpc_errors_total', 'Total failed RPC probes')

def probe():
    start = time.monotonic()
    try:
        resp = requests.post(RPC_URL, json={'jsonrpc':'2.0','method':'eth_blockNumber','params':[],'id':1}, timeout=3)
        resp.raise_for_status()
        body = resp.json()
        if 'error' in body or not isinstance(body.get('result'), str):
            raise ValueError(str(body))
        height.set(int(body['result'],16))
        up.set(1)
    except Exception:
        up.set(0)
        errors.inc()
    finally:
        latency.observe(time.monotonic()-start)

def runner():
    while True:
        probe()
        time.sleep(10)

@app.route('/healthz')
def healthz():
    return jsonify({'exporter':'ok'})

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    threading.Thread(target=runner, daemon=True).start()
    app.run(host='0.0.0.0',port=9108)
