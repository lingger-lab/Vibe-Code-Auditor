"""Setup script for Vibe-Code Auditor."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vibe-code-auditor",
    version="1.0.0",
    author="Vibe Coding Architect",
    description="AI-powered code analysis tool for Vibe Coding projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=[
        "click==8.1.7",
        "anthropic==0.45.0",
        "rich==13.9.4",
        "python-dotenv==1.0.1",
        "pylint==3.3.2",
        "semgrep==1.100.0",
    ],
    entry_points={
        "console_scripts": [
            "vibe-auditor=src.cli.main:main",
        ],
    },
)
