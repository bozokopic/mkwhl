"""Command line interface"""

from pathlib import Path
import argparse
import collections
import email.utils
import sys

from mkwhl.wheel import create_wheel


default_src_dir = Path('.')
default_build_dir = Path('build')
default_conf = Path('pyproject.toml')
default_src_include = ['**/*.py']
default_src_exclude = ['**/__pycache__/**/*',
                       'build/**/*',
                       '**/.git/**/*']
default_python_tag = 'py3'
default_abi_tag = 'none'
default_platform_tag = 'any'


def create_argument_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="Create Python wheel")
    parser.add_argument(
        '--src-dir', metavar='PATH', type=Path, default=default_src_dir,
        help=f"source root directory (default {repr(str(default_src_dir))})")
    parser.add_argument(
        '--build-dir', metavar='PATH', type=Path, default=default_build_dir,
        help=f"output directory (default {repr(str(default_build_dir))})")
    parser.add_argument(
        '--name', metavar='NAME', default=None,
        help="override name from pyproject.toml")
    parser.add_argument(
        '--version', metavar='VERSION', default=None,
        help="override version from pyproject.toml")
    parser.add_argument(
        '--description', metavar='TEXT', default=None,
        help="override description from pyproject.toml")
    parser.add_argument(
        '--readme', metavar='PATH', type=Path, default=None,
        help="override readme path from pyproject.toml")
    parser.add_argument(
        '--requires-python', metavar='VERSION', default=None,
        help="override requires python from pyproject.toml")
    parser.add_argument(
        '--license', metavar='NAME', default=None,
        help="override license identifier from pyproject.toml")
    parser.add_argument(
        '--license-file', metavar='PATH', type=Path, default=None,
        help="override license file path from pyproject.toml")
    parser.add_argument(
        '--author', metavar='NAME', action='append',
        help="override author from pyproject.toml - "
             "can be provided multiple times")
    parser.add_argument(
        '--maintainer', metavar='NAME', action='append',
        help="override maintainer from pyproject.toml - "
             "can be provided multiple times")
    parser.add_argument(
        '--keyword', metavar='KEYWORD', action='append',
        help="override keywords from pyproject.toml - "
             "can be provided multiple times")
    parser.add_argument(
        '--classifier', metavar='CLASSIFIER', action='append',
        help="override classifiers from pyproject.toml - "
             "can be provided multiple times")
    parser.add_argument(
        '--url', metavar='NAME=URL', action='append',
        help="override url from pyproject.toml - "
             "can be provided multiple times")
    parser.add_argument(
        '--script', metavar='NAME=ENTRY', action='append',
        help="override script from pyproject.toml - "
             "can be provided multiple times")
    parser.add_argument(
        '--gui-script', metavar='NAME=ENTRY', action='append',
        help="override gui script from pyproject.toml - "
             "can be provided multiple times")
    parser.add_argument(
        '--dependency', metavar='NAME', action='append',
        help="override dependencies from pyproject.toml - "
             "can be provided multiple times")
    parser.add_argument(
        '--optional-dependency', metavar='GROUP:NAME', action='append',
        help="override optional dependencies from pyproject.toml - "
             "can be provided multiple times")
    parser.add_argument(
        '--conf', metavar='PATH', type=Path, default=default_conf,
        help=f"path to pyproject.toml (default {repr(str(default_conf))})")
    parser.add_argument(
        '--skip-conf', action='store_true',
        help="skip parsing pyproject.toml")
    parser.add_argument(
        '--src-include', metavar='PATTERN', action='append',
        default=list(default_src_include),
        help=f"source include pattern - can be provided multiple times "
             f"(default {repr(default_src_include)})")
    parser.add_argument(
        '--src-exclude', metavar='PATTERN', action='append',
        default=list(default_src_exclude),
        help=f"source exclude pattern - can be provided multiple times "
             f"(default {repr(default_src_exclude)})")
    parser.add_argument(
        '--data', metavar='SRC_PATH:DST_PATH', action='append',
        help="data source:destination path - can be provided multiple times")
    parser.add_argument(
        '--build-tag', metavar='N', type=int, default=None,
        help="optional build tag")
    parser.add_argument(
        '--python-tag', metavar='TAG', default=default_python_tag,
        help=f"python tag (default {repr(default_python_tag)})")
    parser.add_argument(
        '--abi-tag', metavar='TAG', default=default_abi_tag,
        help=f"abi tag (default {repr(default_abi_tag)})")
    parser.add_argument(
        '--platform-tag', metavar='TAG', default=default_platform_tag,
        help=f"platform tag (default {repr(default_platform_tag)})")
    parser.add_argument(
        '--not-purelib', action='store_true',
        help="is not purelib")
    parser.add_argument(
        '--quiet', action='store_true',
        help="skip outputing wheel name to stdout")
    return parser


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()

    authors = []
    for author in (args.author or []):
        if not author:
            continue
        name, mail = email.utils.parseaddr(author)
        if not name:
            authors.append((author, None))
        else:
            authors.append((name, mail or None))

    maintainers = []
    for maintainer in (args.maintainer or []):
        if not maintainer:
            continue
        name, mail = email.utils.parseaddr(maintainer)
        if not name:
            maintainers.append((maintainer, None))
        else:
            maintainers.append((name, mail or None))

    urls = {}
    for url in (args.url or []):
        name, path = url.split('=', 1)
        if not name or not path:
            continue
        urls[name] = path

    scripts = {}
    for script in (args.script or []):
        name, entry = script.split('=', 1)
        if not name or not entry:
            continue
        scripts[name] = entry

    gui_scripts = {}
    for gui_script in (args.gui_script or []):
        name, entry = gui_script.split('=', 1)
        if not name or not entry:
            continue
        gui_scripts[name] = entry

    optional_dependencies = collections.defaultdict(list)
    for optional_dependency in (args.optional_dependency or []):
        group, name = optional_dependency.split(':', 1)
        if not group or not name:
            continue
        optional_dependencies[group].append(name)

    src_include = (args.src_include[len(default_src_include):]
                   if len(args.src_include) > len(default_src_include)
                   else args.src_include)

    src_exclude = (args.src_exclude[len(default_src_exclude):]
                   if len(args.src_exclude) > len(default_src_exclude)
                   else args.src_exclude)

    data_paths = []
    for src_dst_path in (args.data or []):
        src_path, dst_path = src_dst_path.split(':', 1)
        if not src_path or not dst_path:
            continue
        data_paths.append((Path(src_path), Path(dst_path)))

    wheel_name = create_wheel(
        src_dir=args.src_dir,
        build_dir=args.build_dir,
        name=args.name,
        version=args.version,
        description=args.description,
        readme_path=args.readme,
        requires_python=args.requires_python,
        license=args.license,
        license_path=args.license_file,
        authors=authors or None,
        maintainers=maintainers or None,
        keywords=args.keyword or None,
        classifiers=args.classifier or None,
        urls=urls or None,
        scripts=scripts or None,
        gui_scripts=gui_scripts or None,
        dependencies=args.dependency or None,
        optional_dependencies=dict(optional_dependencies) or None,
        conf_path=args.conf if not args.skip_conf else None,
        editable=False,
        src_include_patterns=src_include,
        src_exclude_patterns=src_exclude,
        data_paths=data_paths,
        build_tag=args.build_tag,
        python_tag=args.python_tag,
        abi_tag=args.abi_tag,
        platform_tag=args.platform_tag,
        is_purelib=not args.not_purelib)

    if not args.quiet:
        print(wheel_name)


if __name__ == '__main__':
    sys.argv[0] = 'mkwhl'
    main()
