import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="podfeed",
  version="1.0.0",
  author="Max Mazzocchi",
  author_email="maxwell.mazzocchi@gmail.com",
  description="A simple podcast feed parser",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/mmazzocchi/podfeed",
  packages=setuptools.find_packages(exclude=["test"]),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  keywords="podcast RSS feed parser",
)
