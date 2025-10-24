## Task 3.7: Define Automated Backup Requirements

**CIP Standard**: CIP-009 R2 (Recovery Plans for BES Cyber Systems)
**Estimated Time**: 3-4 hours
**Priority**: LOW

### Research Objectives

1. Document CIP-009 backup requirements (recovery plan, backup testing)
2. Define MISP backup schedule and retention
3. Research MISP backup methods (database, files, configurations)
4. Define disaster recovery procedures

### Deliverables

#### 1. CIP-009 Compliance Assessment

**Template**: Copy and complete this assessment

```markdown
# CIP-009 R2 - BES Cyber System Recovery Plans

**Requirement**: Backup and recovery plan for BES Cyber Systems

**MISP as a BES Cyber Asset**:
- [ ] MISP is classified as a BES Cyber Asset (if used for incident response on BES systems)
- [ ] MISP is NOT a BES Cyber Asset (IT system only)

**If MISP is a BES Cyber Asset, CIP-009 requires**:
- Documented backup procedure
- Backup frequency (at least annually, but daily/weekly recommended)
- Backup retention policy
- Recovery procedure testing (at least once every 15 months)
- Backup storage location (off-site or alternate location)

**Current MISP Backup Status**:
- **Are MISP backups currently performed?**: [ ] Yes  [ ] No
- **If yes, backup frequency**: [ ] Daily  [ ] Weekly  [ ] Monthly  [ ] Other: _______
- **Backup retention**: _______ days/months
- **Backup storage location**: _______________________________
- **Last backup test date**: _______________________________
```

#### 2. MISP Backup Design

Document comprehensive MISP backup strategy:

```markdown
# MISP Backup and Recovery Design

## What to Backup

### 1. MISP Database (PostgreSQL or MySQL)
**Contains**:
- All events, attributes, tags
- User accounts and roles
- Organization data
- Correlation data

**Criticality**: HIGHEST - Contains all threat intelligence

**Backup method**:
```bash
# PostgreSQL backup (if using PostgreSQL)
docker exec misp-db-1 pg_dump -U misp misp > /backup/misp-db-$(date +%Y%m%d).sql

# MySQL backup (if using MySQL)
docker exec misp-db-1 mysqldump -u misp -p misp > /backup/misp-db-$(date +%Y%m%d).sql
```

### 2. MISP Configuration Files
**Contains**:
- `/opt/misp/.env` - Environment variables (BASE_URL, ADMIN_EMAIL, etc.)
- `/opt/misp/docker-compose.yml` - Container orchestration config
- `/opt/misp/PASSWORDS.txt` - Admin credentials (store securely!)

**Criticality**: HIGH - Required to restore MISP with same settings

**Backup method**:
```bash
tar -czf /backup/misp-config-$(date +%Y%m%d).tar.gz /opt/misp/.env /opt/misp/docker-compose.yml /opt/misp/PASSWORDS.txt
```

### 3. MISP Uploaded Files
**Contains**:
- `/opt/misp/files/` - Malware samples, PDFs, screenshots uploaded to events
- Potentially contains BCSI (CIP-011 sensitive data)

**Criticality**: MEDIUM - Can be re-uploaded if lost, but time-consuming

**Backup method**:
```bash
tar -czf /backup/misp-files-$(date +%Y%m%d).tar.gz /opt/misp/files/
```

### 4. MISP Custom Scripts and Integrations
**Contains**:
- Custom automation scripts (Task 3.1-3.6)
- PyMISP scripts for SIEM, firewall, ICS tool integration
- Cron jobs

**Criticality**: MEDIUM - Can be recreated, but development effort required

**Backup method**:
```bash
tar -czf /backup/misp-scripts-$(date +%Y%m%d).tar.gz /opt/misp/scripts/ /etc/cron.d/misp*
```

## Automated Backup Script

```bash
#!/bin/bash
# /opt/misp/scripts/misp-backup.sh
# Automated daily MISP backup for CIP-009 compliance

BACKUP_DIR="/mnt/backup/misp"
RETENTION_DAYS=90
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

echo "Starting MISP backup - $(date)"

# 1. Backup MySQL database
echo "Backing up database..."
docker exec misp-db-1 mysqldump -u misp -p'PASSWORD_FROM_ENV' misp | gzip > $BACKUP_DIR/misp-db-$DATE.sql.gz

# 2. Backup configuration files
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/misp-config-$DATE.tar.gz /opt/misp/.env /opt/misp/docker-compose.yml /opt/misp/PASSWORDS.txt

# 3. Backup uploaded files
echo "Backing up uploaded files..."
tar -czf $BACKUP_DIR/misp-files-$DATE.tar.gz /opt/misp/files/

# 4. Backup custom scripts
echo "Backing up scripts..."
tar -czf $BACKUP_DIR/misp-scripts-$DATE.tar.gz /opt/misp/scripts/

