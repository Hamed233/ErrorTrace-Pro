from setuptools import setup, find_packages
import os
import re

# Read the content of __init__.py to get the version
with open(os.path.join('errortrace_pro', '__init__.py'), 'r', encoding='utf-8') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    version = version_match.group(1) if version_match else '0.3.0'

# Read the content of README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='errortrace-pro',
    version=version,
    description='Enhanced exception handling with visual tracebacks, solution suggestions, and cloud logging',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Hamed Esam',
    author_email='h.esam@example.com',
    url='https://github.com/Hamed233/ErrorTrace-Pro',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'errortrace_pro': ['data/*.json'],
    },
    entry_points={
        'console_scripts': [
            'errortrace=errortrace_pro.cli:main',
        ],
    },
    install_requires=[
        'colorama>=0.4.4;python_version<"3.10"',
    ],
    extras_require={
        'rich': ['rich>=10.0.0'],
        'cli': ['click>=7.0.0'],
        'all': [
            'rich>=10.0.0',
            'click>=7.0.0',
            'flask>=2.0.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'isort>=5.0.0',
            'build>=0.10.0',
            'twine>=4.0.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    keywords='exception, traceback, debugging, error handling, cloud logging',
)
