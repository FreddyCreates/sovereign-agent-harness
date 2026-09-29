from setuptools import setup, find_packages

setup(
    name="sovereign-agent-harness",
    version="1.0.0",
    author="Alfredo Medina Hernandez",
    author_email="Medinasitech@outlook.com",
    description="Enterprise Client-Side Sovereign Vault, LOOM Memoria & AI Agent Runtime Harness",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/FreddyCreates/sovereign-engine",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sovereign-harness=sovereign_harness.cli:main",
        ],
    },
)
