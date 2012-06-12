REPORTER = list
TIMEOUT = 1000
CACTUS = `which cactus`
SITE_PACKAGES = `python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`

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
	rm -Rf $(SITE_PACKAGES)/Cactus-*.egg
	rm $(CACTUS)

test:
	nosetests

test-shell:
	make uninstall
	make install
	./tests/test.sh

.PHONY: install clean watch uninstall test test-shell