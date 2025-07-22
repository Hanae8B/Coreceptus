# setup.py

from setuptools import setup, find_packages

setup(
    name="coreceptus",
    version="0.1.0",
    description="A symbolic computation engine with unified number and symbol nodes",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/coreceptus",  # Optional
    packages=find_packages(exclude=["tests*", "venv*", "docs*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        # Add project dependencies here
        # Example:
        # "numpy>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.0.0",
            "black",
            "mypy",
            "flake8",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    entry_points={
        # Optional CLI script entry point (can be added later)
        # "console_scripts": [
        #     "coreceptus-cli = coreceptus.cli:main",
        # ]
    },
)
