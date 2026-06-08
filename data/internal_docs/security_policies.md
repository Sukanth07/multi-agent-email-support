# Security Policies

## Compliance and certifications
Nimbus maintains **SOC 2 Type II** and **ISO 27001** certifications. Reports are
available to Business and Enterprise customers under NDA via
**Admin → Security → Compliance**. Nimbus supports **GDPR** and **CCPA** data
subject requests.

## Data encryption
- **In transit:** TLS 1.2+ for all connections.
- **At rest:** AES-256 encryption for stored data and backups.

## Data residency
Data is hosted in the United States by default. Enterprise customers may elect
EU (Frankfurt) residency at provisioning time. Residency cannot be changed after
the workspace is created without a migration request.

## Backups and retention
Encrypted backups run daily and are retained for 30 days. Deleted content is
recoverable from trash for 30 days, after which it is permanently purged.
Canceled workspaces retain data for 60 days before deletion.

## Access controls
Internal access to customer data follows least privilege and is logged. Production
access requires MFA and is reviewed quarterly. Customer administrators can review
their own workspace audit log under **Admin → Security → Audit log** (Business and
Enterprise).

## Vulnerability reporting
Report security issues to security@nimbus.com. Nimbus runs a responsible
disclosure program and acknowledges reports within 2 business days. Do not
test against other customers' data.

## Incident response
Confirmed incidents affecting customer data are communicated to affected
workspace administrators without undue delay, consistent with contractual and
regulatory obligations.
