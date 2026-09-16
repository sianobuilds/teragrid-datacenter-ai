import asyncio
from typing import Optional, List
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="TeraGrid-Ops: Visual Power & Thermal Orchestrator", version="2.0.0")

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TeraGrid-Ops // Hyperscale Data Center Dispatcher</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    body { font-family: 'Inter', sans-serif; }
    .mono { font-family: 'JetBrains Mono', monospace; }
    .rack-glow-red { box-shadow: 0 0 12px rgba(239, 68, 68, 0.6); }
    .rack-glow-blue { box-shadow: 0 0 12px rgba(6, 182, 212, 0.6); }
    .rack-glow-green { box-shadow: 0 0 10px rgba(16, 185, 129, 0.4); }
  </style>
</head>
<body class="bg-[#090D16] text-slate-100 min-h-screen flex flex-col selection:bg-cyan-500 selection:text-black">

  <!-- TOP APP BAR -->
  <header class="border-b border-slate-800 bg-[#0F172A]/80 backdrop-blur-md px-8 py-4 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 text-white flex items-center justify-center text-xl shadow-lg shadow-cyan-500/30">
          <i class="fa-solid fa-server"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-base font-extrabold tracking-wide text-white uppercase">TeraGrid <span class="text-cyan-400">Ops</span></h1>
            <span class="px-2 py-0.5 text-[11px] bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-semibold rounded-full">AI Cluster AP-NE-2</span>
          </div>
          <p class="text-xs text-slate-400">Autonomous Power Capping & Liquid-Cooling Orchestration Platform</p>
        </div>
      </div>

      <!-- SYSTEM STATUS BADGES -->
      <div class="flex items-center space-x-4">
        <div class="hidden sm:flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs mono">
          <span class="text-slate-400">ASYNC QUEUE:</span>
          <span id="queue-status" class="text-emerald-400 font-bold flex items-center gap-1.5">
            <span class="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span> 0 Tasks (Idle)
          </span>
        </div>
        <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs mono">
          <span class="text-slate-400">SYSTEM HEALTH:</span>
          <span id="system-health-badge" class="text-emerald-400 font-bold">100% NOMINAL</span>
        </div>
      </div>
    </div>
  </header>

  <!-- LIVE KPI CARDS -->
  <section class="max-w-7xl mx-auto px-8 py-6 w-full grid grid-cols-1 md:grid-cols-4 gap-4">
    <div class="bg-[#0F172A] border border-slate-800 p-4 rounded-xl shadow-sm">
      <div class="flex justify-between items-center text-slate-400 text-xs mb-1">
        <span>TOTAL POWER DRAW</span>
        <i class="fa-solid fa-bolt text-amber-400"></i>
      </div>
      <div class="flex items-baseline space-x-2">
        <span id="kpi-power" class="text-2xl font-bold mono text-white">88.4</span>
        <span class="text-xs text-slate-400">MW / 120 MW</span>
      </div>
      <div class="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
        <div id="bar-power" class="bg-gradient-to-r from-cyan-500 to-amber-500 h-full rounded-full transition-all duration-700" style="width: 73%"></div>
      </div>
    </div>

    <div class="bg-[#0F172A] border border-slate-800 p-4 rounded-xl shadow-sm">
      <div class="flex justify-between items-center text-slate-400 text-xs mb-1">
        <span>HOTTEST GPU RACK</span>
        <i class="fa-solid fa-temperature-arrow-up text-rose-400"></i>
      </div>
      <div class="flex items-baseline space-x-2">
        <span id="kpi-temp" class="text-2xl font-bold mono text-emerald-400">42.5</span>
        <span class="text-xs text-slate-400">°C (Safe < 65°C)</span>
      </div>
      <div class="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
        <div id="bar-temp" class="bg-emerald-500 h-full rounded-full transition-all duration-700" style="width: 45%"></div>
      </div>
    </div>

    <div class="bg-[#0F172A] border border-slate-800 p-4 rounded-xl shadow-sm">
      <div class="flex justify-between items-center text-slate-400 text-xs mb-1">
        <span>FACILITY PUE EFFICIENCY</span>
        <i class="fa-solid fa-leaf text-emerald-400"></i>
      </div>
      <div class="flex items-baseline space-x-2">
        <span id="kpi-pue" class="text-2xl font-bold mono text-emerald-400">1.08</span>
        <span class="text-xs text-slate-400">Target: < 1.15</span>
      </div>
      <div class="text-[11px] text-slate-400 mt-3 flex items-center gap-1">
        <i class="fa-solid fa-circle-check text-emerald-400"></i> Liquid-cooling loops synchronized
      </div>
    </div>

    <div class="bg-[#0F172A] border border-slate-800 p-4 rounded-xl shadow-sm">
      <div class="flex justify-between items-center text-slate-400 text-xs mb-1">
        <span>BESS BACKUP STORAGE</span>
        <i class="fa-solid fa-car-battery text-purple-400"></i>
      </div>
      <div class="flex items-baseline space-x-2">
        <span id="kpi-bess" class="text-2xl font-bold mono text-white">45.0</span>
        <span class="text-xs text-slate-400">MWh (92%)</span>
      </div>
      <div class="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
        <div class="bg-purple-500 h-full rounded-full" style="width: 92%"></div>
      </div>
    </div>
  </section>

  <!-- WORKSPACE GRID -->
  <main class="max-w-7xl mx-auto px-8 pb-8 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 w-full">
    
    <!-- LEFT: SERVER RACKS HEATMAP & CONTROLS -->
    <div class="lg:col-span-7 flex flex-col space-y-6">
      
      <!-- HEATMAP VIEW -->
      <div class="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div class="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
          <div>
            <h2 class="text-sm font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-cubes-stacked text-cyan-400"></i> 
              32-Node Pod Heatmap (H100 / B200 Clusters)
            </h2>
            <p class="text-xs text-slate-400">Real-time thermal load per individual server rack chassis</p>
          </div>
          <div class="flex items-center space-x-3 text-[11px] mono">
            <span class="flex items-center gap-1"><span class="h-2.5 w-2.5 rounded bg-emerald-500"></span> Cool (&lt;50°C)</span>
            <span class="flex items-center gap-1"><span class="h-2.5 w-2.5 rounded bg-amber-500"></span> Warm (65°C)</span>
            <span class="flex items-center gap-1"><span class="h-2.5 w-2.5 rounded bg-rose-500"></span> Overheat (&gt;80°C)</span>
          </div>
        </div>

        <!-- 32 RACK BLOCKS -->
        <div id="rack-grid" class="grid grid-cols-8 gap-2.5 py-2">
          <!-- Dynamically filled via JS -->
        </div>

        <div class="mt-5 pt-4 border-t border-slate-800 flex justify-between items-center text-xs text-slate-400">
          <span>Active Coolant Manifold: <strong class="text-cyan-400 mono">CDU-Loop #04</strong></span>
          <span>Coolant Flow: <strong id="flow-rate" class="text-white mono">240 L/min</strong></span>
        </div>
      </div>

      <!-- INTERACTIVE SCENARIO CONTROLLER -->
      <div class="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Simulation Scenarios</h3>
        <div class="grid grid-cols-2 gap-4">
          <button onclick="triggerOverload()" 
            class="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 text-left transition-all group">
            <div class="flex items-center justify-between mb-1">
              <span class="font-bold text-rose-400 text-sm flex items-center gap-2">
                <i class="fa-solid fa-triangle-exclamation text-rose-500 animate-bounce"></i> 1. Trigger Spike
              </span>
              <span class="text-[10px] bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded font-mono">CRITICAL</span>
            </div>
            <p class="text-xs text-slate-400">Simulate 405B LLM Checkpoint sync. Racks spike to 84°C, power hits 118 MW (Contract Breach).</p>
          </button>

          <button onclick="executeMitigation()" 
            class="p-4 rounded-xl border border-cyan-500/30 bg-cyan-500/10 hover:bg-cyan-500/20 text-left transition-all group">
            <div class="flex items-center justify-between mb-1">
              <span class="font-bold text-cyan-400 text-sm flex items-center gap-2">
                <i class="fa-solid fa-wand-magic-sparkles text-cyan-400"></i> 2. Auto-Mitigate
              </span>
              <span class="text-[10px] bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded font-mono">AI DISPATCH</span>
            </div>
            <p class="text-xs text-slate-400">Queue async task: Cap GPU power to 580W, discharge BESS, step-up CDU coolant +30%.</p>
          </button>
        </div>
      </div>

    </div>

    <!-- RIGHT: ASYNC QUEUE LOGS & DISPATCH DIRECTIVE -->
    <div class="lg:col-span-5 flex flex-col space-y-6">
      <div class="bg-[#0F172A] border border-slate-800 rounded-2xl p-6 shadow-xl flex-1 flex flex-col">
        <div class="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
          <h2 class="text-sm font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-network-wired text-cyan-400"></i>
            Async Queue & Action Directives
          </h2>
          <span id="log-time" class="text-xs text-slate-500 mono">READY</span>
        </div>

        <!-- TIMELINE LOGS -->
        <div id="action-terminal" class="flex-1 bg-black/60 rounded-xl border border-slate-800/80 p-4 mono text-xs text-slate-300 overflow-y-auto space-y-3 leading-relaxed">
          <div class="text-slate-500 text-center py-16">
            <i class="fa-solid fa-satellite-dish text-2xl mb-2 opacity-40"></i><br/>
            Waiting for simulation trigger...<br/>
            <span class="text-[10px]">Click [1. Trigger Spike] to see how the system handles critical load.</span>
          </div>
        </div>

        <!-- BOTTOM METRIC FOOTER -->
        <div class="mt-4 pt-3 border-t border-slate-800 flex justify-between text-xs text-slate-400 mono">
          <span>Worker Threads: <strong class="text-white">8 Active</strong></span>
          <span>Dispatch Protocol: <strong class="text-cyan-400">BACnet / Redfish</strong></span>
        </div>
      </div>
    </div>

  </main>

  <script>
    // 32 Racks State
    let racks = Array(32).fill(42);

    function renderRacks() {
      const grid = document.getElementById('rack-grid');
      grid.innerHTML = '';
      racks.forEach((temp, i) => {
        let colorClass = 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400';
        let dotClass = 'bg-emerald-500';
        if (temp > 75) {
          colorClass = 'bg-rose-500/30 border-rose-500 text-rose-400 rack-glow-red animate-pulse';
          dotClass = 'bg-rose-500';
        } else if (temp > 60) {
          colorClass = 'bg-amber-500/20 border-amber-500/50 text-amber-400';
          dotClass = 'bg-amber-500';
        }

        const div = document.createElement('div');
        div.className = `border rounded-lg p-2 flex flex-col items-center justify-center transition-all duration-500 ${colorClass}`;
        div.innerHTML = `
          <span class="text-[9px] text-slate-400 mono">R-${String(i+1).padStart(2,'0')}</span>
          <span class="text-xs font-bold mono mt-0.5">${temp.toFixed(0)}°</span>
        `;
        grid.appendChild(div);
      });
    }

    renderRacks();

    function triggerOverload() {
      // Overheat racks 12 to 24
      racks = racks.map((_, i) => (i >= 11 && i <= 23) ? 84 + Math.random()*4 : 45 + Math.random()*5);
      renderRacks();

      document.getElementById('kpi-power').innerText = "118.6";
      document.getElementById('bar-power').style.width = "98%";
      document.getElementById('bar-power').className = "bg-rose-500 h-full rounded-full transition-all duration-700";

      document.getElementById('kpi-temp').innerText = "86.4";
      document.getElementById('kpi-temp').className = "text-2xl font-bold mono text-rose-400 animate-pulse";
      document.getElementById('bar-temp').style.width = "92%";
      document.getElementById('bar-temp').className = "bg-rose-500 h-full rounded-full transition-all duration-700";

      document.getElementById('kpi-pue').innerText = "1.28";
      document.getElementById('kpi-pue').className = "text-2xl font-bold mono text-rose-400";

      document.getElementById('system-health-badge').innerText = "CRITICAL EXCURSION";
      document.getElementById('system-health-badge').className = "text-rose-400 font-bold animate-pulse";

      document.getElementById('flow-rate').innerText = "240 L/min (Choked)";
      document.getElementById('flow-rate').className = "text-rose-400 mono";

      document.getElementById('action-terminal').innerHTML = `
        <div class="text-rose-400 font-bold mb-2">🚨 [ALERT] CRITICAL THERMAL & POWER SPIKE DETECTED</div>
        <div class="text-slate-300">
          • Facility Draw: <span class="text-rose-400 font-bold">118.6 MW</span> (Substation Limit: 110 MW)<br/>
          • Peak Hotspot: Racks R-12 ~ R-24 at <span class="text-rose-400 font-bold">86.4°C</span><br/>
          • Penalty Hazard: $42,500/hr utility demand fine active.
        </div>
        <div class="mt-3 p-2 bg-rose-500/10 border border-rose-500/30 rounded text-rose-300">
          Action Required: Click [2. Auto-Mitigate] to dispatch asynchronous throttling job to the worker queue.
        </div>
      `;
    }

    async function executeMitigation() {
      const qStatus = document.getElementById('queue-status');
      qStatus.innerHTML = '<span class="h-2 w-2 rounded-full bg-cyan-400 animate-ping"></span> 1 Task Queued (Processing)';
      qStatus.className = 'text-cyan-400 font-bold flex items-center gap-1.5';

      const terminal = document.getElementById('action-terminal');
      terminal.innerHTML = `
        <div class="text-cyan-400 font-bold">> Enqueuing Job #JOB-8842 into Celery/Redis Queue...</div>
        <div class="text-slate-400">> Worker #3 picked up task: Executing MILP Solver & BMC dispatch...</div>
      `;

      try {
        const response = await fetch('/api/v1/grid/dispatch', { method: 'POST' });
        const data = await response.json();

        setTimeout(() => {
          // Gradual Cooling visual
          racks = racks.map(() => 42 + Math.random()*3);
          renderRacks();

          document.getElementById('kpi-power').innerText = "104.2";
          document.getElementById('bar-power').style.width = "82%";
          document.getElementById('bar-power').className = "bg-gradient-to-r from-cyan-500 to-emerald-500 h-full rounded-full transition-all duration-700";

          document.getElementById('kpi-temp').innerText = "43.1";
          document.getElementById('kpi-temp').className = "text-2xl font-bold mono text-emerald-400";
          document.getElementById('bar-temp').style.width = "46%";
          document.getElementById('bar-temp').className = "bg-emerald-500 h-full rounded-full transition-all duration-700";

          document.getElementById('kpi-pue').innerText = "1.07";
          document.getElementById('kpi-pue').className = "text-2xl font-bold mono text-emerald-400";

          document.getElementById('system-health-badge').innerText = "100% STABILIZED";
          document.getElementById('system-health-badge').className = "text-emerald-400 font-bold";

          document.getElementById('flow-rate').innerText = "380 L/min (+58%)";
          document.getElementById('flow-rate').className = "text-cyan-400 mono font-bold";

          qStatus.innerHTML = '<span class="h-2 w-2 rounded-full bg-emerald-400"></span> 0 Tasks (Completed)';
          qStatus.className = 'text-emerald-400 font-bold flex items-center gap-1.5';

          terminal.innerHTML = `
            <div class="text-emerald-400 font-bold mb-2">✅ [ASYNC WORKER FINISHED] CLUSTER RESTORED TO SAFETY</div>
            <div class="space-y-1.5 text-slate-300">
              <div>• <strong>GPU Power Cap:</strong> Throttled 700W ➔ 580W via NVML (-6.4 MW).</div>
              <div>• <strong>BESS Battery:</strong> Discharged 4.2 MW into grid feeder.</div>
              <div>• <strong>Coolant Valve:</strong> Stepped up flow to 380 L/min via BACnet.</div>
              <div class="text-cyan-400 font-bold pt-1">• Result: Utility draw safe at 104.2 MW | Racks cooled to 43°C.</div>
            </div>
          `;
        }, 1200);

      } catch (e) {
        terminal.innerHTML = `<div class="text-rose-400">> Task Failure: ${e.message}</div>`;
      }
    }
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_console():
    return HTMLResponse(content=DASHBOARD_HTML)

@app.post("/api/v1/grid/dispatch")
async def execute_dispatch():
    await asyncio.sleep(0.4) # Simulate async optimization calculation
    return {"status": "SUCCESS", "message": "Cluster stabilized"}
