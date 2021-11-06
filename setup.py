from setuptools import find_packages, setup

setup(
    name='mesh',
    packages=find_packages(),
    version='0.0.5',
    description='This library can get answers from uchebnik.mos.ru ',
    author='superdima05, kinda-cookie-monster',
    python_requires='>=3.9',
    scripts=['scripts/meshLauncher'],
    license='GPL-3.0',
    license_file='LICENSE',
    install_requires=['requests']    
)
