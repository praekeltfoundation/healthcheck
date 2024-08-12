import pathlib

import pkg_resources
from setuptools import find_packages, setup

requirements = [
    "django-environ==0.11.2",
    "psycopg2==2.9.9",
    "requests==2.32.0",
    "rapidpro-python==2.6.1",
    "django-import-export==4.1.1",
    "setuptools==72.1.0",
]

try:
    with pathlib.Path("requirements.txt").open() as requirements_txt:
        requirements += [
            str(requirement)
            for requirement in pkg_resources.parse_requirements(requirements_txt)
        ]
except FileNotFoundError:
    pass


setup(
    name="healthcheck",
    version="0.0.1",
    url="https://github.com/praekeltfoundation/healthcheck",
    license="BSD",
    description="Django service for HealthCheck",
    author="praekelt.org",
    author_email="dev@praekelt.org",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
