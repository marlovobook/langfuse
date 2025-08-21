#!/usr/bin/env python3
"""
Simple setuptools setup.py for AWS Bedrock + Langfuse integration.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")
else:
    long_description = "AWS Bedrock integration with Langfuse for LLM observability"

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]
else:
    requirements = [
        "boto3>=1.26.0",
        "langfuse>=2.0.0",
        "pydantic>=1.10.0",
        "typing-extensions>=4.0.0"
    ]

setup(
    name="bedrock-langfuse",
    version="0.1.0",
    description="AWS Bedrock integration with Langfuse for LLM observability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AWS Bedrock Langfuse Team",
    author_email="team@example.com",
    url="https://github.com/example/bedrock-langfuse",
    packages=find_packages(exclude=["tests", "examples"]),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "types-boto3"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    license="MIT",
    zip_safe=False,
)
