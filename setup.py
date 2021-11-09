from setuptools import setup, find_packages
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='terrasafe',
    version=os.getenv('RELEASE_TAG'),
    packages=find_packages(".", exclude=["test"]),
    url='https://github.com/PrismeaOpsTeam/Terrasafe',
    license='GPLv3',
    author='PrismeaOpsTeam',
    author_email='team-ops@prismea.fr',
    description='A CLI tool to analyze Terraform plan files, and prevent unallowed resources deletions and drop/create actions.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'terrasafe = terrasafe.terrasafe:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

)
