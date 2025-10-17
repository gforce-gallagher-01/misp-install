#!/usr/bin/env python3
"""
Analyze Python scripts for DRY violations
Identifies common patterns that should be extracted to shared modules
"""

import os
from collections import defaultdict
from pathlib import Path


class DRYAnalyzer:
    """Analyze code for DRY violations"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.patterns = defaultdict(list)

    def analyze_file(self, filepath):
        """Analyze single file for common patterns"""
        with open(filepath) as f:
            content = f.read()
            content.split('\n')

        rel_path = filepath.relative_to(self.base_dir)

        # Pattern 1: API key extraction from .env
        if 'MISP_API_KEY' in content and 'grep' in content:
            self.patterns['api_key_from_env'].append(str(rel_path))

        # Pattern 2: Docker container checks
        if 'docker ps' in content or 'docker exec' in content:
            self.patterns['docker_operations'].append(str(rel_path))

        # Pattern 3: MISP URL construction
        if 'https://' in content and ('misp' in content.lower() or 'localhost' in content):
            self.patterns['misp_url_construction'].append(str(rel_path))

        # Pattern 4: REST API calls with requests
        if 'import requests' in content or 'requests.get' in content or 'requests.post' in content:
            self.patterns['rest_api_calls'].append(str(rel_path))

        # Pattern 5: Logging initialization
        if 'get_logger' in content or 'logging.getLogger' in content:
            self.patterns['logger_init'].append(str(rel_path))

        # Pattern 6: File operations with sudo/misp-owner
        if 'sudo' in content and ('cp' in content or 'chown' in content or 'chmod' in content):
            self.patterns['file_operations_sudo'].append(str(rel_path))

        # Pattern 7: Cron job management
        if 'crontab' in content:
            self.patterns['cron_management'].append(str(rel_path))

        # Pattern 8: MISP container readiness checks
        if 'misp-core' in content and 'running' in content.lower():
            self.patterns['container_readiness'].append(str(rel_path))

        # Pattern 9: argparse CLI setup
        if 'argparse' in content and 'ArgumentParser' in content:
            self.patterns['cli_argparse'].append(str(rel_path))

        # Pattern 10: JSON encode/decode
        if 'json.load' in content or 'json.dump' in content:
            self.patterns['json_operations'].append(str(rel_path))

        # Pattern 11: Error handling patterns
        try_count = content.count('try:')
        if try_count >= 3:
            self.patterns['multiple_try_blocks'].append(f"{rel_path} ({try_count} blocks)")

        # Pattern 12: Subprocess run patterns
        subprocess_count = content.count('subprocess.run')
        if subprocess_count >= 5:
            self.patterns['many_subprocess_calls'].append(f"{rel_path} ({subprocess_count} calls)")

    def analyze_all(self):
        """Analyze all Python files"""
        print("Analyzing Python files for DRY violations...\n")

        for root, _dirs, files in os.walk(self.base_dir):
            # Skip certain directories
            if '__pycache__' in root or '.git' in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    self.analyze_file(filepath)

    def report(self):
        """Generate DRY violations report"""
        print("="*80)
        print("DRY VIOLATIONS ANALYSIS REPORT")
        print("="*80)
        print()

        total_patterns = sum(len(v) for v in self.patterns.values())
        print(f"Total potential violations found: {total_patterns}")
        print(f"Pattern categories: {len(self.patterns)}")
        print()

        for pattern, files in sorted(self.patterns.items(), key=lambda x: len(x[1]), reverse=True):
            if not files:
                continue

            print(f"\n{'='*80}")
            print(f"Pattern: {pattern.upper().replace('_', ' ')}")
            print(f"Occurrences: {len(files)}")
            print(f"{'='*80}")

            for i, file in enumerate(files, 1):
                print(f"  {i}. {file}")

        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)
        print()

        recommendations = {
            'api_key_from_env': "Create lib/misp_api_helpers.py with get_api_key() function",
            'docker_operations': "Create lib/docker_helpers.py with container management functions",
            'misp_url_construction': "Create lib/misp_api_helpers.py with get_misp_url() function",
            'rest_api_calls': "Create lib/misp_api_client.py with MISPAPIClient class",
            'logger_init': "Already using misp_logger.py - ensure all scripts use it",
            'file_operations_sudo': "BasePhase has write_file_as_misp_user() - ensure all phases use it",
            'cron_management': "Create lib/cron_helpers.py with cron management functions",
            'container_readiness': "Create lib/docker_helpers.py with is_container_ready() function",
            'cli_argparse': "Create lib/cli_helpers.py with common CLI argument patterns",
            'json_operations': "Create lib/json_helpers.py with safe JSON operations",
        }

        for pattern in sorted(self.patterns.keys()):
            if pattern in recommendations:
                print(f"\n{pattern}:")
                print(f"  → {recommendations[pattern]}")

if __name__ == "__main__":
    analyzer = DRYAnalyzer(Path(__file__).parent.parent)
    analyzer.analyze_all()
    analyzer.report()
