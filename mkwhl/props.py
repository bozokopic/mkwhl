"""Create .dist-info properties based on configuration and arguments"""

from collections.abc import Collection, Iterable
from pathlib import Path
import collections
import datetime

import packaging.licenses
import packaging.markers
import packaging.requirements
import packaging.tags
import packaging.version
import packaging.utils

from mkwhl import common


def get_entry_points_props(project: common.Project | None,
                           scripts: dict[str, str] | None,
                           gui_scripts: dict[str, str] | None
                           ) -> common.EntryPointsProps:
    """Create entry point properties

    If argument `scripts` or `gui_scripts` is ``None``, associated resulting
    property is set based on project configuration.

    """
    project_conf = project.conf if project else {}

    if scripts is None:
        scripts = project_conf.get('scripts', {})

    if gui_scripts is None:
        gui_scripts = project_conf.get('gui-scripts', {})

    return common.EntryPointsProps(console_scripts=scripts,
                                   gui_scripts=gui_scripts)


def get_metadata_props(project: common.Project | None,
                       name: str | None,
                       version: str | None,
                       description: str | None,
                       readme_path: Path | None,
                       requires_python: str | None,
                       license: str | None,
                       license_paths: Collection[Path] | None,
                       authors: Collection[common.Person] | None,
                       maintainers: Collection[common.Person] | None,
                       keywords: Collection[str] | None,
                       classifiers: Collection[str] | None,
                       urls: dict[str, str] | None,
                       dependencies: Collection[str] | None,
                       optional_dependencies: dict[str, Collection[str]] | None,  # NOQA
                       ) -> common.MetadataProps:
    """Create metadata properties

    If any of the arguments (except `project`) is ``None``, associated
    resulting property is set based on project configuration.

    """
    if name is None:
        name = project.conf.get('name') if project else None
    if name is None:
        raise Exception('name not provided')
    name = packaging.utils.canonicalize_name(name)

    if version is None:
        version = project.conf.get('version') if project else None
    if version is None:
        raise Exception('version not provided')
    version = _parse_version(version)

    if description is None and project:
        description = project.conf.get('description')

    readme_content_type = None
    if readme_path is None and project:
        readme = project.conf.get('readme')
        if isinstance(readme, str):
            readme_path = project.path / readme
        elif isinstance(readme, dict):
            readme_path = (project.path / readme['file'] if 'file' in readme
                           else None)
            readme_content_type = readme.get('content-type')
    if readme_path and readme_content_type is None:
        if readme_path.suffix == '.rst':
            readme_content_type = 'text/x-rst'
        elif readme_path.suffix == '.md':
            readme_content_type = 'text/markdown'
        elif readme_path.suffix == '.txt':
            readme_content_type = 'text/plain'

    if requires_python is None and project:
        requires_python = project.conf.get('requires-python')

    if license is None and project:
        license = project.conf.get('license')
        if isinstance(license, dict):
            license = license.get('text')
    if license is not None:
        license = packaging.licenses.canonicalize_license_expression(license)

    license_file_paths = _get_license_file_paths(project, license_paths)

    if authors is None:
        authors = ([common.Person(name=i.get('name'),
                                  email=i.get('email'))
                    for i in project.conf.get('authors', [])]
                   if project else [])
    author = _get_person_names(authors) or None
    author_email = _get_person_emails(authors) or None

    if maintainers is None:
        maintainers = ([common.Person(name=i.get('name'),
                                      email=i.get('email'))
                        for i in project.conf.get('maintainers', [])]
                       if project else [])
    maintainer = _get_person_names(maintainers) or None
    maintainer_email = _get_person_emails(maintainers) or None

    if keywords is None:
        keywords = project.conf.get('keywords', []) if project else []

    if classifiers is None:
        classifiers = (project.conf.get('classifiers', [])
                       if project else [])

    if urls is None:
        urls = project.conf.get('urls', {}) if project else {}

    if dependencies is None:
        dependencies = project.conf.get('dependencies', []) if project else []

    if optional_dependencies is None:
        optional_dependencies = (project.conf.get('optional-dependencies', {})
                                 if project else {})
    optional_dependencies = _normalize_optional_dependencies(
        optional_dependencies)

    requires_dists = _get_requires_dists(dependencies, optional_dependencies)

    provides_extras = optional_dependencies.keys()

    return common.MetadataProps(name=name,
                                version=version,
                                platforms=[],
                                supported_platforms=[],
                                summary=description,
                                description_path=readme_path,
                                description_content_type=readme_content_type,
                                keywords=keywords,
                                author=author,
                                author_email=author_email,
                                maintainer=maintainer,
                                maintainer_email=maintainer_email,
                                license_expression=license,
                                license_file_paths=license_file_paths,
                                classifiers=classifiers,
                                requires_dists=requires_dists,
                                requires_python=requires_python,
                                requires_externals=[],
                                project_urls=urls,
                                provides_extras=provides_extras,
                                import_names=[],
                                import_namespaces=[])


