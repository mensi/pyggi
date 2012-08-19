# Pyggi
Pyggi is a lightweight git frontend

## Features

- README markdown on front-page
- easy setup and configuration
- full WSGI compliance (flask)
- an easy-on-the-eyes UI

## Dependencies

- Flask			>= 0.7
- GitPython		== 0.3git

The current version of GitPython on PyPi does not contain a needed patch for displaying blame
information. The setup script will resolve the dependency by downloading the package from github. 
We are currently using the 0.3 branch, although the master branch might also work but is untested.

(optional)

- Markdown		>= 2.0.3
- docutils		>= 0.7
- python-memcached	>= 1.47

You only need these packages if you want README files in repositories be formatted using these libraries.

You can install all dependencies by executing

	python setup.py install

to let the setuptools resolve them all.

## Installation

Pyggi is fully WSGI compliant and can thus be easily integrated in your server infrastructure. Below is a sample configuration for Apache using mod_wsgi.

	<VirtualHost *>
		ServerName example.com

		WSGIDaemonProcess pyggi user=git group=git threads=5
		WSGIScriptAlias / /var/www/pyggi/pyggi.wsgi

		<Directory /var/www/pyggi>
			WSGIProcessGroup pyggi
			WSGIApplicationGroup %{GLOBAL}
			Order deny,allow
			Allow from all
		</Directory>
	</VirtualHost>

In addition you might have to change the git repository directory in "config.cfg" by setting the correct value for 'git__repositories'.

That's it. There's nothing more to do.

## License

pyggi is licensed under the BSD License. See LICENSE for more information.

The icons used are [famfamfam silk](http://www.famfamfam.com/lab/icons/silk/), which are licensed
under a [Creative Commons Attribution 2.5 License](http://creativecommons.org/licenses/by/2.5/)

