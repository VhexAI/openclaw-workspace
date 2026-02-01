#!/bin/bash
# Vhex's Health Check
# Returns issues if any, empty if all clear

issues=""

# Disk space (warn if >85% used)
disk_usage=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$disk_usage" -gt 85 ]; then
  issues="${issues}⚠️ Disk usage at ${disk_usage}%\n"
fi

# Memory (warn if <10% available)
mem_available=$(free | awk '/Mem:/ {printf "%.0f", $7/$2 * 100}')
if [ "$mem_available" -lt 10 ]; then
  issues="${issues}⚠️ Memory low: only ${mem_available}% available\n"
fi

# Load average (warn if > number of CPUs)
cpus=$(nproc)
load=$(cat /proc/loadavg | awk '{print $1}')
if (( $(echo "$load > $cpus" | bc -l) )); then
  issues="${issues}⚠️ High load: ${load} (${cpus} CPUs)\n"
fi

# Failed systemd services
failed=$(systemctl --failed --no-pager --no-legend 2>/dev/null | wc -l)
if [ "$failed" -gt 0 ]; then
  issues="${issues}⚠️ ${failed} failed systemd service(s)\n"
fi

# Auth failures in last hour (security)
if [ -r /var/log/auth.log ]; then
  auth_fails=$(grep -c "authentication failure" /var/log/auth.log 2>/dev/null || echo 0)
  if [ "$auth_fails" -gt 10 ]; then
    issues="${issues}🔐 ${auth_fails} auth failures in log\n"
  fi
fi

# Output
if [ -n "$issues" ]; then
  echo -e "$issues"
else
  echo ""
fi
