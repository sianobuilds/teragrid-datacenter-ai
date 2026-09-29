import os
import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="TeraGrid-Ops SCADA", version="4.2.0")

@app.get("/", response_class=HTMLResponse)
def index():
    file_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/v4/cluster-telemetry")
def api_telemetry():
    return {
        "timestamp": time.time(),
        "site": "US-WEST-POD-04",
        "pue": 1.118,
        "grid_draw_mw": 13.84,
        "bess_soc": 88.4,
        "active_racks": 40
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
