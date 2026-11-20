# Security Policy

## Supported Versions

Only the current minor release series of `stock-fetcher` receives active security updates.

| Version | Supported |
| :--- | :--- |
| 0.3.x / 0.4.x | Yes |
| < 0.3.0 | No |

## Reporting a Vulnerability

Security issues affecting `stock-fetcher` (including API credential handling, TLS certificate verification failures, or dependency vulnerabilities) must not be reported via public GitHub issues.

### Private Disclosure Process

1. Open a draft security advisory via [GitHub Security Advisories](https://github.com/AtaCanYmc/stock-fetcher/security/advisories/new).
2. If GitHub Advisories is inaccessible, email the maintainer directly at `atacanymc@gmail.com` with the subject line `[SECURITY] stock-fetcher vulnerability report`.

### Report Requirements

Please include the following technical details in your report:
- Component or module affected (`src/stock_fetcher/...`).
- Description of the attack vector or failure mode.
- Step-by-step reproduction commands or minimal script.
- Potential blast radius or data exposure risk.

### Response SLA

- **Initial Response**: Within 48 hours of receipt.
- **Triage & Assessment**: Within 5 business days.
- **Patch Release**: Scheduled based on CVSS severity rating. Critical advisories receive hotfix releases within 7 business days of confirmation.
