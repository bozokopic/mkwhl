"""Create .dist-info properties based on configuration and arguments"""

from pathlib import Path
import collections

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

    if gui_scripts is None and project:
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
                       authors: list[tuple[str | None, str | None]] | None,
                       maintainers: list[tuple[str | None, str | None]] | None,
                       keywords: list[str] | None,
                       classifiers: list[str] | None,
                       urls: dict[str, str] | None,
                       dependencies: list[str] | None,
                       optional_dependencies: dict[str, list[str]] | None,
                       ) -> common.MetadataProps:
    """Create metadata properties

    If any of the arguments (except `project`) is ``None``, associated
    resulting property is set based on project configuration.

    """
    if name is None:
        name = project.conf.get('name') if project else None
    if name is None:
        raise Exception('name not provided')
    name = common.normalize_name(name)

    if version is None:
        version = project.conf.get('version') if project else None
    if version is None:
        raise Exception('version not provided')
    version = common.parse_version(version)

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
        license = project.conf.get('license', {}).get('text')

    if authors is None:
        authors = ([(i.get('name'), i.get('email'))
                    for i in project.conf.get('authors', [])]
                   if project else [])
    author = ', '.join(name
                       for name, _ in authors
                       if name is not None) or None
    author_email = ', '.join(f'"{name}" <{email}>'
                             for name, email in authors
                             if email is not None) or None

    if maintainers is None:
        maintainers = ([(i.get('name'), i.get('email'))
                        for i in project.conf.get('maintainers', [])]
                       if project else [])
    maintainer = ', '.join(name
                           for name, _ in maintainers
                           if name is not None) or None
    maintainer_email = ', '.join(f'"{name}" <{email}>'
                                 for name, email in maintainers
                                 if email is not None) or None

    if classifiers is None:
        classifiers = (project.conf.get('classifiers', [])
                       if project else [])

    if urls is None:
        urls = project.conf.get('urls', {}) if project else {}

    if dependencies is None:
        dependencies = project.conf.get('dependencies', []) if project else []

    if optional_dependencies is None:
        optional_dependencies = (project.conf.get('optional-dependencies', {})
                                 if project else [])

    dependencies = collections.deque(dependencies)
    provides_extras = collections.deque()
    for k, v in optional_dependencies.items():
        provides_extras.append(k)
        for i in v:
            dependencies.append(f"{i}; extra == '{k}'")

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
                                requires_externals=[],
                                project_urls=urls,
                                provides_extras=provides_extras)


def get_wheel_props(build_tag: int | None,
                    python_tag: str,
                    abi_tag: str,
                    platform_tag: str,
                    is_purelib: bool
                    ) -> common.WheelProps:
    """Create wheel properties"""
    tags = list(common.parse_tags(python_tag=python_tag,
                                  abi_tag=abi_tag,
                                  platform_tag=platform_tag))

    return common.WheelProps(is_purelib=is_purelib,
                             tags=tags,
                             build=build_tag)
