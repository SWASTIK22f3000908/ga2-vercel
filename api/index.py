from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json") as f:
    telemetry = json.load(f)

@app.post("/")
async def analytics(body: dict):
    regions = body["regions"]
    threshold = body["threshold_ms"]

    result = {}

    for region in regions:
        region_data = [r for r in telemetry if r["region"] == region]

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]

        if not latencies:
            continue

        avg_latency = sum(latencies) / len(latencies)

        sorted_lat = sorted(latencies)
        index_95 = math.ceil(0.95 * len(sorted_lat)) - 1
        p95_latency = sorted_lat[index_95]

        avg_uptime = sum(uptimes) / len(uptimes)

        breaches = len([l for l in latencies if l > threshold])

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return result
