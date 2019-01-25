# This file is part of pypassport.
#
# pypassport is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# pypassport is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with pyPassport.
# If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(
    name='pypassport',
    version='2.1',
    description='Python Biometric Passport API',
    long_description=read('README'),
    author='Jean-Francois Houzard, Olivier Roger and Antonin Beaujeant',
    author_email='jhouzard@gmail.com and folkenda@gmail.com',
    url='https://github.com/beaujeant/ePassportViewer',
    keywords='mrtd passport pypassport epassport viewer',
    license='LGPL',
    classifiers=[
      "License :: OSI Approved :: GNU Lesser General Public License (LGPL)",
      "Programming Language :: Python",
      "Development Status :: 4 - Beta",
      "Intended Audience :: Developers",
      "Topic :: RFID"
    ],

    packages=find_packages(),
    package_data = {
      '': ['*.py'],
      'pypassport': ['README', 'LICENSE']
    },

    install_requires=[
        'pyCrypto',
        'pyasn1',
        'pyscard',
        'pillow'
    ],

    zip_safe = False
)
