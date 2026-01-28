from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import statistics
import os

app = FastAPI()

import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")

with open(DATA_PATH, "r") as f:
    data = json.load(f)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    regions: List[str]
    threshold_ms: int

@app.post("/api")
def analyze_latency(body: RequestBody):
    result = {}

    for region in body.regions:
        region_data = [d for d in data if d["region"] == region]

        if not region_data:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0,
                "error": "No data for region"
            }
            continue

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime_pct"] for d in region_data]
        breaches = sum(
            1 for d in region_data if d["latency_ms"] > body.threshold_ms
        )

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": (
                statistics.quantiles(latencies, n=20)[18]
                if len(latencies) >= 20
                else max(latencies)
            ),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": breaches,
        }

    return result
   
   