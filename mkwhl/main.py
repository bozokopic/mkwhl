"""Command line interface"""

from pathlib import Path
import argparse
import sys

from mkwhl.wheel import create_wheel


def create_argument_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="Create Python wheel")
    parser.add_argument(
        '--src-dir', metavar='PATH', type=Path, default=Path('.'),
        help="source root directory (default '.')")
    parser.add_argument(
        '--build-dir', metavar='PATH', type=Path, default=Path('build'),
        help="output directory (default 'build')")
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

    # TODO authors
    # TODO maintainers

    parser.add_argument(
        '--keyword', metavar='KEYWORD', action='append',
        help="override keywords from pyproject.toml - "
             "can be provided multiple times")
    parser.add_argument(
        '--classifier', metavar='CLASSIFIER', action='append',
        help="override classifiers from pyproject.toml - "
             "can be provided multiple times")

    # TODO urls
    # TODO scripts
    # TODO gui_scripts

    parser.add_argument(
        '--dependency', metavar='NAME', action='append',
        help="override dependencies from pyproject.toml - "
             "can be provided multiple times")

    # TODO optional_dependencies

    parser.add_argument(
        '--conf', metavar='PATH', type=Path, default=Path('pyproject.toml'),
        help="path to pyproject.toml (default 'pyproject.toml')")
    parser.add_argument(
        '--skip-conf', action='store_true',
        help="skip parsing pyproject.toml")
    parser.add_argument(
        '--src-include', metavar='PATTERN', action='append', default=['**/*'],
        help="source include pattern - can be provided multiple times "
             "(default '**/*')")
    parser.add_argument(
        '--src-exclude', metavar='PATTERN', action='append',
        default=['**/__pycache__/**/*'],
        help="source exclude pattern - can be provided multiple times "
             "(default '**/__pycache__/**/*')")
    parser.add_argument(
        '--python-tag', metavar='TAG', default='py3',
        help="python tag (default 'py3')")
    parser.add_argument(
        '--abi-tag', metavar='TAG', default='none',
        help="abi tag (default 'none')")
    parser.add_argument(
        '--platform-tag', metavar='TAG', default='any',
        help="platform tag (default 'any')")
    parser.add_argument(
        '--not-purelib', action='store_true',
        help="is not purelib")
    parser.add_argument(
        '--build', metavar='N', type=int, default=None,
        help="optional build number")
    parser.add_argument(
        '--quiet', action='store_true',
        help="skip outputing wheel name to stdout")
    return parser


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()

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
        authors=None,
        maintainers=None,
        keywords=args.keyword or None,
        classifiers=args.classifier or None,
        urls=None,
        scripts=None,
        gui_scripts=None,
        dependencies=args.dependency or None,
        optional_dependencies=None,
        conf_path=args.conf if not args.skip_conf else None,
        editable=False,
        src_include_patterns=(args.src_include[1:] if len(args.src_include) > 1
                              else args.src_include),
        src_exclude_patterns=(args.src_exclude[1:] if len(args.src_exclude) > 1
                              else args.src_exclude),
        python_tag=args.python_tag,
        abi_tag=args.abi_tag,
        platform_tag=args.platform_tag,
        is_purelib=not args.not_purelib,
        build=args.build)

    if not args.quiet:
        print(wheel_name)


if __name__ == '__main__':
    sys.argv[0] = 'mkwhl'
    main()
