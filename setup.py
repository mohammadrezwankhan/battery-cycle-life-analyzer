from setuptools import setup, find_packages

setup(
    name="bcla",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21",
        "scipy>=1.7",
        "matplotlib>=3.5",
    ],
    python_requires=">=3.9",
    author="Mohammad Rezwan Khan",
    author_email="mohammadrezwankhan@users.noreply.github.com",
    description="Battery Cycle‑Life Analyzer — fit degradation models, project EOL, create publication‑ready figures",
    license="MIT",
    url="https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
    ],
)
