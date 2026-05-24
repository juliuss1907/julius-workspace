# GitHub Internal Breach — Thread Breakdown
## Source: @github, @the_smart_ape, The Hacker News
## Date: 2026-05-20
## Format: 8-tweet thread (English)

---

🚨 Rotate every API key, token, and .env file on your GitHub — **RIGHT NOW** — before it's too late.

GitHub just confirmed an internal breach. Nearly 4,000 internal repos have been exfiltrated. The attacker had a 24-hour head start.

Full breakdown 🧵👇

---

## 2/8 — What happened

▸ One GitHub employee. Auto-update on VS Code extensions enabled.
▸ Extension "NX Console" — 2.2M installs globally — received a malicious update with zero user interaction required.
▸ Malicious version: v18.95.0, pushed using a real contributor account (token stolen beforehand).
▸ GitHub detected abnormal activity a day later and isolated the device.

By then, the attacker had already been inside for 24 hours.

---

## 3/8 — How the payload got in

TeamPCP used the stolen contributor token to push an orphan commit to the nrwl/nx repo:

• 498KB of obfuscated code (package.json + index.js)
• Runs on Bun runtime
• Dev opens workspace → payload executes automatically

No prompt. No warning. Just open VS Code.

---

## 4/8 — What was stolen

The payload scans the entire machine and extracts:

🔑 GitHub tokens
📦 npm tokens → publish malicious packages under the victim's name
☁️ AWS credentials → propagate to other EC2 instances via SSM
🔐 HashiCorp Vault + Kubernetes secrets
🗝️ 1Password + Bitwarden vaults (if unlocked)
🐳 Docker credentials, SSH keys, VPN configs, shell history

Everything. Nothing left behind.

---

## 5/8 — Scale of the breach

• ~3,800–4,000 internal GitHub repos exfiltrated
• Listed for sale at $50K on dark web forums
• Contents: moderation tooling, unreleased security features, production infra scripts, accidentally committed secrets

GitHub rotated critical credentials. But with a 24-hour head start, the attacker already combed through everything.

---

## 6/8 — TeamPCP: This is a campaign, not an isolated incident

Same group. Six months of activity:

• Bitwarden → SAP → TanStack → guardrails-ai → GitHub
• Most recent: durabletask — Microsoft's own official Python package — also compromised
• Campaign name: "Mini Shai-Hulud" — self-replicating malware
• 300GB+ of data + 500K credentials already stolen from prior attacks

---

## 7/8 — Professional-grade, not amateur

The sophistication level makes this clear:

• 3-channel exfil: HTTPS + GitHub API + DNS tunneling
• Backdoor receives commands via GitHub Search API "dead drop"
• Commands signed with RSA-4096
• Self-discovers backup C2 by scanning public GitHub commit messages
• Auto-propagates across EC2 → Kubernetes
• Detects Israel/Iran origin → self-destructs

---

## 8/8 — Action checklist

✅ Rotate every API key, token, .env file — private repos included
✅ Audit your VS Code extensions — remove anything you don't need
✅ Disable auto-update on extensions
✅ Check if any npm/PyPI packages you use appear in the compromise list

Supply chain attacks aren't theoretical anymore.
One just went straight through GitHub — the platform crypto relies on every single day.
