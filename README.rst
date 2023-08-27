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


Requirements
------------

* python >=3.10


Install
-------

::

    $ pip install mkwhl


Command line tool
-----------------

Usage::

    $ mkwhl --help


`pyproject.toml` build backend
------------------------------

TODO


Python API
----------

TODO


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
