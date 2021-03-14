# coding: utf8

from setuptools import find_packages, setup

setup(name='bookings-report',
      version='0.1',
      description='Generate a monthly restaurant bookings report',
      author='Quentin Augé',
      author_email='quentin.auge@gmail.com',
      license='closed',
      packages=find_packages(),

      python_requires='>=3.6',

      classifiers=['Programming Language :: Python :: 3 :: Only',
                   'Operating System :: MacOS',
                   'Operating System :: Unix'],

      install_requires=['sqlalchemy', 'psycopg2-binary'],

      extras_require={
          'testing': ['coverage', 'pytest', 'pytest-cov']
      },

      entry_points={
          'console_scripts': [
              'bookings-report = bookings_report.cli:main'
          ]
      })
