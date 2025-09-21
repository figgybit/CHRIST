"""
Setup script for the C.H.R.I.S.T. Project
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="christ-consciousness",
    version="0.1.0-alpha",
    author="The C.H.R.I.S.T. Community",
    author_email="hello@christproject.org",
    description="An open-source consciousness capture and emulation system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/figgybit/CHRIST",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.25.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.25",
        "cryptography>=41.0.7",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "ml": [
            "openai>=1.6.1",
            "langchain>=0.1.0",
            "chromadb>=0.4.22",
        ],
    },
    entry_points={
        "console_scripts": [
            "christ=src.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/figgybit/CHRIST/issues",
        "Source": "https://github.com/figgybit/CHRIST",
        "Documentation": "https://christ.ai/docs",
    },
)