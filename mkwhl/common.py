from pathlib import Path
import base64
import datetime
import re
import typing

import packaging.tags
import packaging.version
import tomli


now: datetime.datetime = datetime.datetime.now()


class EntryPointsProps(typing.NamedTuple):
    console_scripts: dict[str, str]
    gui_scripts: dict[str, str]


class MetadataProps(typing.NamedTuple):
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
    is_purelib: bool
    tags: typing.Iterable[str]
    build: int | None


class WheelRecord(typing.NamedTuple):
    path: Path
    sha256: bytes | None
    size: int | None


def get_conf(path: Path = Path('pyproject.toml')) -> dict[str, typing.Any]:
    conf_str = path.read_text()
    return tomli.loads(conf_str)


def urlsafe_b64encode_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_version(version: str) -> str:
    if version.endswith('dev'):
        version += now.strftime("%Y%m%d")

    return str(packaging.version.parse(version))


def parse_tags(python_tag: str,
               abi_tag: str,
               platform_tag: str
               ) -> typing.Iterable[str]:
    tags = packaging.tags.parse_tag(f"{python_tag}-{abi_tag}-{platform_tag}")

    for tag in tags:
        yield str(tag)


def get_wheel_name(name: str,
                   version: str,
                   build: int | None,
                   python_tag: str,
                   abi_tag: str,
                   platform_tag: str
                   ) -> str:
    wheel_name = f"{name}-{version}"

    if build is not None:
        wheel_name += f"-{build}"

    wheel_name += f"-{python_tag}-{abi_tag}-{platform_tag}.whl"
    return wheel_name


def get_dist_info_name(name: str,
                       version: str
                       ) -> str:
    return f"{name}-{version}.dist-info"
