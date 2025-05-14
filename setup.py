from setuptools import setup, find_packages

setup(
    name='framework_core',
    version='0.1.0',
    description='AI-Assisted Framework Core Components',
    author='AI-Assisted Framework Team',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'google-generativeai>=0.3.0',
    ],
    python_requires='>=3.8',
)
