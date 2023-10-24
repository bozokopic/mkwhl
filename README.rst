.. _PEP517: https://peps.python.org/pep-0517
.. _PEP660: https://peps.python.org/pep-0660
.. _project metadata: https://packaging.python.org/en/latest/specifications/declaring-project-metadata
.. _binary distribution format: https://packaging.python.org/en/latest/specifications/binary-distribution-format

mkwhl - python wheel creation utility
=====================================

Create Python wheel based on `pyproject.toml` configuration and/or provided
arguments. Wheels can be created by:

* running command line tool
* `pyproject.toml` build backend
* calling `mkwhl.create_wheel` function

Goal of this project is to provide simple and minimal utility based on
accepted PEPs. Usage of `pyproject.toml` should not be mandatory and
each `pyproject.toml` property should be overridable by provided arguments.
Functionality should not depend on specific project's repository layout.
User is responsible for providing correct configuration/arguments
(e.g. python/abi/platform tags) without additional "automatic" detection.

Only responsibility of `mkwhl` is creation of wheels. Any kind of
preprocessing, including compilation of native extensions, should be done
prior to `mkwhl` execution.


Requirements
------------

* python >=3.10


Install
-------

PyPI python package::

    $ pip install mkwhl

Archlinux AUR::

    $ yay -S mkwhl


Command line tool
-----------------

Usage::

    $ mkwhl --help

`mkwhl` will create new wheel in ``--build-dir`` (defaults to ``build``)
containing files from ``--src-dir`` (defaults to ``.``). Files in ``--src-dir``
are selected based on ``--src-include`` and ``--src-exclude`` patterns
used as `pathlib.Path.glob` arguments applied to ``--src-dir``
(``--src-exclude`` patterns are prioritized over ``--src-include`` patterns).
If ``--skip-conf`` is not set, project properties, which are not explicitly
overridden by command line arguments, are read from ``--conf`` (defaults to
``pyproject.toml``) as defined by `project metadata`_. When wheel is created,
wheel name is printed to stdout (unless ``--quiet`` flag is set).

For more information::

    $ man 1 mkwhl


`pyproject.toml` build backend
------------------------------

`mkwhl` implements build backend according to PEP517_ and PEP660_. To use
`mkwhl` as build backend, add following to pyproject.toml::

    [build-system]
    requires = ["mkwhl"]
    build-backend = "mkwhl"

Wheel will be build based on pyproject.toml `project metadata`_ and additional
``[tool.mkwhl]`` properties:

* `src-dir` (string)

  Source root directory. If this property is not set, existence of ``src_py``
  or ``src`` directory is checked and used if available.

* `license-path` (string)

  Optional path to license file.

* `src-include-patterns` (list of strings)

  List of strings used as `pathlib.Path.glob` patterns applied to `src_dir`.
  These patterns specify which files should be included as part of built
  wheel. If not set, ``['**/*']`` is assumed.

* `src-exclude-patterns` (list of strings)

  List of strings used as `pathlib.Path.glob` patterns applied to `src_dir`.
  These patterns specify which files should not be included as part of built
  wheel. This patterns take priority over `src-include-patterns`. If not set,
  ``['**/__pycache__/**/*']`` is assumed.

* `data-paths` (list of tables)

  Optional data paths where list element is table with ``src`` and ``dst``
  keys referencing source and destination path strings.

* 'python-tag' (string)

  Python tag (see `binary distribution format`_). If not set, ``py3`` is
  assumed.

* 'abi-tag' (string)

  ABI tag (see `binary distribution format`_). If not set, ``none`` is
  assumed.

* `build-tag` (integer)

  Optional build tag (see `binary distribution format`_).

* 'platform-tag' (string)

  Python tag (see `binary distribution format`_). If not set, ``any`` is
  assumed.

* 'is-purelib' (boolean)

  Is purelib (see `binary distribution format`_). If not set, ``true`` is
  assumed.

* `optional-dependencies` (list of strings)

  List of strings used as keys in pyproject.toml
  ``[project.optional-dependencies]``. These dependencies are required as part
  of build virtual environment. If not set, ``['dev']`` is assumed.


Python API
----------

In addition to command line interface and build backend, package `mkwhl`
exposes single function::

    def create_wheel(src_dir: Path,
                     build_dir: Path,
                     *,
                     name: str | None = None,
                     version: str | None = None,
                     description: str | None = None,
                     readme_path: Path | None = None,
                     requires_python: str | None = None,
                     license: str | None = None,
                     license_path: Path | None = None,
                     authors: list[tuple[str | None, str | None]] | None = None,
                     maintainers: list[tuple[str | None, str | None]] | None = None,
                     keywords: list[str] | None = None,
                     classifiers: list[str] | None = None,
                     urls: dict[str, str] | None = None,
                     scripts: dict[str, str] | None = None,
                     gui_scripts: dict[str, str] | None = None,
                     dependencies: list[str] | None = None,
                     optional_dependencies: dict[str, list[str]] | None = None,
                     conf_path: Path | None = Path('pyproject.toml'),
                     editable: bool = False,
                     src_include_patterns: typing.Iterable[str] = ['**/*'],
                     src_exclude_patterns: typing.Iterable[str] = ['**/__pycache__/**/*'],
                     data_paths: list[tuple[Path, Path]] = [],
                     build_tag: int | None = None,
                     python_tag: str = 'py3',
                     abi_tag: str = 'none',
                     platform_tag: str = 'any',
                     is_purelib: bool = True
                     ) -> str:
        """Create wheel and return wheel name

        Argument `src_dir` is path to source root directory.

        Argument `build_dir` is path to directory where resulting wheel will be
        created.

        If one of arguments `name`, `version`, `description`, `readme_path`,
        `requires_python`, `license`, `authors`, `maintainers`, `keywords`,
        `classifiers`, `urls`, `scripts`, `gui_scripts`, `dependencies` or
        `optional_dependencies` is ``None``, associated resulting property is
        set based on project configuration read from pyproject.

        Arguments `authors` and `maintainers` are structured as list of tuples
        where first tuple element represents name and second tuple element
        represents email.

        If `conf_path` is ``None``, resulting wheel will be created based only
        on provided arguments without parsing of pyproject configuration.

        Arguments `src_include_patterns` and `src_exclude_patterns` provide
        list of strings used as `pathlib.Path.glob` patterns applied to
        `src_dir`. Include patterns specify all files that will be included in
        resulting wheel. All files specified by exclude patterns will not be
        included in resulting wheel, even if same file is specified by include
        pattern.

        Argument `data_paths` defines list of (source, destination) paths to be
        included in wheel's data directory.

        """


License
-------

mkwhl - python wheel creation utility

Copyright (C) 2023 Bozo Kopic

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
