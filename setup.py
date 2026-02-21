from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="reddit-saas-validator",
    version="1.0.0",
    author="Reddit SaaS Validator Team",
    author_email="",
    description="Multi-platform SaaS idea validation tool (Reddit, Twitter/X, LinkedIn)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/reddit-saas-validator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "saas-validator=validator:main",
        ],
    },
    keywords="saas validation reddit twitter linkedin scraping market-research",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/reddit-saas-validator/issues",
        "Source": "https://github.com/yourusername/reddit-saas-validator",
    },
)
