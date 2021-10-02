import setuptools
from anonymizer._version import __version__


# Parse requirements
install_requires = [line.strip() for line in open("requirements.txt").readlines()]

# Get long description
with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

# Setup package
setuptools.setup(
    name="anonymizer",
    version=__version__,
    author="Drineczki AI",
    author_email="wjlazarski@gmail.com",
    description="Document anonymizer for hack4law.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drineczki/hack4law-anonymizer",
    packages=["anonymizer"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    include_package_data=True,
)
