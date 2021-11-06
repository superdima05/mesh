from setuptools import find_packages, setup

with open("README.md") as f:
	long_description = f.read()

setup(
    name='libmesh',
    packages=find_packages(),
    version='0.0.6',
    description='This library can get answers from uchebnik.mos.ru ',
    author='superdima05, kinda-cookie-monster',
    python_requires='>=3.9',
    scripts=['scripts/meshLauncher'],
    license='GPL-3.0',
    license_file='LICENSE',
    install_requires=['requests'],
    long_description_content_type='text/markdown',
    long_description=long_description,
    url='https://github.com/superdima05/mesh/',
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ]    
)

