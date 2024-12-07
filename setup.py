from setuptools import setup, find_packages

setup(
    name="bookai",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"bookai": "bookai"},
    author="Andrea Favia",
    author_email="andrea.faviait@gmail.com",
    description="A package to summarize non-fictional books",
    # long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/faviasono/bookai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
