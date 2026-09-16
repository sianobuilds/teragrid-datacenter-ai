# TeraGrid-Ops // Hyperscale Data Center Dispatcher

Autonomous Power Capping & Liquid-Cooling Orchestration Platform for High-Density AI GPU Clusters (H100 / B200).

## Key Features
- **32-Node Thermal Heatmap**: Live tracking of chassis-level hotspot excursions.
- **Asynchronous Task Queue**: Decoupled non-blocking dispatch pipeline for sub-second mitigating controls.
- **Dynamic Power Capping**: Hardware-level RAPL/NVML throttling and BESS energy injection to avert utility demand fines.

## Quick Start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
