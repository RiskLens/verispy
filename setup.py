import setuptools

with open('requirements.txt', 'r') as f:
	install_requires = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
	name='verispy',
	version='0.1.4',
	description='Parses VCDB json data into a Pandas DataFrame and provides summary functions and basic enumeration plotting.',
	author='Tyler Byers',
	author_email='tbyers@risklens.com',
	packages=setuptools.find_packages(),
	license='MIT',
	long_description=long_description,
	long_description_content_type="text/markdown",
	url='https://github.com/RiskLens/verispy',
	install_requires=install_requires,
	include_package_data=True,
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)