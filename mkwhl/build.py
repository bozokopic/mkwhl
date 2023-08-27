from pathlib import Path

from mkwhl import common
from mkwhl.wheel import create_wheel


class UnsupportedOperation(Exception):
    pass


def build_wheel(wheel_directory,
                config_settings=None,
                metadata_directory=None):
    return _build_wheel(build_dir=Path(wheel_directory),
                        editable=False)


def build_editable(wheel_directory,
                   config_settings=None,
                   metadata_directory=None):
    return _build_wheel(build_dir=Path(wheel_directory),
                        editable=True)


def build_sdist(sdist_directory, config_settings=None):
    raise UnsupportedOperation()


def get_requires_for_build_wheel(config_settings=None):
    return _get_requires()


def get_requires_for_build_editable(config_settings=None):
    return _get_requires()


def _build_wheel(build_dir: Path,
                 editable: bool
                 ) -> str:
    conf = common.get_conf()
    tool_conf = conf.get('tool', {}).get('mkwhl', {})

    src_dir = tool_conf.get('src-dir')
    license_path = tool_conf.get('license-path')
    src_include_patterns = tool_conf.get('src-include-patterns',
                                         ['**/*'])
    src_exclude_patterns = tool_conf.get('src-exclude-patterns',
                                         ['**/__pycache__/**/*'])
    python_tag = tool_conf.get('python-tag', 'py3')
    abi_tag = tool_conf.get('abi-tag', 'none')
    platform_tag = tool_conf.get('platform-tag', 'any')
    is_purelib = tool_conf.get('is-purelib', True)
    build = tool_conf.get('build')

    if src_dir is None:
        for i in [Path('src_py'), Path('src')]:
            if i.is_dir():
                src_dir = i
                break
        else:
            raise Exception('cound not detect src dir')
    else:
        src_dir = Path(src_dir)

    if license_path is not None:
        license_path = Path(license_path)

    return create_wheel(src_dir=src_dir,
                        build_dir=build_dir,
                        license_path=license_path,
                        editable=editable,
                        src_include_patterns=src_include_patterns,
                        src_exclude_patterns=src_exclude_patterns,
                        python_tag=python_tag,
                        abi_tag=abi_tag,
                        platform_tag=platform_tag,
                        is_purelib=is_purelib,
                        build=build)


def _get_requires():
    conf = common.get_conf()
    project_conf = conf.get('project', {})

    return [*project_conf.get('dependencies', []),
            *project_conf.get('optional-dependencies', {}).get('dev', [])]
