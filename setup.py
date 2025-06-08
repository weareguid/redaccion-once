from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="once-noticias-ai",
    version="2.0.0",
    author="Once Noticias AI Team",
    author_email="ai@oncenoticias.digital",
    description="Sistema Editorial Optimizado para Once Noticias con IA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oncenoticias/ai-editorial-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "once-noticias=src.interfaces.streamlit_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["**/*.sql", "**/*.md", "**/*.toml"],
    },
)