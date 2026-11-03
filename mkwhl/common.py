"""Shared structures and functions"""

from collections.abc import Collection
from pathlib import Path
import base64
import sys
import typing

if sys.version_info[:2] >= (3, 11):
    import tomllib as toml
else:
    import tomli as toml


class EntryPointsProps(typing.NamedTuple):
    """Entry point properties"""
    console_scripts: dict[str, str]
    gui_scripts: dict[str, str]


class MetadataProps(typing.NamedTuple):
    """Metadata properties"""
    name: str
    version: str
    platforms: Collection[str]
    supported_platforms: Collection[str]
    summary: str | None
    description_path: Path | None
    description_content_type: str | None
    keywords: Collection[str]
    author: str | None
    author_email: str | None
    maintainer: str | None
    maintainer_email: str | None
    license_expression: str | None
    license_file_paths: dict[str, Path]
    classifiers: Collection[str]
    requires_dists: Collection[str]
    requires_python: str | None
    requires_externals: Collection[str]
    project_urls: dict[str, str]
    provides_extras: Collection[str]
    import_names: Collection[str]
    import_namespaces: Collection[str]


class WheelProps(typing.NamedTuple):
    """Wheel properties"""
    is_purelib: bool
    tags: Collection[str]
    build: str | None


class WheelRecord(typing.NamedTuple):
    """Single wheel record"""
    path: Path
    sha256: bytes | None
    size: int | None


class Project(typing.NamedTuple):
    """Project definition"""
    conf: dict[str, typing.Any]
    path: Path


class Person(typing.NamedTuple):
    """Person"""
    name: str | None
    email: str | None


def get_conf(path: Path = Path('pyproject.toml')
             ) -> dict[str, typing.Any]:
    """Get TOML configuration"""
    conf_str = path.read_text('utf-8')
    return toml.loads(conf_str)


def urlsafe_b64encode_nopad(data: bytes) -> str:
    """Record hash encoding"""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')
