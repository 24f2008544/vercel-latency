from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json") as f:
    DATA = json.load(f)


@app.post("/")
async def analytics(payload: dict):

    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for region in regions:

        rows = [r for r in DATA if r["region"] == region]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 3),
            "breaches": sum(
                1 for r in rows
                if r["latency_ms"] > threshold
            )
        }

    return result
