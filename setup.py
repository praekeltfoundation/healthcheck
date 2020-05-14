from setuptools import find_packages, setup

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
    install_requires=["django==2.2.12", "django-environ==0.4.5"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
