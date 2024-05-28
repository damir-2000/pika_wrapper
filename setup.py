from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["pydantic==2.7.1", "pika==1.3.2"]

setup(
    name="pika_wrapper",
    version="0.0.1",
    author="damir-2000",
    author_email="gilemhonov.damir@gmail.com",
    description="Pika Pydantic Wrapper",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/damir-2000/pika_wrapper",
    packages=find_packages(),
    install_requires=requirements,
    license="MIT",
    python_requires=">=3.9.13",
    # classifiers=[
    #     "Programming Language :: Python :: 3.7",
    #     "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    # ],
)