from setuptools import setup, find_packages

setup(
    name="pytdx2",
    version="0.1.0",
    author="Your Name",
    author_email="lisonevf@gmail.com",
    description="A Python client for TDX stock data",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
