install:
	python setup.py install
	make clean

uninstall:
	python setup.py uninstall

clean:
	rm -Rf build Cactus.egg-info dist

test:
	nosetests -s

shelltest:
	tests/test.sh

skeleton:
	rm -Rf skeleton.tar.gz
	tar  zcf skeleton.tar.gz --exclude='.*' skeleton

	echo 'data = """' > cactus/skeleton.py
	cat skeleton.tar.gz | base64 | fold -sw 60 >> cactus/skeleton.py
	echo '"""' >> cactus/skeleton.py
	rm -Rf skeleton.tar.gz

.PHONY: test skeleton