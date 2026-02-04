#!/bin/bash
# List Tailscale fleet nodes as JSON

tailscale status --json | jq '[.[].{name: .SelfReportedName, ip: .TailscaleIPs[0] // empty, status: .Status, os: .OS}]'
