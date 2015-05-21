SHELL = /bin/bash

dev: \
	clean \
	_setupVirtualenv

clean:
	rm -fr env/ log/ state/
	find ./ -name *.pyc -delete

qa:
	source ./env/bin/activate; \
	nosetests

install:
	source ./env/bin/activate; \
	python setup.py install

_setupVirtualenv:
	virtualenv env
	source ./env/bin/activate; \
	pip install -r requirements.txt
