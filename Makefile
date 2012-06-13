CACTUS = `which cactus`
SITE_PACKAGES = `python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`

all: install

build:
	python setup.py build

install:
	python setup.py install

clean:
	python setup.py clean
	rm -Rf ./dist
	rm -Rf ./Cactus.egg*

uninstall:
	rm -Rf $(SITE_PACKAGES)/Cactus-*.egg
	rm $(CACTUS)

test:
	nosetests

test-shell:
	sudo make uninstall
	sudo make clean
	sudo make install
	./tests/test.sh

.PHONY: build install clean watch uninstall test test-shell