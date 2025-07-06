#!/usr/bin/env python3
"""
Setup script for BTC Portfolio Tracker
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="btc-portfolio-tracker",
    version="2.0.0",
    author="BTC Portfolio Tracker Team",
    author_email="contact@btctracker.dev",
    description="A comprehensive Bitcoin portfolio tracking application with savings and spending management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/btc-portfolio-tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "pytest>=7.0.0",
            "pytest-flask>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "btc-tracker=frontend.btc_gui:main",
            "btc-tracker-backend=backend.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="bitcoin, portfolio, tracker, cryptocurrency, investment, savings, spending",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/btc-portfolio-tracker/issues",
        "Source": "https://github.com/yourusername/btc-portfolio-tracker",
        "Documentation": "https://github.com/yourusername/btc-portfolio-tracker/wiki",
    },
)
