from pathlib import Path
import collections
import getopt
import sys
import typing


class Args(typing.NamedTuple):
    src_paths: dict[Path, collections.deque[str]] = {}
    build_dir: Path = Path('build')
    conf: Path = Path('pyproject.toml')
    skip_conf: bool = False


usage = r"""Usage:
  mkwhl [<option>|<path>]...

Create Python wheel

Paths specify files which should be included into wheel. If provided path
is a directory, all of it's content is recursively included in wheel.

Options:
  --help             show usage
  --src-dir PATH     change src root dir for following paths - can
                     be provided multiple times (default '.')
  --build-dir PATH   output directory (default 'build')
  --conf PATH        path to pyproject.toml (default 'pyproject.toml')
  --skip-conf        skip parsing pyproject.toml
"""


def fatal(msg: str | None):
    if msg:
        print(msg, file=sys.stderr)

    print(usage, file=sys.stderr)
    sys.exit(1)


def parse_args(argv: typing.List[str]
               ) -> Args:
    src_dir = Path('.')
    args = Args(src_paths={src_dir: collections.deque()})

    names = ['help', 'src-dir=', 'build-dir=', 'conf=', 'skip-conf']

    rest = argv[1:]
    while rest:
        try:
            result, rest = getopt.getopt(rest, '', names)

        except getopt.GetoptError as e:
            fatal(str(e))

        if not result:
            args.src_paths[src_dir].append(rest[0])
            rest = rest[1:]
            continue

        for name, value in result:
            if name == '--help':
                fatal(None)

            elif name == '--src-dir':
                src_dir = Path(value)
                if src_dir not in args.src_paths:
                    args.src_paths[src_dir] = collections.deque()

            elif name == '--build-dir':
                args = args._replace(build_dir=Path(value))

            elif name == '--conf':
                args = args._replace(conf=Path(value))

            elif name == '--skip-conf':
                args = args._replace(skip_conf=True)

            else:
                raise ValueError('unsupported name')

    return args
