r"""Page-related CLI commands."""

import sys

import click

import wikipediaapi

from .base import PageInfo
from .base import PageNotFoundError
from .base import SectionInfo
from .base import SectionNotFoundError
from .base import _common_options
from .base import _json_option
from .base import add_options
from .base import create_wikipedia_instance
from .base import fetch_page
from .base import format_page_info
from .base import format_sections


def get_page_summary(wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0) -> str:
    r"""Get the summary of a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Page summary text

    Raises:
        PageNotFoundError: If the page does not exist
    """
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.summary


def get_page_text(wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0) -> str:
    r"""Get the full text of a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Full page text

    Raises:
        PageNotFoundError: If the page does not exist
    """
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.text


def get_page_sections(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0
) -> list[SectionInfo]:
    r"""Get sections of a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        List of section dictionaries with title, level, and indent

    Raises:
        PageNotFoundError: If the page does not exist
    """
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")

    def _collect_sections(section_list, level=0):
        result = []
        for s in section_list:
            result.append({"title": s.title, "level": s.level, "indent": level})
            result.extend(_collect_sections(s.sections, level + 1))
        return result

    sections = _collect_sections(page.sections)
    return sections


def get_section_text(
    wiki: wikipediaapi.Wikipedia, title: str, section_title: str, namespace: int = 0
) -> str:
    r"""Get the text of a specific section.

    Args:
        wiki: Wikipedia instance
        title: Page title
        section_title: Section title
        namespace: Wikipedia namespace

    Returns:
        Section text

    Raises:
        PageNotFoundError: If the page does not exist
        SectionNotFoundError: If the section does not exist
    """
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")

    sec = page.section_by_title(section_title)
    if sec is None:
        raise SectionNotFoundError(f"Section '{section_title}' not found in '{title}'.")

    return sec.full_text() if sec else ""


def get_page_info(wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0) -> PageInfo:
    r"""Get metadata and existence info for a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Dictionary with page information
    """
    p = fetch_page(wiki, title, namespace)

    info: PageInfo = {
        "title": p.title,
        "exists": p.exists(),
        "language": p.language,
        "namespace": p.namespace,
    }
    if p.exists():
        info["pageid"] = p.pageid
        info["fullurl"] = p.fullurl
        info["canonicalurl"] = p.canonicalurl
        info["displaytitle"] = p.displaytitle

    return info


def register_commands(cli_group):
    """Register all page commands with the CLI group."""

    @cli_group.command()
    @click.argument("title")
    @add_options(_common_options)
    def summary(
        title, language, user_agent, variant, extract_format, namespace, max_retries, retry_wait
    ):
        r"""Print the summary of a Wikipedia page.

        TITLE is the Wikipedia page title (e.g. "Python_(programming_language)").

        \b
        Examples:
            wikipedia-api summary "Python (programming language)"
            wikipedia-api summary "Ostrava" -l cs
            wikipedia-api summary "Python" -l zh -v zh-cn
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            result = get_page_summary(wiki, title, namespace=namespace)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)

    @cli_group.command()
    @click.argument("title")
    @add_options(_common_options)
    def text(
        title, language, user_agent, variant, extract_format, namespace, max_retries, retry_wait
    ):
        r"""Print the full text of a Wikipedia page.

        TITLE is the Wikipedia page title.

        \b
        Examples:
            wikipedia-api text "Python (programming language)"
            wikipedia-api text "Ostrava" -l cs -f html
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            result = get_page_text(wiki, title, namespace=namespace)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)

    @cli_group.command()
    @click.argument("title")
    @add_options(_common_options)
    @_json_option
    def sections(
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
        r"""List sections of a Wikipedia page.

        TITLE is the Wikipedia page title.

        \b
        Examples:
            wikipedia-api sections "Python (programming language)"
            wikipedia-api sections "Python (programming language)" --json
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            sections_data = get_page_sections(wiki, title, namespace=namespace)
            result = format_sections(sections_data, output_format)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)

    @cli_group.command()
    @click.argument("title")
    @click.argument("section_title")
    @add_options(_common_options)
    def section(
        title,
        section_title,
        language,
        user_agent,
        variant,
        extract_format,
        namespace,
        max_retries,
        retry_wait,
    ):
        r"""Print the text of a specific section.

        TITLE is the Wikipedia page title.
        SECTION_TITLE is the name of the section to retrieve.

        \b
        Examples:
            wikipedia-api section "Python (programming language)" "Features and philosophy"
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            result = get_section_text(wiki, title, section_title, namespace=namespace)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)
        except SectionNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)

    @cli_group.command()
    @click.argument("title")
    @add_options(_common_options)
    @_json_option
    def page(
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
        r"""Show metadata and existence info for a Wikipedia page.

        TITLE is the Wikipedia page title.

        \b
        Examples:
            wikipedia-api page "Python (programming language)"
            wikipedia-api page "Python (programming language)" --json
        """
        wiki = create_wikipedia_instance(
            user_agent, language, variant, extract_format, max_retries, retry_wait
        )
        info = get_page_info(wiki, title, namespace=namespace)
        result = format_page_info(info, output_format)
        click.echo(result)
