r"""Image (file) related CLI commands."""

import json
import sys
from typing import Any

import click

import wikipediaapi

from .base import PageNotFoundError
from .base import _common_options
from .base import _json_option
from .base import add_options
from .base import create_wikipedia_instance
from .base import fetch_page


def get_page_images(
    wiki: wikipediaapi.Wikipedia,
    title: str,
    namespace: int = 0,
    limit: int = 10,
) -> wikipediaapi.ImagesDict:
    r"""Get images (files) used on a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace
        limit: Maximum number of images to return

    Returns:
        ImagesDict of image pages keyed by title

    Raises:
        PageNotFoundError: If the page does not exist
    """
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return wiki.images(page, limit=limit)


def format_images(
    images_dict: wikipediaapi.ImagesDict,
    output_format: str,
    with_imageinfo: bool = False,
) -> str:
    r"""Format image dictionary in the requested format.

    Args:
        images_dict: ImagesDict or dict of WikipediaImage objects
        output_format: "text" or "json"
        with_imageinfo: If True, include image metadata in output

    Returns:
        Formatted string
    """
    if output_format == "json":
        result = {}
        for title, img in sorted(images_dict.items()):
            entry: dict[str, Any] = {
                "title": img.title,
                "language": img.language,
                "namespace": img.namespace,
                "pageid": img.pageid if hasattr(img, "pageid") and img.pageid is not None else None,
                "variant": img.variant,
            }
            if hasattr(img, "_attributes") and "fullurl" in img._attributes:
                entry["fullurl"] = img._attributes["fullurl"]

            if with_imageinfo:
                # Add imageinfo metadata
                try:
                    entry["url"] = img.url
                    entry["descriptionurl"] = img.descriptionurl
                    entry["descriptionshorturl"] = img.descriptionshorturl
                    entry["width"] = img.width
                    entry["height"] = img.height
                    entry["size"] = img.size
                    entry["mime"] = img.mime
                    entry["mediatype"] = img.mediatype
                    entry["sha1"] = img.sha1
                    entry["timestamp"] = img.timestamp
                    entry["user"] = img.user
                except Exception:
                    # If imageinfo fetch fails, just skip those fields
                    pass

            result[title] = entry
        return json.dumps(result, ensure_ascii=False, indent=2)
    else:
        # Text format
        lines = []
        for title in sorted(images_dict.keys()):
            img = images_dict[title]
            if with_imageinfo:
                # Show title with URL and dimensions
                try:
                    parts = [img.title]
                    if img.url:
                        parts.append(f"({img.url})")
                    if img.width is not None and img.height is not None:
                        parts.append(f"{img.width}x{img.height}")
                    if img.mime:
                        parts.append(img.mime)
                    lines.append(" ".join(parts))
                except Exception:
                    # If imageinfo fetch fails, fall back to title only
                    lines.append(title)
            else:
                lines.append(title)
        return "\n".join(lines)


def register_commands(cli_group):
    """Register all image commands with the CLI group."""

    @cli_group.command()
    @click.argument("title")
    @click.option(
        "--limit",
        type=int,
        default=10,
        show_default=True,
        help="Maximum number of images to return.",
    )
    @click.option(
        "--imageinfo",
        is_flag=True,
        default=False,
        help="Fetch and display image metadata (url, dimensions, mime type, etc.).",
    )
    @add_options(_common_options)
    @_json_option
    def images(
        title,
        limit,
        imageinfo,
        language,
        user_agent,
        variant,
        extract_format,
        namespace,
        output_format,
        max_retries,
        retry_wait,
    ):
        r"""List images (files) used on a Wikipedia page.

        TITLE is the Wikipedia page title.

        By default, shows only image titles. Use --imageinfo to include
        metadata such as URL, dimensions, MIME type, uploader, and upload
        timestamp.

        \b
        Examples:
            wikipedia-api images "Python (programming language)"
            wikipedia-api images "Mount Everest" --imageinfo
            wikipedia-api images "Mount Everest" --imageinfo --json
            wikipedia-api images "Earth" --limit 50
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            images_data = get_page_images(wiki, title, namespace=namespace, limit=limit)
            result = format_images(images_data, output_format, imageinfo)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)
