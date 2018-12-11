import io
import os
import sys

from setuptools import setup, find_packages


def local_file(*name):
    return os.path.join(
        os.path.dirname(__file__),
        *name)


def read(name, **kwargs):
    with io.open(
        name,
        encoding=kwargs.get("encoding", "utf8")
    ) as handle:
        return handle.read()


# This is unfortunately duplicated from scripts/cosmic_ray_tooling.py. I
# couldn't find a way to use the original version and still have tox
# work...hmmm...
def read_version():
    "Read the `(version-string, version-info)` from `cosmic_ray/version.py`."
    version_file = local_file('cosmic_ray', 'version.py')
    local_vars = {}
    with open(version_file) as handle:
        exec(handle.read(), {}, local_vars)  # pylint: disable=exec-used
    return (local_vars['__version__'], local_vars['__version_info__'])


LONG_DESCRIPTION = read(local_file('README.rst'), mode='rt')


INSTALL_REQUIRES = [
    'astunparse',
    'decorator',
    'docopt_subcommands>=2.3.0',
    'kfg',
    'parso',
    'pathlib',
    'qprompt',
    'spor==1.0.2',
    'stevedore',
    'yattag',
]

if sys.version_info < (3, 4):
    INSTALL_REQUIRES.append('enum34')

setup(
    name='cosmic_ray',
    version=read_version()[0],
    packages=find_packages(),

    author='Sixty North AS',
    author_email='austin@sixty-north.com',
    description='Mutation testing',
    license='MIT License',
    keywords='testing',
    url='http://github.com/sixty-north/cosmic-ray',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
    ],
    platforms='any',
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'test': ['hypothesis', 'pytest', 'pytest-mock', 'tox'],
        'docs': ['sphinx', 'sphinx_rtd_theme'],
        'pytest_runner': ['cosmic_ray_pytest_runner'],
        'celery3_engine': ['cosmic_ray_celery3_engine'],
    },
    entry_points={
        'console_scripts': [
            'cosmic-ray = cosmic_ray.cli:main',
            'cr-html = cosmic_ray.commands.format:report_html',
            'cr-report = cosmic_ray.commands.format:report',
            'cr-rate = cosmic_ray.tools.survival_rate:format_survival_rate',
            'cr-xml = cosmic_ray.commands.format:report_xml',
        ],
        'cosmic_ray.test_runners': [
            'unittest = cosmic_ray.testing.unittest_runner:UnittestRunner',
        ],
        'cosmic_ray.operator_providers': [
            'core = cosmic_ray.operators.provider:OperatorProvider'
        ],
        'cosmic_ray.execution_engines': [
            'local = cosmic_ray.execution.local:LocalExecutionEngine',
        ],
        'cosmic_ray.interceptors': [
            'spor = cosmic_ray.interceptors.spor:intercept'
        ],
    },
    long_description=LONG_DESCRIPTION,
)
