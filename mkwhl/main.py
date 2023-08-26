import sys

from mkwhl.args import parse_args
from mkwhl.wheel import create_wheel


def main():
    args = parse_args(sys.argv)

    create_wheel(src_paths=args.src_paths,
                 build_dir=args.build_dir,
                 conf_path=args.conf if not args.skip_conf else None)


if __name__ == '__main__':
    sys.argv[0] = 'mkwhl'
    main()
