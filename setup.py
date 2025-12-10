"""Setup script for Frontend Scanner."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="frontend-scanner",
    version="1.0.0",
    author="Engineering Team",
    author_email="team@example.com",
    description="LangGraph-powered frontend code scanner for AI agent systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/frontend-scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "scan-frontend=frontend_scanner.api.cli:main",
        ],
    },
)
