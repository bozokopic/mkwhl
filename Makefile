.POSIX:
.SUFFIXES:

PYTHON = python3

dist:
	$(PYTHON) -m mkwhl

install:
	$(PYTHON) -m pip install .

editable:
	$(PYTHON) -m pip install -e .

check:
	$(PYTHON) -m flake8 mkwhl

clean:
	rm -rf build
