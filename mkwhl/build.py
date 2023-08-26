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

    src_paths = tool_conf.get('src-paths')
    license_path = tool_conf.get('license-path')
    python_tag = tool_conf.get('python-tag')
    abi_tag = tool_conf.get('abi-tag')
    platform_tag = tool_conf.get('platform-tag')
    is_purelib = tool_conf.get('is-purelib')
    build = tool_conf.get('build')

    if src_paths is not None:
        src_paths = {Path(k): v for k, v in src_paths.items()}

    else:
        for src_dir in [Path('src_py'), Path('src')]:
            if src_dir.is_dir():
                src_paths = {src_dir: ['.']}
                break
        else:
            raise Exception('cound not detect src dir')

    return create_wheel(src_paths=src_paths,
                        build_dir=build_dir,
                        license_path=license_path,
                        editable=editable,
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