def get_wheel_props(build_tag: str | None,
                    python_tag: str,
                    abi_tag: str,
                    platform_tag: str,
                    is_purelib: bool
                    ) -> common.WheelProps:
    """Create wheel properties"""
    tags = list(_parse_tags(python_tag=python_tag,
                            abi_tag=abi_tag,
                            platform_tag=platform_tag))

    return common.WheelProps(is_purelib=is_purelib,
                             tags=tags,
                             build=build_tag)


def _get_license_file_paths(project: common.Project | None,
                            license_paths: Collection[Path] | None
                            ) -> dict[str, Path]:
    license_file_paths = {}
    project_path = project.path if project else Path('.')

    if license_paths is None:
        license_paths = collections.deque()

        if project:
            for pattern in project.conf.get('license-files', ['LICENSE',
                                                              'LICENSE.txt']):
                for license_path in project_path.glob(pattern):
                    if license_path.is_file():
                        license_paths.append(license_path)

    for license_path in sorted(license_paths):
        try:
            license_file = license_path.relative_to(project_path).as_posix()

        except ValueError:
            license_file = license_path.name

        license_file_paths[license_file] = license_path

    return license_file_paths


def _get_requires_dists(dependencies: Collection[str],
                        optional_dependencies: dict[str, Collection[str]],
                        ) -> Collection[str]:
    requires_dists = collections.deque(dependencies)

    for k, v in optional_dependencies.items():
        for i in v:
            req = packaging.requirements.Requirement(i)
            req.marker = packaging.markers.Marker(
                f"({req.marker}) and extra == '{k}'" if req.marker
                else f"extra == '{k}'")

            requires_dists.append(str(req))

    return requires_dists


def _get_person_names(persons: Collection[common.Person]) -> str:
    return ', '.join(person.name
                     for person in persons
                     if person.name is not None and person.email is None)


def _get_person_emails(persons: Collection[common.Person]) -> str:
    return ', '.join((person.email if person.name is None
                      else f'"{person.name}" <{person.email}>')
                     for person in persons
                     if person.email is not None)


def _parse_version(version: str) -> str:
    if version.endswith('dev'):
        now = datetime.datetime.now(datetime.timezone.utc)
        version += now.strftime("%Y%m%d")

    return str(packaging.version.parse(version))


def _parse_tags(python_tag: str,
                abi_tag: str,
                platform_tag: str
                ) -> Iterable[str]:
    tags = packaging.tags.parse_tag(f"{python_tag}-{abi_tag}-{platform_tag}")

    for tag in tags:
        yield str(tag)


def _normalize_optional_dependencies(optional_dependencies: dict[str, Collection[str]]  # NOQA
                                     ) -> dict[str, Collection[str]]:
    result = collections.defaultdict(collections.deque)

    for group, dependencies in optional_dependencies.items():
        result[packaging.utils.canonicalize_name(group)].extend(dependencies)

    return dict(result)
