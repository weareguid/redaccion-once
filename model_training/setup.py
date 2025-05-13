from setuptools import setup, find_packages

setup(
    name="model_training",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "datasets",
        "wandb",
        "pydantic"
    ]
) 