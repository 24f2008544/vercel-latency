from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], expose_headers=["*"])

with open(os.path.join(os.path.dirname(__file__), '..', 'q-vercel-latency.json')) as f:
    data = json.load(f)

class Req(BaseModel):
    regions: list
    threshold_ms: float

@app.post("/api/latency")
def latency(req: Req):
    result = []
    for region in req.regions:
        rows = [r for r in data if r["region"] == region]
        latencies = sorted([r["latency_ms"] for r in rows])
        uptimes = [r["uptime_pct"] for r in rows]
        n = len(latencies)
        p95_pos = (n - 1) * 0.95
        lower = int(p95_pos)
        upper = lower + 1
        frac = p95_pos - lower
        if upper >= n:
            p95 = latencies[lower]
        else:
            p95 = latencies[lower] + frac * (latencies[upper] - latencies[lower])
        result.append({
            "region": region,
            "avg_latency": round(sum(latencies)/n, 2),
            "p95_latency": round(p95, 2),
            "avg_uptime": round(sum(uptimes)/n, 2),
            "breaches": sum(1 for l in latencies if l > req.threshold_ms)
        })
    return {"regions": result}

handler = app
