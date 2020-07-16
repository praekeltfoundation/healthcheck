from setuptools import find_packages, setup
import pkg_resources
import pathlib
import os.path

requirements = ["django==2.2.13", "django-environ==0.4.5", "psycopg2==2.8.5"]

try:
    with pathlib.Path('requirements.txt').open() as requirements_txt:
        requirements += [
            str(requirement)
            for requirement
            in pkg_resources.parse_requirements(requirements_txt)
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
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
