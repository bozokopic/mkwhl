"""Formating of .dist-info files"""

from collections.abc import Iterable
import csv
import io

from mkwhl import common


def get_entry_points_txt(props: common.EntryPointsProps) -> str:
    """Create entry_points.txt file content"""
    stream = io.StringIO()

    if props.console_scripts:
        stream.write("[console_scripts]\n")

        for name, path in props.console_scripts.items():
            stream.write(f"{name} = {path}\n")

    if props.gui_scripts:
        stream.write("[gui_scripts]\n")

        for name, path in props.gui_scripts.items():
            stream.write(f"{name} = {path}\n")

    return stream.getvalue()


def get_METADATA(props: common.MetadataProps) -> str:
    """Create METADATA file content"""
    stream = io.StringIO()

    stream.write("Metadata-Version: 2.5\n")
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

    if props.keywords:
        stream.write(f"Keywords: {','.join(props.keywords)}\n")

    if props.author is not None:
        stream.write(f"Author: {props.author}\n")

    if props.author_email is not None:
        stream.write(f"Author-email: {props.author_email}\n")

    if props.maintainer is not None:
        stream.write(f"Maintainer: {props.maintainer}\n")

    if props.maintainer_email is not None:
        stream.write(f"Maintainer-email: {props.maintainer_email}\n")

    if props.license_expression is not None:
        stream.write(f"License-Expression: {props.license_expression}\n")

    for license_file in props.license_file_paths.keys():
        stream.write(f"License-File: {license_file}\n")

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

    for import_name in props.import_names:
        stream.write(f"Import-Name: {import_name}\n")

    for import_namespace in props.import_namespaces:
        stream.write(f"Import-Namespace: {import_namespace}\n")

    if props.description_path:
        description = props.description_path.read_text('utf-8')
        stream.write(f"\n{description}")

    return stream.getvalue()


def get_WHEEL(props: common.WheelProps) -> str:
    """Create WHEEL file content"""
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


def get_RECORD(records: Iterable[common.WheelRecord]) -> str:
    """Create RECORD file content"""
    stream = io.StringIO()
    writer = csv.writer(stream, delimiter=',', quotechar='"')

    for record in records:
        path = record.path.as_posix()
        sha256 = (f"sha256={common.urlsafe_b64encode_nopad(record.sha256)}"
                  if record.sha256 is not None else '')
        size = str(record.size) if record.size is not None else ''

        writer.writerow([path, sha256, size])

    return stream.getvalue()
