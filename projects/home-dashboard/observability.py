#!/usr/bin/env python3
# Vhex Home Dashboard v0.1 - Powered by agent-observability-dashboard skill

import psutil
import subprocess
import time
from flask import Flask, render_template_string

app = Flask(__name__)

def get_health():
    disk = psutil.disk_usage('/')
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent()
    
    # Fail2ban
    try:
        bans = subprocess.run(['fail2ban-client', 'status', 'sshd'], capture_output=True, text=True).stdout
        banned = bans.count('banned')
    except:
        banned = 0
    
    # UFW
    try:
        ufw = subprocess.run(['ufw', 'status'], capture_output=True, text=True).stdout
        firewall = 'active' if 'Status: active' in ufw else 'inactive'
    except:
        firewall = 'unknown'
    
    return {
        'cpu': cpu,
        'mem_used': mem.percent,
        'disk_used': disk.percent,
        'banned_ips': banned,
        'firewall': firewall,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

@app.route('/')
def dashboard():
    status = get_health()
    html = '''
    <h1>Vhex Home Dashboard 👁️</h1>
    <table border="1">
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>CPU</td><td>{{ status.cpu }}%</td></tr>
        <tr><td>Memory</td><td>{{ status.mem_used }}%</td></tr>
        <tr><td>Disk</td><td>{{ status.disk_used }}%</td></tr>
        <tr><td>Banned IPs</td><td>{{ status.banned_ips }}</td></tr>
        <tr><td>Firewall</td><td>{{ status.firewall }}</td></tr>
        <tr><td>Updated</td><td>{{ status.timestamp }}</td></tr>
    </table>
    '''
    return render_template_string(html, status=status)

if __name__ == '__main__':
    print("Dashboard running at http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
