# -*- coding: utf-8; -*-

import os

from setuptools import setup


def read(path):
    with open(os.path.join(os.path.dirname(__file__), path), encoding='utf-8') as f:
        return f.read()


long_description = read("README.md")

setup(
    name="check-synology",
    version="1.0.0",
    url="https://github.com/wernerfred/check_synology",
    author="Frederic Werner",
    description="Check different values on your Synology DiskStation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=["any"],
    license="AGPL-3.0",
    keywords="synology, synology-diskstation, snmp, snmpv3, monitoring, monitoring-plugin, nagios, icinga2, icinga2-plugin",
    py_modules=["check_synology"],
    scripts=["check_synology.py"],
    python_requires=">=3.4",
    install_requires=["easysnmp>=0.2.6,<1"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Topic :: Communications",
        "Topic :: Database",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Archiving",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
)
