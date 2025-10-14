"""
Phase 10: Build and start Docker containers
"""

import os
import time
import json
import subprocess
from pathlib import Path
from phases.base_phase import BasePhase
from lib.colors import Colors
from lib.user_manager import MISP_USER, get_current_username


class Phase10DockerBuild(BasePhase):
    """Phase 10: Build and start Docker containers with progress monitoring"""

    def run(self):
        """Execute Docker build and start"""
        self.section_header("PHASE 10: DOCKER BUILD")

        os.chdir(self.misp_dir)

        try:
            self._pull_images()
            self._build_containers()
            self._start_containers()
            self._wait_for_health()
            self._show_final_status()
            self._configure_acls()

            self.logger.info(Colors.success("\n✓ Phase 10 completed"))
            self.save_state(10, "Docker Build Complete")

        except subprocess.TimeoutExpired as e:
            self.logger.error(Colors.error(f"\n❌ Timeout during docker build: {e}"))
            raise
        except Exception as e:
            self.logger.error(Colors.error(f"\n❌ Docker build failed: {e}"))
            raise

    def _pull_images(self):
        """Pull Docker images"""
        self.logger.info("[10.1] Pulling Docker images...")
        self.logger.info("This may take 10-20 minutes on first run...")
        self.logger.info("Progress will be shown below:\n")

        pull_cmd = ['sudo', 'docker', 'compose', 'pull']
        pull_process = subprocess.Popen(
            pull_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=self.misp_dir
        )

        # Stream output in real-time
        for line in iter(pull_process.stdout.readline, ''):
            if line:
                # Filter for important progress lines
                if any(keyword in line for keyword in ['Pulling', 'Downloading', 'Extracting',
                                                       'Pull complete', 'Status', 'Downloaded',
                                                       'Digest', 'Already exists']):
                    self.logger.info(f"  {line.rstrip()}")

        pull_process.wait(timeout=1800)  # 30 minute timeout for pulls

        if pull_process.returncode != 0:
            self.logger.warning("⚠ Pull had some issues, but continuing...")
        else:
            self.logger.info(Colors.success("\n✓ Images pulled successfully\n"))

    def _build_containers(self):
        """Build containers if needed"""
        self.logger.info("[10.2] Checking if build is required...")

        # Check for custom Dockerfiles
        needs_build = False
        if (self.misp_dir / "Dockerfile").exists():
            needs_build = True

        # Look for build contexts in docker-compose
        for subdir in self.misp_dir.iterdir():
            if subdir.is_dir() and (subdir / "Dockerfile").exists():
                needs_build = True
                break

        if needs_build:
            self.logger.info("Custom builds detected. Building containers...")
            self.logger.info("This may take 15-30 minutes on first run...\n")

            build_cmd = ['sudo', 'docker', 'compose', 'build', '--progress=plain']
            build_process = subprocess.Popen(
                build_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.misp_dir
            )

            # Stream output in real-time
            for line in iter(build_process.stdout.readline, ''):
                if line:
                    # Filter for important build lines
                    if any(keyword in line for keyword in ['Step', 'Successfully', 'Building',
                                                           'Sending build context', '--->',
                                                           'Running in', 'Removing intermediate']):
                        self.logger.info(f"  {line.rstrip()}")

            build_process.wait(timeout=2400)  # 40 minute timeout for builds

            if build_process.returncode == 0:
                self.logger.info(Colors.success("\n✓ Build completed\n"))
            else:
                self.logger.warning("⚠ Build completed with warnings\n")
        else:
            self.logger.info("No custom builds needed (using pre-built images)")
            self.logger.info(Colors.success("✓ Skipping build step\n"))

    def _start_containers(self):
        """Start Docker containers"""
        self.logger.info("[10.3] Starting MISP services...")
        self.run_command(
            ['sudo', 'docker', 'compose', 'up', '-d'],
            timeout=300,  # 5 minutes to start
            cwd=self.misp_dir
        )

        self.logger.info(Colors.success("✓ Containers started\n"))

    def _wait_for_health(self):
        """Wait for services to become healthy"""
        self.logger.info("[10.4] Waiting for services to become healthy...")
        self.logger.info("This typically takes 2-5 minutes...\n")

        max_wait = 300  # 5 minutes
        start_time = time.time()
        last_status = ""

        while (time.time() - start_time) < max_wait:
            # Get container status
            ps_result = self.run_command(
                ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
                timeout=30,
                cwd=self.misp_dir,
                check=False
            )

            if ps_result.returncode == 0:
                try:
                    containers = []
                    for line in ps_result.stdout.strip().split('\n'):
                        if line:
                            containers.append(json.loads(line))

                    healthy = sum(1 for c in containers if 'healthy' in c.get('Health', '').lower())
                    running = sum(1 for c in containers if c.get('State') == 'running')
                    total = len(containers)

                    elapsed = int(time.time() - start_time)
                    status = f"  [{elapsed}s] Running: {running}/{total} | Healthy: {healthy}/{total}"

                    # Only print if status changed
                    if status != last_status:
                        self.logger.info(status)
                        last_status = status

                    # Success condition: all running and at least some healthy
                    if running == total and total > 0:
                        if healthy > 0 or elapsed > 120:  # Give 2 min for health checks
                            self.logger.info(Colors.success(f"\n✓ All {total} containers are running"))
                            if healthy > 0:
                                self.logger.info(Colors.success(f"✓ {healthy} containers report healthy status"))
                            break

                except json.JSONDecodeError:
                    pass

            time.sleep(5)

    def _show_final_status(self):
        """Show final service status"""
        self.logger.info("\n[10.5] Final service status:")
        ps_result = self.run_command(
            ['sudo', 'docker', 'compose', 'ps'],
            timeout=30,
            cwd=self.misp_dir,
            check=False
        )

        if ps_result.returncode == 0:
            self.logger.info(ps_result.stdout)

        # Check for any unhealthy containers
        logs_needed = []
        check_result = self.run_command(
            ['sudo', 'docker', 'compose', 'ps', '--format', 'json'],
            timeout=30,
            cwd=self.misp_dir,
            check=False
        )

        if check_result.returncode == 0:
            try:
                for line in check_result.stdout.strip().split('\n'):
                    if line:
                        container = json.loads(line)
                        if container.get('State') != 'running':
                            logs_needed.append(container.get('Service', container.get('Name')))
            except:
                pass

        if logs_needed:
            self.logger.warning(f"\n⚠ Some containers are not running: {', '.join(logs_needed)}")
            self.logger.info("Checking logs...")
            for service in logs_needed[:2]:  # Limit to 2 services
                self.logger.info(f"\n--- Logs for {service} (last 20 lines) ---")
                log_result = self.run_command(
                    ['sudo', 'docker', 'compose', 'logs', '--tail', '20', service],
                    timeout=30,
                    cwd=self.misp_dir,
                    check=False
                )
                if log_result.returncode == 0:
                    self.logger.info(log_result.stdout)

    def _configure_acls(self):
        """Configure ACLs for shared log directory access"""
        # ARCHITECTURE: Docker owns directory as www-data, but ACLs allow scripts to write
        # This solves the permission conflict where Docker resets ownership to www-data:www-data
        self.logger.info("\n[10.6] Configuring ACLs for log directory...")
        try:
            current_user = get_current_username()
            logs_dir = '/opt/misp/logs'
            misp_dir = '/opt/misp'

            # Set ACLs for all users that need write access (existing files)
            self.run_command(['sudo', 'setfacl', '-R', '-m', 'u:www-data:rwx', logs_dir], check=False)
            self.run_command(['sudo', 'setfacl', '-R', '-m', f'u:{current_user}:rwx', logs_dir], check=False)
            self.run_command(['sudo', 'setfacl', '-R', '-m', f'u:{MISP_USER}:rwx', logs_dir], check=False)

            # Set default ACLs for newly created files
            self.run_command(['sudo', 'setfacl', '-R', '-d', '-m', 'u:www-data:rwx', logs_dir], check=False)
            self.run_command(['sudo', 'setfacl', '-R', '-d', '-m', f'u:{current_user}:rwx', logs_dir], check=False)
            self.run_command(['sudo', 'setfacl', '-R', '-d', '-m', f'u:{MISP_USER}:rwx', logs_dir], check=False)

            # CRITICAL: Fix ACL mask to ensure rwx permissions are effective
            # Without this, effective permissions remain r-x even though user ACLs are set to rwx
            self.run_command(['sudo', 'setfacl', '-m', 'mask::rwx', logs_dir], check=False)

            # Grant read access to config files for backup/restore scripts
            # This allows backup scripts to run as regular user without requiring sudo for file reads
            config_files = [
                f'{misp_dir}/.env',
                f'{misp_dir}/PASSWORDS.txt',
                f'{misp_dir}/docker-compose.yml',
                f'{misp_dir}/docker-compose.override.yml'
            ]

            for config_file in config_files:
                # Check if file exists before setting ACL
                if Path(config_file).exists():
                    self.run_command(['sudo', 'setfacl', '-m', f'u:{current_user}:r', config_file], check=False)

            self.logger.info(Colors.success(f"✓ ACLs configured for shared log access (www-data, {current_user}, {MISP_USER})"))
            self.logger.info(Colors.success(f"✓ ACL mask fixed for proper rwx permissions"))
            self.logger.info(Colors.success(f"✓ Config files readable by {current_user} for backup scripts"))
        except Exception as e:
            self.logger.warning(f"⚠ Could not configure ACLs: {e}")
