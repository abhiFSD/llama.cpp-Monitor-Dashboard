# ⚡ llama.cpp Monitor

A single-file, real-time monitoring dashboard for [llama.cpp](https://github.com/ggerganov/llama.cpp) server. Zero dependencies — just one HTML file.

![llama.cpp](https://img.shields.io/badge/llama.cpp-monitor-blue?style=flat-square)
![Zero Deps](https://img.shields.io/badge/dependencies-0-brightgreen)
![Single File](https://img.shields.io/badge/single_file-20KB-orange)

> **Built for production use** — monitoring Qwen 3.5 35B on RTX 5080 at 64 tok/s across 4 parallel slots. Works with any llama.cpp model and hardware.

## Features

- **Real-time tok/s** — per-slot and aggregate generation speed
- **Slot monitoring** — see which slots are active, idle, or queued
- **Live sparkline charts** — generation speed, active slots over time
- **Completed request log** — history of finished generations with timing
- **Server stats** — cumulative tokens, decode calls, prompt/generation time
- **Optional GPU/CPU/RAM monitoring** — via lightweight sidecar script
- **Auto-detects** model name and slot count from llama.cpp metrics
- **Responsive** — works on desktop and mobile
- **Dark theme** — GitHub-inspired dark UI

## Quick Start

### 1. Start llama.cpp with metrics enabled

```bash
llama-server \
  -m your-model.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --metrics \
  --slots
```

> **Required flags:** `--metrics` and `--slots` must be enabled for the dashboard to work.

### 2. Serve the dashboard

**Option A: Use llama.cpp's built-in static file serving**

Copy `monitor.html` to your llama.cpp directory and access it at:
```
http://localhost:8080/monitor.html
```

llama.cpp serves static files from its working directory automatically.

**Option B: Open directly in browser**

```bash
# If llama.cpp is on localhost:8080 (default)
open monitor.html

# If llama.cpp is on a different host/port, use URL params
open "monitor.html?server=http://192.168.1.100:8080"
```

**Option C: Use any static file server**

```bash
python3 -m http.server 3000
# Then open http://localhost:3000/monitor.html?server=http://localhost:8080
```

### 3. (Optional) Hardware monitoring sidecar

For GPU, CPU, RAM, and disk metrics, run the included `hw-metrics.py` sidecar:

```bash
pip install flask psutil gputil
python3 hw-metrics.py --port 8083
```

Then open the dashboard with the `hw` parameter:
```
http://localhost:8080/monitor.html?hw=http://localhost:8083
```

## URL Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `server` | Same origin | llama.cpp server URL (e.g., `http://host:8080`) |
| `hw` | *(none)* | Hardware metrics sidecar URL (e.g., `http://host:8083`) |
| `slots` | Auto-detect | Number of slots (auto-detected from `/slots` endpoint) |
| `poll` | `1000` | Polling interval in milliseconds |

### Examples

```
# Local server, default port
monitor.html

# Remote server
monitor.html?server=http://192.168.1.50:8080

# With hardware metrics
monitor.html?server=http://192.168.1.50:8080&hw=http://192.168.1.50:8083

# Slower polling (every 2 seconds)
monitor.html?poll=2000
```

## Hardware Metrics Sidecar

The optional `hw-metrics.py` script provides system metrics via a simple HTTP endpoint.

### Setup

```bash
# Install dependencies
pip install flask psutil

# For NVIDIA GPU metrics (optional)
pip install gputil

# Run
python3 hw-metrics.py --port 8083
```

### API

**GET `/hw`** — Returns JSON:

```json
{
  "gpu": {
    "util": "45",
    "temp": "62",
    "power": "150.5",
    "power_limit": "250.0",
    "fan": "35",
    "clock_gpu": "1800",
    "clock_mem": "9501",
    "vram_used": "12288",
    "vram_total": "16384",
    "vram_free": "4096"
  },
  "cpu": {
    "percent": 25.3,
    "freq": "3500",
    "cores": "8",
    "threads": "16"
  },
  "ram": {
    "used": "12.4",
    "total": "32.0",
    "percent": 38.8
  },
  "disk": {
    "percent": 55.2
  }
}
```

### Without GPU

If no NVIDIA GPU is detected (or GPUtil isn't installed), the GPU section is automatically hidden. CPU, RAM, and disk metrics still work.

## Requirements

- **llama.cpp** server with `--metrics` and `--slots` flags
- A modern web browser
- *(Optional)* Python 3 with Flask + psutil for hardware metrics

## How It Works

The dashboard polls two llama.cpp endpoints:

- **`/metrics`** — Prometheus-format metrics (tok/s, token counts, timing)
- **`/slots`** — Real-time slot status (active/idle, context size, progress)

Everything runs client-side in the browser. No backend, no build step, no dependencies.

## Screenshots

The dashboard shows:

1. **Top bar** — Aggregate gen tok/s, prompt tok/s, active slots, total tokens
2. **Hardware cards** — GPU util, VRAM, CPU, RAM with live sparklines (if sidecar running)
3. **Slot grid** — Per-slot tok/s with mini charts, progress bars for active generation
4. **Charts** — Generation speed and active slots over time
5. **Request log** — Completed requests with timing breakdown
6. **Server stats** — Cumulative statistics

## License

MIT
