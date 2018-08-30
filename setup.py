from setuptools import setup

with open('requirements.txt', 'r') as f:
	install_requires = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
	name='verispy',
	version='0.1.0',
	description='Parses VCDB json data into a Pandas DataFrame and provides useful analytic functions',
	author='Tyler Byers',
	author_email='tbyers@risklens.com',
	packages=['verispy', 'verispy.tests'],
	license='LICENSE.txt',
	long_description=long_description,
	long_description_content_type="text/markdown",
	#url='https://fillinwhenIhaveahome'
	install_requires=install_requires,
	include_package_data=True
)