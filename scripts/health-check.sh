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

# Fail2ban bans (security)
f2b_bans=$(fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | awk '{print $NF}')
f2b_bans=${f2b_bans:-0}
if [ "$f2b_bans" -gt 0 ] 2>/dev/null; then
  issues="${issues}🔐 ${f2b_bans} IP(s) currently banned by fail2ban\n"
fi

# Firewall status (check via systemctl since ufw status needs sudo)
ufw_active=$(systemctl is-active ufw 2>/dev/null)
if [[ "$ufw_active" != "active" ]]; then
  issues="${issues}🛡️ Firewall not active!\n"
fi

# Output
if [ -n "$issues" ]; then
  echo -e "$issues"
else
  echo ""
fi
