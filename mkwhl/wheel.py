"""Create wheel API"""

from collections.abc import Collection, Iterable
from pathlib import Path
import collections
import hashlib
import itertools
import stat
import zipfile

import packaging.utils

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
                 license_paths: Collection[Path] | None = None,
                 authors: Collection[common.Person] | None = None,
                 maintainers: Collection[common.Person] | None = None,
                 keywords: Collection[str] | None = None,
                 classifiers: Collection[str] | None = None,
                 urls: dict[str, str] | None = None,
                 scripts: dict[str, str] | None = None,
                 gui_scripts: dict[str, str] | None = None,
                 dependencies: Collection[str] | None = None,
                 optional_dependencies: dict[str, Collection[str]] | None = None,  # NOQA
                 conf_path: Path | None = Path('pyproject.toml'),
                 editable: bool = False,
                 src_include_patterns: Iterable[str] = ['**/*'],
                 src_exclude_patterns: Iterable[str] = ['**/__pycache__/**/*'],
                 data_paths: Iterable[tuple[Path, Path]] = [],
                 build_tag: str | None = None,
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
    `requires_python`, `license`, `license_paths`, `authors`, `maintainers`,
    `keywords`, `classifiers`, `urls`, `scripts`, `gui_scripts`, `dependencies`
    or `optional_dependencies` is ``None``, associated resulting property is
    set based on project configuration read from pyproject.

    If `conf_path` is ``None``, resulting wheel will be created based only
    on provided arguments without parsing of pyproject configuration.

    Arguments `src_include_patterns` and `src_exclude_patterns` provide
    list of strings used as `pathlib.Path.glob` patterns applied to
    `src_dir`. Include patterns specify all files that will be included in
    resulting wheel. All files specified by exclude patterns will not be
    included in resulting wheel, even if same file is specified by include
    pattern.

    Argument `data_paths` defines iterable of (source, destination) paths to be
    included in wheel's data directory.

    """
    conf = common.get_conf(conf_path) if conf_path else {}
    project = (common.Project(conf=conf['project'],
                              path=conf_path.parent)
               if 'project' in conf else None)

    entry_points_props = props.get_entry_points_props(
        project=project,
        scripts=scripts,
        gui_scripts=gui_scripts)

    metadata_props = props.get_metadata_props(
        project=project,
        name=name,
        version=version,
        description=description,
        readme_path=readme_path,
        requires_python=requires_python,
        license=license,
        license_paths=license_paths,
        authors=authors,
        maintainers=maintainers,
        keywords=keywords,
        classifiers=classifiers,
        urls=urls,
        dependencies=dependencies,
        optional_dependencies=optional_dependencies)

    wheel_props = props.get_wheel_props(build_tag=build_tag,
                                        python_tag=python_tag,
                                        abi_tag=abi_tag,
                                        platform_tag=platform_tag,
                                        is_purelib=is_purelib)

    wheel_name = _get_wheel_name(name=metadata_props.name,
                                 version=metadata_props.version,
                                 build_tag=build_tag,
                                 python_tag=python_tag,
                                 abi_tag=abi_tag,
                                 platform_tag=platform_tag)

    wheel_path = build_dir / wheel_name
    tmp_wheel_path = build_dir / f'{wheel_name}.tmp'

    dist_info_name = _get_dist_info_name(name=metadata_props.name,
                                         version=metadata_props.version)
    dist_info_path = Path(dist_info_name)

    data_name = _get_data_name(name=metadata_props.name,
                               version=metadata_props.version)
    data_path = Path(data_name)

    records = collections.deque()
    build_dir.mkdir(parents=True,
                    exist_ok=True)

    try:
        with zipfile.ZipFile(tmp_wheel_path, "w", zipfile.ZIP_DEFLATED) as whl:
            if editable:
                data = _get_editable_pth(src_dir)
                record = _whl_write(whl=whl,
                                    path=Path(f'{metadata_props.name}.pth'),
                                    data=data.encode('utf-8'))
                records.append(record)

            else:
                for src_path in sorted(_get_src_paths(src_dir,
                                                      src_include_patterns,
                                                      src_exclude_patterns)):
                    record = _whl_write(whl=whl,
                                        path=src_path.relative_to(src_dir),
                                        data=src_path)
                    records.append(record)

                for src_path, dst_path in sorted(data_paths):
                    record = _whl_write(
                        whl=whl,
                        path=data_path / 'data' / dst_path,
                        data=src_path)
                    records.append(record)

            license_file_paths = metadata_props.license_file_paths
            for license_file, license_path in license_file_paths.items():
                record = _whl_write(
                    whl=whl,
                    path=dist_info_path / 'licenses' / license_file,
                    data=license_path)
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

        tmp_wheel_path.replace(wheel_path)

    finally:
        tmp_wheel_path.unlink(missing_ok=True)

    return wheel_name


def _whl_write(whl: zipfile.ZipFile,
               path: Path,
               data: Path | bytes
               ) -> common.WheelRecord:
    if isinstance(data, Path):
        mode = 0o755 if data.stat().st_mode & 0o111 else 0o644
        data = data.read_bytes()

    else:
        mode = 0o644

    record = common.WheelRecord(path=path,
                                sha256=hashlib.sha256(data).digest(),
                                size=len(data))

    info = zipfile.ZipInfo(path.as_posix())
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (stat.S_IFREG | mode) << 16

    whl.writestr(info, data)

    return record


def _get_src_paths(src_dir: Path,
                   src_include_patterns: Iterable[str],
                   src_exclude_patterns: Iterable[str]
                   ) -> Iterable[Path]:
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
    return f'{src_dir.resolve()}\n'


def _get_wheel_name(name: packaging.utils.NormalizedName,
                    version: str,
                    build_tag: str | None,
                    python_tag: str,
                    abi_tag: str,
                    platform_tag: str
                    ) -> str:
    wheel_name = f"{name.replace('-', '_')}-{version}"

    if build_tag is not None:
        wheel_name += f"-{build_tag}"

    wheel_name += f"-{python_tag}-{abi_tag}-{platform_tag}.whl"
    return wheel_name


def _get_dist_info_name(name: packaging.utils.NormalizedName,
                        version: str
                        ) -> str:
    return f"{name.replace('-', '_')}-{version}.dist-info"


def _get_data_name(name: packaging.utils.NormalizedName,
                   version: str
                   ) -> str:
    return f"{name.replace('-', '_')}-{version}.data"
