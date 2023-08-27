import io
import typing

from mkwhl import common


def get_entry_points_txt(props: common.EntryPointsProps
                         ) -> str:
    stream = io.StringIO()

    if props.console_scripts:
        stream.write("[console_scripts]\n")

        for name, path in props.console_scripts.items():
            stream.write(f"{name} = {path}")

    if props.gui_scripts:
        stream.write("[gui_scripts]\n")

        for name, path in props.gui_scripts.items():
            stream.write(f"{name} = {path}")

    return stream.getvalue()


def get_METADATA(props: common.MetadataProps) -> str:
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


def get_WHEEL(props: common.WheelProps) -> str:
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


def get_RECORD(records: typing.Iterable[common.WheelRecord]) -> str:
    stream = io.StringIO()

    for record in records:
        stream.write(f"{record.path},")

        sha256 = (f"sha256={common.urlsafe_b64encode_nopad(record.sha256)}"
                  if record.sha256 is not None else '')
        stream.write(f"{sha256},")

        size = str(record.size) if record.size is not None else ''
        stream.write(f"{size}\n")

    return stream.getvalue()
