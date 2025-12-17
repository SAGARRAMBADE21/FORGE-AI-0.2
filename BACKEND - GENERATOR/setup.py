"""
Setup configuration for Backend Generation Agent.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="backend-agent",
    version="1.0.0",
    description="AI-powered backend code generation agent using LangGraph",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/backend-agent",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "backend_agent": [
            "templates/**/*",
            "templates/**/*.jinja2",
        ],
    },
    python_requires=">=3.10",
    install_requires=[
        "langchain>=0.1.16",
        "langchain-openai>=0.1.3",
        "langgraph>=0.0.55",
        "jinja2>=3.1.3",
        "black>=24.2.0",
        "sqlalchemy>=2.0.27",
        "alembic>=1.13.1",
        "pydantic>=2.6.4",
        "fastapi>=0.110.0",
        "uvicorn>=0.29.0",
        "click>=8.1.7",
        "rich>=13.7.1",
        "python-dotenv>=1.0.1",
        "pyyaml>=6.0.1",
        "gitpython>=3.1.42",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.2",
            "pytest-asyncio>=0.23.5",
            "black>=24.2.0",
            "isort>=5.13.2",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "generate-backend=backend_agent.api.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
