#!/usr/bin/env python3
"""
Hardware metrics sidecar for llama.cpp Monitor.
Provides GPU, CPU, RAM, and disk stats via a simple HTTP endpoint.

Usage:
  pip install flask psutil gputil
  python3 hw-metrics.py --port 8083
"""

import argparse
import json
import subprocess
import psutil
from flask import Flask, jsonify
from flask_cors import cross_origin

app = Flask(__name__)

def get_gpu_info():
    """Get NVIDIA GPU metrics via nvidia-smi."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu,power.draw,power.limit,'
             'fan.speed,clocks.current.graphics,clocks.current.memory,'
             'memory.used,memory.total,memory.free',
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return None
        
        values = [v.strip() for v in result.stdout.strip().split(',')]
        if len(values) < 10:
            return None
        
        return {
            'util': values[0],
            'temp': values[1],
            'power': values[2],
            'power_limit': values[3],
            'fan': values[4],
            'clock_gpu': values[5],
            'clock_mem': values[6],
            'vram_used': values[7],
            'vram_total': values[8],
            'vram_free': values[9]
        }
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

def get_cpu_info():
    """Get CPU metrics."""
    freq = psutil.cpu_freq()
    return {
        'percent': psutil.cpu_percent(interval=0),
        'freq': str(int(freq.current)) if freq else '--',
        'cores': str(psutil.cpu_count(logical=False) or '--'),
        'threads': str(psutil.cpu_count(logical=True) or '--')
    }

def get_ram_info():
    """Get RAM metrics."""
    mem = psutil.virtual_memory()
    return {
        'used': f'{mem.used / (1024**3):.1f}',
        'total': f'{mem.total / (1024**3):.1f}',
        'percent': mem.percent
    }

def get_disk_info():
    """Get disk usage for the root partition."""
    try:
        disk = psutil.disk_usage('/')
        return {'percent': disk.percent}
    except Exception:
        try:
            disk = psutil.disk_usage('C:\\')
            return {'percent': disk.percent}
        except Exception:
            return {'percent': 0}

@app.route('/hw')
def hw():
    """Return all hardware metrics as JSON."""
    data = {
        'cpu': get_cpu_info(),
        'ram': get_ram_info(),
        'disk': get_disk_info()
    }
    
    gpu = get_gpu_info()
    if gpu:
        data['gpu'] = gpu
    
    response = jsonify(data)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/health')
def health():
    response = jsonify({'status': 'ok'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hardware metrics sidecar for llama.cpp Monitor')
    parser.add_argument('--port', type=int, default=8083, help='Port to listen on (default: 8083)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    args = parser.parse_args()
    
    print(f'⚡ hw-metrics sidecar starting on {args.host}:{args.port}')
    print(f'   GPU: {"nvidia-smi found" if get_gpu_info() else "not available (no NVIDIA GPU or nvidia-smi)"}')
    print(f'   Endpoint: http://{args.host}:{args.port}/hw')
    
    app.run(host=args.host, port=args.port, debug=False)
