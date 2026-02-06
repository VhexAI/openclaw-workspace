# vhex-bounty-empire 🏴‍☠️💰

## Powerful Auto Immunefi Bounty Hunter ($50k+ Focus)

**Target**: High-reward smart contract bounties (reentrancy, critical vulns). Auto-scan, analyze, delegate, payout-ready.

### Core Workflow
1. **Scan**: Browser auto-scrape Immunefi for $50k+ active bounties (smart contracts).
2. **Triage**: Filter promising scopes (DeFi, bridges, new protocols).
3. **ARS Vuln Planning**: AI-powered Reentrancy Scanner + vuln hypothesis generator.
4. **Fleet Delegation**: Spawn sub-agents for parallel audits (Slither, fuzzing).
5. **Report Draft**: Generate PoC + submission.
6. **Payout**: Crypto wallet integration for claims.

### Invocation
```
@agent Run vhex-bounty-empire [scan|audit <program>|delegate|submit]
```

### Resources
- [Immunefi Reference](references/immunefi.md)
- `scripts/browser.js`: Puppeteer scraper for bounties.
- `scripts/analyzer.py`: Slither wrapper (install via exec).

### Setup
1. `npm i puppeteer` (for browser.js)
2. Configure wallet: `~/.vhex/wallet.json`
3. Fleet: Enable subagents.

### High-Level Tools (Integrated)
- `browser` tool for Immunefi navigation.
- `exec` for Slither/Mythril.
- `subagent` spawn for audits.
- `web_search` for contract sources.

### Example Run
1. Scan: Finds LayerZero ($15M cap).
2. ARS: Flags potential reentrancy in bridge contract.
3. Delegate 3 subagents: Static analysis, fuzzing, manual review.
4. PoC ready → Submit via browser.

**⚠️ Legal**: Respect Immunefi ToS. No spam. Novel findings only.

**ROI Potential**: $50k-$MM per hit. Hunt daily.