# 5. Generate backup manifest (for verification)
echo "Generating manifest..."
cat > $BACKUP_DIR/misp-manifest-$DATE.txt <<EOF
MISP Backup - $DATE
-------------------
Database: $(ls -lh $BACKUP_DIR/misp-db-$DATE.sql.gz)
Config: $(ls -lh $BACKUP_DIR/misp-config-$DATE.tar.gz)
Files: $(ls -lh $BACKUP_DIR/misp-files-$DATE.tar.gz)
Scripts: $(ls -lh $BACKUP_DIR/misp-scripts-$DATE.tar.gz)
EOF

# 6. Copy to off-site backup location (CIP-009 requirement)
echo "Copying to off-site location..."
rsync -avz $BACKUP_DIR/ backup-server.company.local:/backup/misp/

# 7. Cleanup old backups (retain 90 days)
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "misp-*" -mtime +$RETENTION_DAYS -delete

echo "MISP backup completed - $(date)"
```

**Deployment**:
```bash
chmod +x /opt/misp/scripts/misp-backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /opt/misp/scripts/misp-backup.sh >> /var/log/misp-backup.log 2>&1" | crontab -
```

## Recovery Procedures

### Scenario 1: Full MISP Server Failure

**Recovery Steps**:

1. **Provision new server** (same OS, same IP if possible)

2. **Install Docker and Docker Compose**:
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# Install Docker Compose
apt-get install -y docker-compose
```

3. **Restore MISP configuration files**:
```bash
# Copy backup to new server
rsync -avz backup-server.company.local:/backup/misp/misp-config-YYYYMMDD.tar.gz /tmp/

# Extract configuration
cd /opt
tar -xzf /tmp/misp-config-YYYYMMDD.tar.gz
```

4. **Deploy MISP containers**:
```bash
cd /opt/misp
docker-compose up -d
```

5. **Wait for containers to start** (check with `docker ps`)

6. **Restore database**:
```bash
# Copy database backup
rsync -avz backup-server.company.local:/backup/misp/misp-db-YYYYMMDD.sql.gz /tmp/

# Restore database
gunzip /tmp/misp-db-YYYYMMDD.sql.gz
cat /tmp/misp-db-YYYYMMDD.sql | docker exec -i misp-db-1 mysql -u misp -p'PASSWORD' misp
```

7. **Restore uploaded files**:
```bash
rsync -avz backup-server.company.local:/backup/misp/misp-files-YYYYMMDD.tar.gz /tmp/
tar -xzf /tmp/misp-files-YYYYMMDD.tar.gz -C /opt/misp/
```

8. **Restore custom scripts**:
```bash
rsync -avz backup-server.company.local:/backup/misp/misp-scripts-YYYYMMDD.tar.gz /tmp/
tar -xzf /tmp/misp-scripts-YYYYMMDD.tar.gz -C /
```

9. **Restart MISP**:
```bash
cd /opt/misp
docker-compose restart
```

10. **Verify recovery**:
- Access MISP web interface: https://misp-test.lan
- Login with admin credentials
- Check event count matches pre-disaster count
- Verify API access works
- Test integrations (SIEM, firewall, ICS tool)

**Recovery Time Objective (RTO)**: 4-8 hours
**Recovery Point Objective (RPO)**: 24 hours (based on daily backups)

### Scenario 2: Database Corruption

If MISP database corrupted but server is functional:

```bash
# Stop MISP
cd /opt/misp && docker-compose stop misp-core misp-modules

# Restore database from last good backup
gunzip /backup/misp/misp-db-YYYYMMDD.sql.gz
cat /backup/misp/misp-db-YYYYMMDD.sql | docker exec -i misp-db-1 mysql -u misp -p'PASSWORD' misp

# Restart MISP
docker-compose start misp-core misp-modules
```

### Scenario 3: Accidental Event Deletion

MISP soft-deletes events (recoverable):

```
Admin > List Events > Include deleted events > Restore event
```

If permanently deleted, restore from database backup (Scenario 2).

## Backup Testing (CIP-009 R2.2)

**Requirement**: Test recovery plan at least once every 15 calendar months

**Test Procedure**:

1. **Schedule test** (coordinate with operations, minimize disruption)

2. **Provision test environment**:
   - Separate VM/server (NOT production)
   - Use production backups

3. **Perform full recovery** (follow Scenario 1 steps)

4. **Validate recovered MISP**:
   - Login with admin account
   - Verify event count matches production
   - Query API for test event
   - Check taxonomies and galaxies enabled
   - Test SIEM log forwarding
   - Test firewall IOC export

5. **Document test results**:
   - Test date
   - Backup date used
   - Recovery time (actual)
   - Issues encountered
   - Lessons learned

6. **Store documentation** (CIP-009 compliance evidence)

