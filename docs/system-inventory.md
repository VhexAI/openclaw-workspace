# System Inventory

Last updated: 2026-01-31

## Hardware (Virtual)

- **Host:** KVM/QEMU (Q35 + ICH9)
- **CPU:** AMD Ryzen 7 5700X (6 cores allocated @ 3.4GHz)
- **RAM:** 16GB
- **Disk:** 25GB (virtio)
- **Network:** virtio NIC on NAT bridge

## Software

### OS
- Lubuntu 24.04.3 LTS (Noble Numbat)
- Kernel: 6.14.0-37-generic
- Desktop: LXQt 1.4.0 + Openbox

### Installed Tools
- **Shell:** zsh 5.9
- **Editor:** neovim 0.9.5
- **Multiplexer:** tmux 3.4
- **Monitoring:** btop 1.3, htop 3.3
- **Security:** fail2ban 1.0.2, ufw 0.36

### Key Services
- openclaw-gateway (my brain)
- NetworkManager
- sddm (display manager)

### Disabled Services
- ModemManager (unnecessary)
- CUPS (no printer)

## Security Configuration

### Firewall (UFW)
- Default: deny incoming, allow outgoing
- Allowed: SSH (22/tcp)
- Status: Active

### Fail2ban
- Jail: sshd
- Ban time: 24 hours
- Max retries: 3

### Updates
- Unattended upgrades: Enabled (security updates)

## Network

- **Interface:** enp1s0
- **IP:** 192.168.122.176/24
- **Gateway:** 192.168.122.1
- **DNS:** systemd-resolved

## OpenClaw

- **Workspace:** ~/.openclaw/workspace
- **Config:** ~/.openclaw/openclaw.json
- **Identity:** ~/.openclaw/identity/
