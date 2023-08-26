from pathlib import Path
import collections
import hashlib
import io
import typing
import zipfile

from mkwhl import common


def create_wheel(src_paths: dict[Path, typing.Iterable[str]],
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
                 python_tag: str = 'py3',
                 abi_tag: str = 'none',
                 platform_tag: str = 'any',
                 is_purelib: bool = True,
                 build: int | None = None
                 ) -> str:
    conf = common.get_conf(conf_path) if conf_path else {}
    project_conf = conf.get('project') if conf else {}

    metadata_props = _get_metadata_props(
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

    wheel_props = _get_wheel_props(python_tag=python_tag,
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

    if scripts is None:
        scripts = project_conf.get('scripts', {})

    if gui_scripts is None:
        gui_scripts = project_conf.get('gui-scripts', {})

    wheel_name = _get_wheel_name(name=metadata_props.name,
                                 version=metadata_props.version,
                                 build=build,
                                 python_tag=python_tag,
                                 abi_tag=abi_tag,
                                 platform_tag=platform_tag)
    wheel_path = build_dir / wheel_name

    dist_info_path = _get_dist_info_path(name=metadata_props.name,
                                         version=metadata_props.version)

    records = collections.deque()
    wheel_path.parent.mkdir(parents=True,
                            exist_ok=True)
    with zipfile.ZipFile(wheel_path, "w") as whl:
        if editable:
            data = _get_editable_pth(k for k, v in src_paths.items() if v)
            record = _whl_write(whl=whl,
                                path=Path(f'{metadata_props.name}.pth'),
                                data=data.encode('utf-8'))
            records.append(record)

        else:
            for src_dir, src_dir_paths in src_paths.items():
                for path in _get_paths(src_dir / i for i in src_dir_paths):
                    record = _whl_write(whl=whl,
                                        path=path.relative_to(src_dir),
                                        data=path.read_bytes())
                    records.append(record)

        if license_path:
            record = _whl_write(whl=whl,
                                path=dist_info_path / license_path.name,
                                data=license_path.read_bytes())
            records.append(record)

        if scripts or gui_scripts:
            data = _get_entry_points_txt(console_scripts=scripts,
                                         gui_scripts=gui_scripts)
            record = _whl_write(whl=whl,
                                path=dist_info_path / 'entry_points.txt',
                                data=data.encode('utf-8'))
            records.append(record)

        data = _get_METADATA(metadata_props)
        record = _whl_write(whl=whl,
                            path=dist_info_path / 'METADATA',
                            data=data.encode('utf-8'))
        records.append(record)

        data = _get_WHEEL(wheel_props)
        record = _whl_write(whl=whl,
                            path=dist_info_path / 'WHEEL',
                            data=data.encode('utf-8'))
        records.append(record)

        record = common.WheelRecord(path=dist_info_path / 'RECORD',
                                    sha256=None,
                                    size=None)
        records.append(record)
        data = _get_RECORD(records)
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


def _get_paths(src_paths: typing.Iterable[Path]
               ) -> typing.Iterable[Path]:
    src_paths = collections.deque(src_paths)

    while src_paths:
        src_path = src_paths.popleft()

        if not src_path.is_dir():
            yield src_path
            continue

        if src_path.name == '__pycache__':
            continue

        src_paths.extend(src_path.iterdir())


def _get_metadata_props(project_conf: dict[str, typing.Any],
                        name: str | None,
                        version: str | None,
                        description: str | None,
                        readme_path: Path | None,
                        requires_python: str | None,
                        license: str | None,
                        authors: list[tuple[str | None, str | None]] | None,
                        maintainers: list[tuple[str | None, str | None]] | None,  # NOQA
                        keywords: list[str] | None,
                        classifiers: list[str] | None,
                        urls: dict[str, str] | None,
                        dependencies: list[str] | None,
                        optional_dependencies: dict[str, list[str]] | None,
                        ) -> common.MetadataProps:
    if name is None:
        name = project_conf.get('name')
    if name is None:
        raise Exception('name not provided')
    name = common.normalize_name(name)

    if version is None:
        version = project_conf.get('version')
    if version is None:
        raise Exception('version not provided')
    version = common.parse_version(version)

    if description is None:
        description = project_conf.get('description')

    readme_content_type = None
    if readme_path is None:
        readme = project_conf.get('readme')
        if isinstance(readme, str):
            readme_path = Path(readme)
        elif isinstance(readme, dict):
            readme_path = Path(readme['file']) if 'file' in readme else None
            readme_content_type = readme.get('content-type')
    if readme_path and readme_content_type is None:
        if readme_path.suffix == '.rst':
            readme_content_type = 'text/x-rst'
        elif readme_path.suffix == '.md':
            readme_content_type = 'text/markdown'
        elif readme_path.suffix == '.txt':
            readme_content_type = 'text/plain'

    if requires_python is None:
        requires_python = project_conf.get('requires-python')

    if license is None:
        license = project_conf.get('license', {}).get('text')

    if authors is None:
        authors = [(i.get('name'), i.get('email'))
                   for i in project_conf.get('authors', [])]
    author = ', '.join(name
                       for name, _ in authors
                       if name is not None) or None
    author_email = ', '.join(f'"{name}" <{email}>'
                             for name, email in authors
                             if email is not None) or None

    if maintainers is None:
        maintainers = [(i.get('name'), i.get('email'))
                       for i in project_conf.get('maintainers', [])]
    maintainer = ', '.join(name
                           for name, _ in maintainers
                           if name is not None) or None
    maintainer_email = ', '.join(f'"{name}" <{email}>'
                                 for name, email in maintainers
                                 if email is not None) or None

    if classifiers is None:
        classifiers = project_conf.get('classifiers', [])

    if urls is None:
        urls = project_conf.get('urls', {})

    if dependencies is None:
        dependencies = project_conf.get('dependencies', [])

    provides_extras = collections.deque()
    requires_externals = collections.deque()
    if optional_dependencies is None:
        optional_dependencies = project_conf.get('optional-dependencies', {})
    for k, v in optional_dependencies.items():
        provides_extras.append(k)
        for i in v:
            requires_externals.append(f"{i}; extra == '{k}'")

    return common.MetadataProps(name=name,
                                version=version,
                                platforms=[],
                                supported_platforms=[],
                                summary=description,
                                description_path=readme_path,
                                description_content_type=readme_content_type,
                                keywords=keywords,
                                home_page=None,
                                download_url=None,
                                author=author,
                                author_email=author_email,
                                maintainer=maintainer,
                                maintainer_email=maintainer_email,
                                license=license,
                                classifiers=classifiers,
                                requires_dists=dependencies,
                                requires_python=requires_python,
                                requires_externals=requires_externals,
                                project_urls=urls,
                                provides_extras=provides_extras)


def _get_wheel_props(python_tag: str,
                     abi_tag: str,
                     platform_tag: str,
                     is_purelib: bool,
                     build: int | None
                     ) -> common.WheelProps:
    tags = list(common.parse_tags(python_tag=python_tag,
                                  abi_tag=abi_tag,
                                  platform_tag=platform_tag))

    return common.WheelProps(is_purelib=is_purelib,
                             tags=tags,
                             build=build)


def _get_wheel_name(name: str,
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


def _get_dist_info_path(name: str,
                        version: str
                        ) -> Path:
    return Path(f"{name}-{version}.dist-info")


def _get_entry_points_txt(console_scripts: dict[str, str],
                          gui_scripts: dict[str, str]
                          ) -> str:
    stream = io.StringIO()

    if console_scripts:
        stream.write("[console_scripts]\n")

        for name, path in console_scripts.items():
            stream.write(f"{name} = {path}")

    if gui_scripts:
        stream.write("[gui_scripts]\n")

        for name, path in gui_scripts.items():
            stream.write(f"{name} = {path}")

    return stream.getvalue()


def _get_METADATA(props: common.MetadataProps) -> str:
    stream = io.StringIO()

    stream.write("Metadata-Version: 2.1\n")
    stream.write(f"Name: {props.name}\n")
    stream.write(f"Version: {props.version}\n")

    for platform in props.platforms:
        stream.write(f"Platform: {platform}\n")

    for supported_platform in props.supported_platforms:
        stream.write(f"Supported-Platform: {supported_platform}\n")

    if props.summary is not None:
        stream.write(f"Summary: {props.summary}\n")

    if props.description_content_type is not None:
        stream.write(f"Description-Content-Type: {props.description_content_type}\n")  # NOQA

    if props.keywords is not None:
        stream.write(f"Keywords: {','.join(props.keywords)}\n")

    if props.home_page is not None:
        stream.write(f"Home-page: {props.home_page}\n")

    if props.download_url is not None:
        stream.write(f"Download-URL: {props.download_url}\n")

    if props.author is not None:
        stream.write(f"Author: {props.author}\n")

    if props.author_email is not None:
        stream.write(f"Author-email: {props.author_email}\n")

    if props.maintainer is not None:
        stream.write(f"Maintainer: {props.maintainer}\n")

    if props.maintainer_email is not None:
        stream.write(f"Maintainer-email: {props.maintainer_email}\n")

    if props.license is not None:
        stream.write(f"License: {props.license}\n")

    for classifier in props.classifiers:
        stream.write(f"Classifier: {classifier}\n")

    for requires_dist in props.requires_dists:
        stream.write(f"Requires-Dist: {requires_dist}\n")

    if props.requires_python is not None:
        stream.write(f"Requires-Python: {props.requires_python}\n")

    for requires_external in props.requires_externals:
        stream.write(f"Requires-External: {requires_external}\n")

    for url_name, url_path in props.project_urls.items():
        stream.write(f"Project-URL: {url_name}, {url_path}\n")

    for provides_extra in props.provides_extras:
        stream.write(f"Provides-Extra: {provides_extra}\n")

    if props.description_path:
        description = props.description_path.read_text('utf-8')
        stream.write(f"\n{description}")

    return stream.getvalue()


def _get_WHEEL(props: common.WheelProps) -> str:
    stream = io.StringIO()

    stream.write("Wheel-Version: 1.0\n")
    stream.write("Generator: mkwhl\n")

    is_purelib = 'true' if props.is_purelib else 'false'
    stream.write(f"Root-Is-Purelib: {is_purelib}\n")

    for tag in props.tags:
        stream.write(f"Tag: {tag}\n")

    if props.build is not None:
        stream.write(f"Build: {props.build}\n")

    return stream.getvalue()


def _get_RECORD(records: typing.Iterable[common.WheelRecord]) -> str:
    stream = io.StringIO()

    for record in records:
        stream.write(f"{record.path},")

        sha256 = (f"sha256={common.urlsafe_b64encode_nopad(record.sha256)}"
                  if record.sha256 is not None else '')
        stream.write(f"{sha256},")

        size = str(record.size) if record.size is not None else ''
        stream.write(f"{size}\n")

    return stream.getvalue()


def _get_editable_pth(src_dirs: typing.Iterable[Path]) -> str:
    src_dirs_repr = repr({str(src_dir.resolve()) for src_dir in src_dirs})

    return (f"import sys; "
            f"sys.path = [*{src_dirs_repr}, "
            f"*(i for i in sys.path if i not in {src_dirs_repr})]\n")
