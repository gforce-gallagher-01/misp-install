#!/usr/bin/env python3
"""
Setup script for MISP GUI Installer
Allows installation via pipx
"""

from pathlib import Path

from setuptools import setup

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="misp-installer-gui",
    version="1.0.0",
    description="Modern GUI installer for MISP using Textual framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="tKQB Enterprises",
    author_email="admin@tkqb.enterprises",
    url="https://github.com/gforce-gallagher-01/misp-install",
    py_modules=["misp_install_gui", "misp_logger"],
    python_requires=">=3.8",
    install_requires=[
        "textual>=0.45.0",
        "textual-dev>=1.2.0",
        "pyperclip>=1.8.0",
    ],
    entry_points={
        "console_scripts": [
            "misp-install-gui=misp_install_gui:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Installation/Setup",
        "Topic :: Security",
    ],
    keywords="misp security installer gui tui",
)
