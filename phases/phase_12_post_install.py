"""
Phase 12: Post-install tasks
"""

from datetime import datetime

from lib.colors import Colors
from lib.user_manager import MISP_USER
from phases.base_phase import BasePhase


class Phase12PostInstall(BasePhase):
    """Phase 12: Post-installation tasks"""

    def run(self):
        """Execute post-install tasks"""
        self.section_header("PHASE 12: POST-INSTALL TASKS")

        self._create_checklist()

        self.logger.info(Colors.success("Post-install checklist created"))
        self.save_state(12, "Post-Install Complete")

    def _create_checklist(self):
        """Create post-installation checklist"""
        self.logger.info("[12.1] Creating post-install checklist...")

        checklist_content = f"""# MISP Post-Installation Checklist
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Immediate Actions (Do Now):
- [ ] Login to MISP web interface: {self.config.base_url}
- [ ] Verify admin account works
- [ ] Review system settings
- [ ] Configure email settings (Administration → Server Settings → Email)
- [ ] Test email notifications

## Security (First Week):
- [ ] Enable 2FA for admin account
- [ ] Change admin password (even though it's already strong)
- [ ] Review user permissions
- [ ] Configure firewall: `sudo ufw allow 443/tcp`
- [ ] Set up SSL certificate monitoring
- [ ] Review audit logs

## Backup & Recovery (First Week):
- [ ] Configure automated backups
- [ ] Test backup restoration
- [ ] Document recovery procedures
- [ ] Set up off-site backup storage

## Integration (First Month):
- [ ] Configure MISP feeds (Administration → Feeds)
- [ ] Set up sync servers if needed
- [ ] Configure API access
- [ ] Test MISP modules functionality
- [ ] Configure enrichment services
- [ ] Set up correlation rules

## Monitoring (First Month):
- [ ] Set up log monitoring
- [ ] Configure alerts for critical events
- [ ] Test notification system
- [ ] Verify worker status: `cd /opt/misp && sudo docker compose exec misp-core ps aux | grep worker`
- [ ] Monitor disk space usage
- [ ] Set up uptime monitoring

## Team & Training (First Month):
- [ ] Create user accounts for team members
- [ ] Assign appropriate roles and permissions
- [ ] Conduct initial training session
- [ ] Document common workflows
- [ ] Create runbook for common tasks

## Performance Optimization (Ongoing):
- [ ] Monitor database performance
- [ ] Review and tune worker settings
- [ ] Optimize Redis cache settings
- [ ] Review and clean old events periodically

## Workstation Setup:
Windows users must add to C:\\Windows\\System32\\drivers\\etc\\hosts:
{self.config.server_ip} {self.config.domain}

macOS/Linux users:
echo '{self.config.server_ip} {self.config.domain}' | sudo tee -a /etc/hosts

## Useful Commands:
```bash
# View logs
cd /opt/misp && sudo docker compose logs -f

# Restart MISP
cd /opt/misp && sudo docker compose restart

# Stop MISP
cd /opt/misp && sudo docker compose down

# Start MISP
cd /opt/misp && sudo docker compose up -d

# Check status
cd /opt/misp && sudo docker compose ps

# View passwords
sudo cat /opt/misp/PASSWORDS.txt
```

## Support & Resources:
- MISP Documentation: https://www.misp-project.org/documentation/
- MISP Book: https://www.circl.lu/doc/misp/
- Community: https://www.misp-project.org/community/
- GitHub: https://github.com/MISP/MISP

## Backup Locations:
- Passwords: /opt/misp/PASSWORDS.txt
- Configuration: /opt/misp/.env
- SSL Certificates: /opt/misp/ssl/
- Backups: ~/misp-backups/
- Logs: /opt/misp/logs/
"""

        # SECURITY: Write using temp file pattern (owned by misp-owner)
        checklist_file = self.misp_dir / "POST-INSTALL-CHECKLIST.md"
        self.write_file_as_misp_user(checklist_content, checklist_file, mode='644', misp_user=MISP_USER)
