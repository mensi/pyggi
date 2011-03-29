from setuptools import setup, find_packages

setup(
	name='Pyggi',
	version='0.1',
	packages=[],
	include_package_data=False,
	install_requires=[\
		'Flask>=0.6',
		'GitPython==0.1.7',
		'Markdown>=2.0.3',
		'docutils>=0.7',
	]
)

