import os
import re
from setuptools import setup, find_packages


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


def get_long_description():
    with open("README.md", "rt") as fd:
        return fd.read()


setup(
    name='Starlette-Login',
    python_requires='>=3.6',
    version=get_version('starlette_login'),
    url='https://github.com/jockerz/starlette-login',
    license='MIT',
    description='User session management for Starlette',
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author='Jockerz',
    author_email='jockerz@protonmail.com',
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        'starlette',
        'itsdangerous',  # required by starlette' SessionMiddleware
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    zip_safe=False,
)
