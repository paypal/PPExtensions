import os

from setuptools import setup, find_packages

DESCRIPTION = "PPExtenions - Set of iPython and Jupyter extensions"
NAME = "ppextensions"
PACKAGES = ["ppextensions", "github", "scheduler"]
AUTHOR = "PPExtensions Development Team"
AUTHOR_EMAIL = "jupyter@googlegroups.org"
URL = 'https://github.com/paypal/ppextensions'
DOWNLOAD_URL = 'https://github.com/paypal/ppextensions'
LICENSE = 'BSD License'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md'), encoding='utf-8').read()

VERSION = '0.0.5'

install_requires = [
    'ipython>=1.0',
    'qgrid',
    'impyla==0.13.8',
    'hdfs3',
    'teradata==15.10.0.20',
    'protobuf==3.5.2.post1',
    'sqlparse',
    'pyhive==0.2.1',
    'pysftp==0.2.9',
    'prettytable',
    'ipython-sql==0.3.8',
    'requests',
    'astor',
    'pandas==0.22.0',
    'autovizwidget',
    'thrift-sasl==0.2.1',
    'apache-airflow==1.8.2',
    'nbdime',
    'gitpython',
    'mysql-connector-python-rf'
]

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=README,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      download_url=DOWNLOAD_URL,
      license=LICENSE,
      packages=find_packages(),
      classifiers=[
          'Intended Audience :: System Administrators',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5'],
      install_requires=install_requires,
      extras_require={
          'dev': [
              'pycodestyle'
          ]
      })

