from pathlib import Path
import collections
import hashlib
import itertools
import typing
import zipfile

from mkwhl import common
from mkwhl import dist_info
from mkwhl import props


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
                 maintainers: list[tuple[str | None, str | None]] | None = None,  # NOQA
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
                 src_exclude_patterns: typing.Iterable[str] = ['**/__pycache__/**/*'],  # NOQA
                 python_tag: str = 'py3',
                 abi_tag: str = 'none',
                 platform_tag: str = 'any',
                 is_purelib: bool = True,
                 build: int | None = None
                 ) -> str:
    conf = common.get_conf(conf_path) if conf_path else {}
    project_conf = conf.get('project') if conf else {}

    entry_points_props = props.get_entry_points_props(
        project_conf=project_conf,
        scripts=scripts,
        gui_scripts=gui_scripts)

    metadata_props = props.get_metadata_props(
        project_conf=project_conf,
        name=name,
        version=version,
        description=description,
        readme_path=readme_path,
        requires_python=requires_python,
        license=license,
        authors=authors,
        maintainers=maintainers,
        keywords=keywords,
        classifiers=classifiers,
        urls=urls,
        dependencies=dependencies,
        optional_dependencies=optional_dependencies)

    wheel_props = props.get_wheel_props(python_tag=python_tag,
                                        abi_tag=abi_tag,
                                        platform_tag=platform_tag,
                                        is_purelib=is_purelib,
                                        build=build)

    if license_path is None:
        license_path_str = project_conf.get('license', {}).get('file')
        if license_path_str:
            license_path = Path(license_path_str)
    if license_path is None:
        for i in [Path('LICENSE'), Path('LICENSE.txt')]:
            if i.exists():
                license_path = i
                break

    wheel_name = common.get_wheel_name(name=metadata_props.name,
                                       version=metadata_props.version,
                                       build=build,
                                       python_tag=python_tag,
                                       abi_tag=abi_tag,
                                       platform_tag=platform_tag)
    wheel_path = build_dir / wheel_name

    dist_info_name = common.get_dist_info_name(name=metadata_props.name,
                                               version=metadata_props.version)
    dist_info_path = Path(dist_info_name)

    records = collections.deque()
    wheel_path.parent.mkdir(parents=True,
                            exist_ok=True)
    with zipfile.ZipFile(wheel_path, "w", zipfile.ZIP_DEFLATED) as whl:
        if editable:
            data = _get_editable_pth(src_dir)
            record = _whl_write(whl=whl,
                                path=Path(f'{metadata_props.name}.pth'),
                                data=data.encode('utf-8'))
            records.append(record)

        else:
            for src_path in _get_src_paths(src_dir, src_include_patterns,
                                           src_exclude_patterns):
                record = _whl_write(whl=whl,
                                    path=src_path.relative_to(src_dir),
                                    data=src_path.read_bytes())
                records.append(record)

        if license_path:
            record = _whl_write(whl=whl,
                                path=dist_info_path / license_path.name,
                                data=license_path.read_bytes())
            records.append(record)

        data = dist_info.get_entry_points_txt(entry_points_props)
        if data:
            record = _whl_write(whl=whl,
                                path=dist_info_path / 'entry_points.txt',
                                data=data.encode('utf-8'))
            records.append(record)

        data = dist_info.get_METADATA(metadata_props)
        record = _whl_write(whl=whl,
                            path=dist_info_path / 'METADATA',
                            data=data.encode('utf-8'))
        records.append(record)

        data = dist_info.get_WHEEL(wheel_props)
        record = _whl_write(whl=whl,
                            path=dist_info_path / 'WHEEL',
                            data=data.encode('utf-8'))
        records.append(record)

        record = common.WheelRecord(path=dist_info_path / 'RECORD',
                                    sha256=None,
                                    size=None)
        records.append(record)
        data = dist_info.get_RECORD(records)
        _whl_write(whl=whl,
                   path=record.path,
                   data=data.encode('utf-8'))

    return wheel_name


def _whl_write(whl: zipfile.ZipFile,
               path: Path,
               data: bytes
               ) -> common.WheelRecord:
    record = common.WheelRecord(path=path,
                                sha256=hashlib.sha256(data).digest(),
                                size=len(data))
    whl.writestr(str(record.path), data)
    return record


def _get_src_paths(src_dir: Path,
                   src_include_patterns: typing.Iterable[str],
                   src_exclude_patterns: typing.Iterable[str]
                   ) -> typing.Iterable[Path]:
    src_include_paths = set(itertools.chain.from_iterable(
        src_dir.glob(pattern) for pattern in src_include_patterns))
    src_exclude_paths = set(itertools.chain.from_iterable(
        src_dir.glob(pattern) for pattern in src_exclude_patterns))

    for src_path in src_include_paths:
        if src_path.is_dir():
            continue

        if src_path in src_exclude_paths:
            continue

        yield src_path


def _get_editable_pth(src_dir: Path) -> str:
    src_dir_repr = repr(str(src_dir.resolve()))

    return (f"import sys; "
            f"sys.path = [{src_dir_repr}, "
            f"*(i for i in sys.path if i != {src_dir_repr})]\n")
