.POSIX:
.SUFFIXES:

PYTHON = python3

dist:
	$(PYTHON) -m mkwhl

install:
	$(PYTHON) -m pip install .

editable:
	$(PYTHON) -m pip install -e .

clean:
	rm -rf build