**Last recovery test**: _______________________________ (update after testing)
**Next recovery test due**: _______________________________ (15 months from last test)
```

---

## Summary of Person 3 Tasks

| Task | CIP Standard | Priority | Estimated Time | Key Deliverables |
|------|-------------|----------|----------------|------------------|
| 3.1 | CIP-007 R4 | HIGH | 6-8 hours | SIEM platform assessment, MISP log forwarding config, parsing rules, correlation rules |
| 3.2 | CIP-010 R3 | HIGH | 5-7 hours | Vulnerability assessment tracking, MISP event templates, 15-month cycle dashboard |
| 3.3 | CIP-010 R2 | HIGH | 4-6 hours | Patch management workflow, 35-day deadline tracking, change control integration |
| 3.4 | CIP-008 R1 | HIGH | 6-8 hours | E-ISAC reporting automation, incident response playbooks, SOAR integration plan |
| 3.5 | CIP-005 R2 | MEDIUM | 4-5 hours | Firewall IOC export, EDL configuration, quality control procedures |
| 3.6 | CIP-015 R1 | MEDIUM | 5-6 hours | ICS monitoring tool integration, bi-directional threat intelligence sharing |
| 3.7 | CIP-009 R2 | LOW | 3-4 hours | Automated backup script, disaster recovery procedures, backup testing plan |
| **TOTAL** | | | **33-44 hours** | Complete integration architecture for MISP |

## Next Steps After Research Completion

After Person 3 completes all research tasks:

1. **Schedule team meeting** with Person 1, Person 2, and Person 3 to present findings

2. **Consolidate requirements** into single implementation plan

3. **Begin implementation phase**:
   - Week 1-2: Quick wins (enable taxonomies, configure SIEM forwarding, enable backups)
   - Week 3-6: Core integrations (vulnerability tracking, patch management, firewall IOC export)
   - Week 7-10: Advanced automation (incident response playbooks, SOAR integration, ICS tool integration)
   - Week 11-12: Testing and documentation (CIP-009 recovery testing, E-ISAC reporting test, final compliance audit)

4. **Track implementation progress** in MISP (dogfooding!)

5. **Conduct final NERC CIP compliance audit** to verify 95-100% readiness

---

## Questions for Person 3 to Answer

As you complete each task, document answers to these questions:

### SIEM Integration (Task 3.1)
- [ ] What is our corporate SIEM platform?
- [ ] Does it support syslog/CEF input for MISP logs?
- [ ] What is the SIEM administrator contact info?
- [ ] Do we need a firewall rule change for MISP → SIEM connectivity?

### Vulnerability Management (Task 3.2)
- [ ] What vulnerability scanner do we use?
- [ ] How often do we scan BES Cyber Systems?
- [ ] When was the last vulnerability assessment?
- [ ] Which ICS vendors do we need to monitor for advisories?

### Patch Management (Task 3.3)
- [ ] What patch management tool do we use (WSUS, SCCM, etc.)?
- [ ] What is our typical change control lead time?
- [ ] What percentage of patches are deployed within 35 days currently?
- [ ] What is our change control platform (ServiceNow, Jira, etc.)?

### Incident Response (Task 3.4)
- [ ] Are we a member of E-ISAC?
- [ ] Who is our E-ISAC primary contact?
- [ ] Do we currently meet the 1-hour reporting requirement?
- [ ] Do we have a SOAR platform?

### Firewall Integration (Task 3.5)
- [ ] What firewall vendor do we use?
- [ ] Does firewall support External Dynamic Lists (EDL)?
- [ ] Does firewall currently consume threat intelligence feeds?
- [ ] Who is the firewall administrator?

### ICS Monitoring (Task 3.6)
- [ ] Do we have dedicated ICS/OT network monitoring?
- [ ] Which vendor (Dragos, Claroty, Nozomi, etc.)?
- [ ] Does it support STIX/TAXII integration?
- [ ] What is the typical alert volume?

### Backup and Recovery (Task 3.7)
- [ ] Is MISP classified as a BES Cyber Asset?
- [ ] Are MISP backups currently performed?
- [ ] Where are backups stored (off-site requirement)?
- [ ] When was the last recovery test?

---

## Useful References for Person 3

- **MISP Log Files**: `/opt/misp/logs/` (auth.log, audit.log, error.log)
- **MISP API Documentation**: https://www.misp-project.org/openapi/
- **PyMISP Documentation**: https://pymisp.readthedocs.io/
- **NERC CIP Standards**: https://www.nerc.com/pa/Stand/Pages/CIPStandards.aspx
- **E-ISAC Website**: https://www.eisac.com/
- **MISP Integrations**: https://www.misp-project.org/tools/

---

**Document Version**: 1.0
**Created**: 2024-10-24
**For**: MISP NERC CIP Medium Impact Compliance Project
**Estimated Completion Time**: 33-44 hours of research
