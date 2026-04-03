r"""Link-related CLI commands."""

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
from .base import format_page_dict


def get_page_links(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0
) -> wikipediaapi.PagesDict:
    r"""Get pages linked from a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Dictionary of linked pages

    Raises:
        PageNotFoundError: If the page does not exist
    """
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.links


def get_page_backlinks(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0
) -> wikipediaapi.PagesDict:
    r"""Get pages that link to a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Dictionary of backlinked pages

    Raises:
        PageNotFoundError: If the page does not exist
    """
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.backlinks


def get_langlinks(wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0) -> Any:
    r"""Get language links for a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Dictionary of language-linked pages

    Raises:
        PageNotFoundError: If the page does not exist
    """
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.langlinks


def format_langlinks(langlinks, output_format: str) -> str:
    r"""Format language links in the requested format."""
    if output_format == "json":
        result = {}
        for lang in sorted(langlinks.keys()):
            p = langlinks[lang]
            result[lang] = {
                "title": p.title,
                "language": p.language,
                "url": p._attributes.get("fullurl", ""),
            }
        return json.dumps(result, ensure_ascii=False, indent=2)
    else:
        lines = []
        for lang in sorted(langlinks.keys()):
            p = langlinks[lang]
            url = p._attributes.get("fullurl", "")
            lines.append(f"{lang}: {p.title} ({url})")
        return "\n".join(lines)


def register_commands(cli_group):
    """Register all link commands with the CLI group."""

    @cli_group.command()
    @click.argument("title")
    @add_options(_common_options)
    @_json_option
    def links(
        title,
        language,
        user_agent,
        variant,
        extract_format,
        namespace,
        output_format,
        max_retries,
        retry_wait,
    ):
        r"""List pages linked from a Wikipedia page.

        TITLE is the Wikipedia page title.

        \b
        Examples:
            wikipedia-api links "Python (programming language)"
            wikipedia-api links "Python (programming language)" --json
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            links_data = get_page_links(wiki, title, namespace=namespace)
            result = format_page_dict(links_data, output_format)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)

    @cli_group.command()
    @click.argument("title")
    @add_options(_common_options)
    @_json_option
    def backlinks(
        title,
        language,
        user_agent,
        variant,
        extract_format,
        namespace,
        output_format,
        max_retries,
        retry_wait,
    ):
        r"""List pages that link to a Wikipedia page.

        TITLE is the Wikipedia page title.

        \b
        Examples:
            wikipedia-api backlinks "Python (programming language)"
            wikipedia-api backlinks "Python (programming language)" --json
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            backlinks_data = get_page_backlinks(wiki, title, namespace=namespace)
            result = format_page_dict(backlinks_data, output_format)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)

    @cli_group.command()
    @click.argument("title")
    @add_options(_common_options)
    @_json_option
    def langlinks(
        title,
        language,
        user_agent,
        variant,
        extract_format,
        namespace,
        output_format,
        max_retries,
        retry_wait,
    ):
        r"""List language links for a Wikipedia page.

        Shows the page title in other language editions of Wikipedia.

        TITLE is the Wikipedia page title.

        \b
        Examples:
            wikipedia-api langlinks "Python (programming language)"
            wikipedia-api langlinks "Python (programming language)" --json
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            langlinks_data = get_langlinks(wiki, title, namespace=namespace)
            result = format_langlinks(langlinks_data, output_format)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)
