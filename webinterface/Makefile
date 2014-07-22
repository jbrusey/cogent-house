init:
	install -m 0644 etc/cogent-web /etc/apache2/sites-available/
	a2enmod  proxy_http
	a2ensite cogent-web
	install -m 0644 etc/webinterface.conf /etc/init/


develop:
	python setup.py develop

tests:
	paster serve test.ini & nosetests --cover-html cogentviewer/tests/
	killall paster

