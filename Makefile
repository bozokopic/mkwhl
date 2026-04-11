.POSIX:
.SUFFIXES:

PYTHON = python3

dist:
	$(PYTHON) -m mkwhl --src-include 'mkwhl/**/*' \
	                   --data man/mkwhl.1:share/man/man1/mkwhl.1

install:
	$(PYTHON) -m pip install .

editable:
	$(PYTHON) -m pip install -e .

check:
	$(PYTHON) -m flake8 mkwhl

clean:
	rm -rf build

.PHONY: dist install editable check clean
