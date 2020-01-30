import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bridgelib", 
    version="0.0.1",
    author="Fabio Pruneri",
    author_email="fabiopruneri@college.harvard.edu",
    description="Tools for the game of Contract Bridge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FabioPru/bridgelib",
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src', exclude=('tests',)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
