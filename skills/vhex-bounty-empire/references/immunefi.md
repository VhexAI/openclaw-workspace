# Immunefi Bounty Hunter Reference

## Platform Overview
Immunefi is the #1 bug bounty platform for Web3 protocols, bridges, DeFi, NFTs, etc. Protects $180B+ in assets. Pays out millions in bounties.

Key page: [Immunefi Bounties](https://immunefi.com/bounties/)
- Filter: Max Reward > $50,000, Smart Contracts scope.

## High-Value Targets ($50k+ Critical)
- **Critical Smart Contract Vulns**: Often 10% of funds at risk, caps $500k-$15M.
  - Reentrancy attacks (e.g., Omni Network $1.4M loss).
  - Flashloan manipulations.
  - Logic errors draining funds.

Examples:
- LayerZero: $15M cap for Group 1 critical.
- Threshold Network: $500k.
- The Graph: $2.5M historical.

## Top Vulnerabilities to Hunt
1. **Reentrancy**: Non-Reentrant checks missing before external calls.
2. **Access Control**: Unauthorized upgrades/mints.
3. **Oracle Manipulation**.
4. **Sandwich/Front-running**.

## Submission Guidelines
- Detailed PoC (Foundry test ideal).
- Novel, in-scope.
- No public disclosure.

## Tools for Analysis
- Slither (static): `slither . --checklist`
- Mythril: Symbolic execution.
- Echidna: Fuzzing.
- Foundry: Forge test suites.

## Past Top 10 Bugs
See: https://immunefi.com/immunefi-top-10/ (many reentrancy).