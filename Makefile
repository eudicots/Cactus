REPORTER = list
TIMEOUT = 1000

all: install

install:
	make clean
	python setup.py install
	make clean

clean:
	python setup.py clean
	rm -Rf dist
	rm -Rf Cactus.egg*

uninstall:
	rm -Rf /Library/Python/2.7/site-packages/Cactus-*.egg
	rm /usr/local/bin/cactus

test:
	nosetests

test-shell:
	make uninstall
	make install
	./tests/test.sh

.PHONY: install clean watch uninstall test test-shell