"""Shared structures and functions"""

from pathlib import Path
import base64
import datetime
import re
import sys
import typing

import packaging.tags
import packaging.version

if sys.version_info[:2] >= (3, 11):
    import tomllib as toml
else:
    import tomli as toml


now: datetime.datetime = datetime.datetime.now()
"""Time instance of module loading"""


class EntryPointsProps(typing.NamedTuple):
    """Entry point properties"""
    console_scripts: dict[str, str]
    gui_scripts: dict[str, str]


class MetadataProps(typing.NamedTuple):
    """Metadata properties"""
    name: str
    version: str
    platforms: typing.Iterable[str]
    supported_platforms: typing.Iterable[str]
    summary: str | None
    description_path: Path | None
    description_content_type: str | None
    keywords: typing.Iterable[str] | None
    home_page: str | None
    download_url: str | None
    author: str | None
    author_email: str | None
    maintainer: str | None
    maintainer_email: str | None
    license: str | None
    classifiers: typing.Iterable[str]
    requires_dists: typing.Iterable[str]
    requires_python: str | None
    requires_externals: typing.Iterable[str]
    project_urls: dict[str, str]
    provides_extras: typing.Iterable[str]


class WheelProps(typing.NamedTuple):
    """Wheel properties"""
    is_purelib: bool
    tags: typing.Iterable[str]
    build: int | None


class WheelRecord(typing.NamedTuple):
    """Single wheel record"""
    path: Path
    sha256: bytes | None
    size: int | None


class Project(typing.NamedTuple):
    """Project definition"""
    conf: dict[str, typing.Any]
    path: Path


def get_conf(path: Path = Path('pyproject.toml')
             ) -> dict[str, typing.Any]:
    """Get TOML configuration"""
    conf_str = path.read_text()
    return toml.loads(conf_str)


def urlsafe_b64encode_nopad(data: bytes) -> str:
    """Record hash encoding"""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def normalize_name(name: str) -> str:
    """Normalize project name"""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_version(version: str) -> str:
    """Parse and return canonical version identifier"""
    if version.endswith('dev'):
        version += now.strftime("%Y%m%d")

    return str(packaging.version.parse(version))


def parse_tags(python_tag: str,
               abi_tag: str,
               platform_tag: str
               ) -> typing.Iterable[str]:
    """Create all tags from possibly compressed tag segments"""
    tags = packaging.tags.parse_tag(f"{python_tag}-{abi_tag}-{platform_tag}")

    for tag in tags:
        yield str(tag)


def get_wheel_name(name: str,
                   version: str,
                   build_tag: int | None,
                   python_tag: str,
                   abi_tag: str,
                   platform_tag: str
                   ) -> str:
    """Get wheel name

    Provided name should be previously normalized (see `normalize_name`)
    and version should be in canonical form (see `parse_version`).

    """
    wheel_name = f"{name.replace('-', '_')}-{version}"

    if build_tag is not None:
        wheel_name += f"-{build_tag}"

    wheel_name += f"-{python_tag}-{abi_tag}-{platform_tag}.whl"
    return wheel_name


def get_dist_info_name(name: str,
                       version: str
                       ) -> str:
    """Get full name of .dist-info folder

    Provided name should be previously normalized (see `normalize_name`)
    and version should be in canonical form (see `parse_version`).

    """
    return f"{name.replace('-', '_')}-{version}.dist-info"
