"""Setup configuration for AI Extraction System."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith('#')
    ]
else:
    requirements = [
        'langchain>=0.1.0',
        'langchain-community>=0.0.10',
        'openai>=1.0.0',
        'anthropic>=0.7.0',
        'pypdf>=3.17.0',
        'pdfplumber>=0.10.0',
        'beautifulsoup4>=4.12.0',
        'lxml>=4.9.0',
        'pydantic>=2.0.0',
        'python-dotenv>=1.0.0',
    ]

setup(
    name="ai-extraction-system",
    version="1.0.0",
    author="AI Systems Team",
    author_email="info@example.com",
    description="AI-powered parameter extraction for renewable energy investment analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-extraction-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'cache': [
            'redis>=5.0.0',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
