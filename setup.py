from setuptools import setup, find_packages

setup(
    name="module_reloader",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add any dependencies here
    ],
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    description="A module reloader for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jonathan Shieh",
    author_email="jonathan.shieh@gmail.com",
    url="https://github.com/odie/module_reloader",
)
