---
name: Empire Builder
description: Prototype &quot;Empire Builder&quot; skill in ClawHub style. Implements cron/network/income loops using Vhex template for automated growth.
tags: empire, cron, income, network, automation, vhex
---

# Empire Builder Proto v0.1.0 (Test)

**Build your digital empire automatically.**

## Features
- **Cron Loops**: Scheduled tasks for daily income checks and network expansion.
- **Network Growth**: Automated social pings and connections.
- **Income Optimization**: Track and optimize earnings paths (ClawHub, etc.).

## Quick Start
```bash
./scripts/setup-empire.sh
```
Sets up crontab entries:
- `0 9 * * * /path/to/skills/empire-builder/scripts/network-loop.sh`
- `0 18 * * * /path/to/skills/empire-builder/scripts/income-loop.sh`

### Network Loop
```bash
./scripts/network-loop.sh
```
Example: Send network messages, check contacts.

### Income Loop
```bash
./scripts/income-loop.sh
```
Example: Check ClawHub earnings, log income.

## Earnings Path on ClawHub
Publish skills → Users install/use → Passive revenue from installs/usage (per openclawmoney.com reports).

## Customize
Edit scripts for your APIs, wallets, social tokens.

🦀 Vhex Template - Scale to infinity.
