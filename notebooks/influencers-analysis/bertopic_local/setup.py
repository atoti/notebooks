import setuptools

test_packages = ["pytest>=5.4.3", "pytest-cov>=2.6.1"]

docs_packages = [
    "mkdocs>=1.1",
    "mkdocs-material>=4.6.3",
    "mkdocstrings>=0.8.0",
]

base_packages = [
    "numpy>=1.19.2",
    "hdbscan>=0.8.27",
    "umap-learn>=0.5.0",
    "pandas>=1.1.5",
    "scikit-learn>=0.22.2.post1",
    "tqdm>=4.41.1",
    "torch>=1.4.0",
    "sentence-transformers>=0.4.1",
]

visualization_packages = ["matplotlib>=3.2.2", "plotly>=4.7.0,<4.14.3"]

flair_packages = ["flair==0.7"]

extra_packages = visualization_packages + flair_packages

dev_packages = docs_packages + test_packages + extra_packages


setuptools.setup(
    name="bertopic",
    version="0.5.0",
    description="Modification of BERTopic package from Maarten Grootendorst: additional functions added.",
    url="#",
    author="Ariel Ibaba",
    author_email="aibaba2108@gmail.com",
    install_requires=base_packages,
    packages=setuptools.find_packages(),
    zip_safe=False,
    extras_require={
        "test": test_packages,
        "docs": docs_packages,
        "dev": dev_packages,
        "visualization": visualization_packages,
        "flair": flair_packages,
        "all": extra_packages,
    },
    python_requires=">=3.6",
)
