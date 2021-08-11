import pathlib
from setuptools import setup

# The directory containing this file
BASE = pathlib.Path(__file__).parent

# The text of the README file
README = (BASE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="maglev",
    version="0.0.1",
    description="A micro ASGI framework",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Nafi-Amaan-Hossain/maglev",
    author="Nafi Amaan Hossain",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["maglev"],
    include_package_data=True,
)
