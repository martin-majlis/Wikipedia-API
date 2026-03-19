r"""Command line interface for Wikipedia-API.r"""

import json
import sys
from typing import Any

import click

import wikipediaapi


def create_wikipedia_instance(
    user_agent: str, language: str, variant: str | None, extract_format: str
) -> wikipediaapi.Wikipedia:
    r"""Create a Wikipedia instance from common CLI options.r"""
    fmt = wikipediaapi.ExtractFormat.WIKI
    if extract_format == "html":
        fmt = wikipediaapi.ExtractFormat.HTML

    return wikipediaapi.Wikipedia(
        user_agent=user_agent,
        language=language,
        variant=variant if variant else None,
        extract_format=fmt,
    )


def _make_wiki(user_agent, language, variant, extract_format):
    r"""Legacy wrapper for backward compatibility.r"""
    return create_wikipedia_instance(user_agent, language, variant, extract_format)


def fetch_page(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int
) -> wikipediaapi.WikipediaPage:
    r"""Get a WikipediaPage from the given Wikipedia instance.r"""
    return wiki.page(title, ns=namespace)


def _get_page(wiki, title, namespace):
    r"""Legacy wrapper for backward compatibility.r"""
    return fetch_page(wiki, title, namespace)


def format_page_dict(pages: dict[str, wikipediaapi.WikipediaPage], output_format: str) -> str:
    r"""Format a PagesDict in the requested format as a string.r"""
    if output_format == "json":
        result = {}
        for title, page in sorted(pages.items()):
            result[title] = {
                "title": page.title,
                "language": page.language,
                "ns": page.namespace,
            }
            if hasattr(page, "_attributes") and "fullurl" in page._attributes:
                result[title]["url"] = page._attributes["fullurl"]
        return json.dumps(result, ensure_ascii=False, indent=2)
    else:
        return "\n".join(sorted(pages.keys()))


def _print_page_dict(pages, output_format):
    r"""Print a PagesDict in the requested format.r"""
    formatted_output = format_page_dict(pages, output_format)
    click.echo(formatted_output)


class PageNotFoundError(Exception):
    r"""Raised when a Wikipedia page does not exist.r"""

    pass


class SectionNotFoundError(Exception):
    r"""Raised when a Wikipedia section does not exist.r"""

    pass


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
    r"""
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
    r"""
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.text


def get_page_sections(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0
) -> list[dict[str, Any]]:
    r"""Get sections of a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        List of section dictionaries with title, level, and indent

    Raises:
        PageNotFoundError: If the page does not exist
    r"""
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
    return sections  # type: ignore


def format_sections(sections: list[dict[str, Any]], output_format: str) -> str:
    r"""Format sections list in the requested format.r"""
    if output_format == "json":
        return json.dumps(sections, ensure_ascii=False, indent=2)
    else:
        lines = []
        for s in sections:
            prefix = "  " * s["indent"]
            lines.append(f"{prefix}{s['title']}")
        return "\n".join(lines)


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
    r"""
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")

    sec = page.section_by_title(section_title)
    if sec is None:
        raise SectionNotFoundError(f"Section '{section_title}' not found in '{title}'.")

    return sec.full_text()


def get_page_links(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0
) -> dict[str, wikipediaapi.WikipediaPage]:
    r"""Get pages linked from a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Dictionary of linked pages

    Raises:
        PageNotFoundError: If the page does not exist
    r"""
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.links


def get_page_backlinks(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0
) -> dict[str, wikipediaapi.WikipediaPage]:
    r"""Get pages that link to a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Dictionary of backlinked pages

    Raises:
        PageNotFoundError: If the page does not exist
    r"""
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.backlinks


def get_langlinks(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0
) -> dict[str, wikipediaapi.WikipediaPage]:
    r"""Get language links for a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Dictionary of language-linked pages

    Raises:
        PageNotFoundError: If the page does not exist
    r"""
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.langlinks


def format_langlinks(langlinks: dict[str, wikipediaapi.WikipediaPage], output_format: str) -> str:
    r"""Format language links in the requested format.r"""
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


def get_page_categories(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0
) -> dict[str, wikipediaapi.WikipediaPage]:
    r"""Get categories for a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Dictionary of category pages

    Raises:
        PageNotFoundError: If the page does not exist
    r"""
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.categories


def get_category_members(
    wiki: wikipediaapi.Wikipedia, title: str, max_level: int = 0, namespace: int = 0
) -> list[dict[str, Any]]:
    r"""Get pages in a Wikipedia category.

    Args:
        wiki: Wikipedia instance
        title: Category page title
        max_level: Maximum depth for recursive category member listing
        namespace: Wikipedia namespace

    Returns:
        List of member dictionaries with title, ns, and level

    Raises:
        PageNotFoundError: If the page does not exist
    r"""
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")

    def _collect_members(members, level=0):
        result = []
        for p in sorted(members.values(), key=lambda x: x.title):
            entry = {"title": p.title, "ns": p.namespace, "level": level}
            result.append(entry)
            if p.namespace == wikipediaapi.Namespace.CATEGORY and level < max_level:
                result.extend(_collect_members(p.categorymembers, level + 1))
        return result

    members = _collect_members(page.categorymembers)
    return members  # type: ignore


def format_category_members(members: list[dict[str, Any]], output_format: str) -> str:
    r"""Format category members in the requested format.r"""
    if output_format == "json":
        return json.dumps(members, ensure_ascii=False, indent=2)
    else:
        lines = []
        for m in members:
            prefix = "  " * m["level"]
            lines.append(f"{prefix}{m['title']} (ns: {m['ns']})")
        return "\n".join(lines)


def get_page_info(wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0) -> dict[str, Any]:
    r"""Get metadata and existence info for a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Dictionary with page information
    r"""
    p = fetch_page(wiki, title, namespace)

    info = {
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


def format_page_info(info: dict[str, Any], output_format: str) -> str:
    r"""Format page info in the requested format.r"""
    if output_format == "json":
        return json.dumps(info, ensure_ascii=False, indent=2)
    else:
        lines = []
        for k, v in info.items():
            lines.append(f"{k}: {v}")
        return "\n".join(lines)


# Legacy function for backward compatibility - keep the original version
def _print_page_dict_legacy(pages, output_format):
    r"""Print a PagesDict in the requested format (legacy version).r"""
    formatted_output = format_page_dict(pages, output_format)
    click.echo(formatted_output)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    version=".".join(str(s) for s in wikipediaapi.__version__),
    prog_name="wikipedia-api",
)
def cli():
    r"""Command line tool for querying Wikipedia using Wikipedia-API.

    Supports fetching page summaries, full text, sections, links,
    backlinks, language links, categories, and category members.

    Every command requires a TITLE argument — the Wikipedia page title.

    Examples:
    \b
        wikipedia-api summary "Python (programming language)"
        wikipedia-api links "Python (programming language)" --language cs
        wikipedia-api categories "Python (programming language)" --json
    r"""


# ── Common options ──────────────────────────────────────────────────────────

_common_options = [
    click.option(
        "--language",
        "-l",
        default="en",
        show_default=True,
        help="Language edition of Wikipedia (e.g. en, cs, de, zh).",
    ),
    click.option(
        "--user-agent",
        "-u",
        default="wikipedia-api-cli (https://github.com/martin-majlis/Wikipedia-API)",
        show_default=True,
        help="HTTP User-Agent string sent with requests.",
    ),
    click.option(
        "--variant",
        "-v",
        default=None,
        help="Language variant (e.g. zh-cn, zh-tw). Only for languages that support variants.",
    ),
    click.option(
        "--extract-format",
        "-f",
        type=click.Choice(["wiki", "html"], case_sensitive=False),
        default="wiki",
        show_default=True,
        help="Extraction format for page text.",
    ),
    click.option(
        "--namespace",
        "-n",
        type=int,
        default=0,
        show_default=True,
        help="Wikipedia namespace (0=Main, 14=Category, etc.).",
    ),
]

_json_option = click.option(
    "--json",
    "output_format",
    flag_value="json",
    default=False,
    help="Output results as JSON.",
)


def add_options(options):
    r"""Add a list of a list of click options to a command.r"""

    def wrapper(func):
        for option in reversed(options):
            func = option(func)
        return func

    return wrapper


# ── Commands ────────────────────────────────────────────────────────────────


@cli.command()
@click.argument("title")
@add_options(_common_options)
def summary(title, language, user_agent, variant, extract_format, namespace):
    r"""Print the summary of a Wikipedia page.

    TITLE is the Wikipedia page title (e.g. "Python_(programming_language)").

    \b
    Examples:
        wikipedia-api summary "Python (programming language)"
        wikipedia-api summary "Ostrava" -l cs
        wikipedia-api summary "Python" -l zh -v zh-cn
    r"""
    try:
        wiki = create_wikipedia_instance(user_agent, language, variant, extract_format)
        result = get_page_summary(wiki, title, namespace)
        click.echo(result)
    except PageNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


@cli.command()
@click.argument("title")
@add_options(_common_options)
def text(title, language, user_agent, variant, extract_format, namespace):
    r"""Print the full text of a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api text "Python (programming language)"
        wikipedia-api text "Ostrava" -l cs -f html
    r"""
    try:
        wiki = create_wikipedia_instance(user_agent, language, variant, extract_format)
        result = get_page_text(wiki, title, namespace)
        click.echo(result)
    except PageNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def sections(title, language, user_agent, variant, extract_format, namespace, output_format):
    r"""List sections of a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api sections "Python (programming language)"
        wikipedia-api sections "Python (programming language)" --json
    r"""
    try:
        wiki = create_wikipedia_instance(user_agent, language, variant, extract_format)
        sections_data = get_page_sections(wiki, title, namespace)
        result = format_sections(sections_data, output_format)
        click.echo(result)
    except PageNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


@cli.command()
@click.argument("title")
@click.argument("section_title")
@add_options(_common_options)
def section(title, section_title, language, user_agent, variant, extract_format, namespace):
    r"""Print the text of a specific section.

    TITLE is the Wikipedia page title.
    SECTION_TITLE is the name of the section to retrieve.

    \b
    Examples:
        wikipedia-api section "Python (programming language)" "Features and philosophy"
    r"""
    try:
        wiki = create_wikipedia_instance(user_agent, language, variant, extract_format)
        result = get_section_text(wiki, title, section_title, namespace)
        click.echo(result)
    except PageNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except SectionNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def links(title, language, user_agent, variant, extract_format, namespace, output_format):
    r"""List pages linked from a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api links "Python (programming language)"
        wikipedia-api links "Python (programming language)" --json
    r"""
    try:
        wiki = create_wikipedia_instance(user_agent, language, variant, extract_format)
        links_data = get_page_links(wiki, title, namespace)
        result = format_page_dict(links_data, output_format)
        click.echo(result)
    except PageNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def backlinks(title, language, user_agent, variant, extract_format, namespace, output_format):
    r"""List pages that link to a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api backlinks "Python (programming language)"
        wikipedia-api backlinks "Python (programming language)" --json
    r"""
    try:
        wiki = create_wikipedia_instance(user_agent, language, variant, extract_format)
        backlinks_data = get_page_backlinks(wiki, title, namespace)
        result = format_page_dict(backlinks_data, output_format)
        click.echo(result)
    except PageNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def langlinks(title, language, user_agent, variant, extract_format, namespace, output_format):
    r"""List language links for a Wikipedia page.

    Shows the page title in other language editions of Wikipedia.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api langlinks "Python (programming language)"
        wikipedia-api langlinks "Python (programming language)" --json
    r"""
    try:
        wiki = create_wikipedia_instance(user_agent, language, variant, extract_format)
        langlinks_data = get_langlinks(wiki, title, namespace)
        result = format_langlinks(langlinks_data, output_format)
        click.echo(result)
    except PageNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def categories(title, language, user_agent, variant, extract_format, namespace, output_format):
    r"""List categories for a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api categories "Python (programming language)"
        wikipedia-api categories "Python (programming language)" --json
    r"""
    try:
        wiki = create_wikipedia_instance(user_agent, language, variant, extract_format)
        categories_data = get_page_categories(wiki, title, namespace)
        result = format_page_dict(categories_data, output_format)
        click.echo(result)
    except PageNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


@cli.command()
@click.argument("title")
@click.option(
    "--max-level",
    type=int,
    default=0,
    show_default=True,
    help="Maximum depth for recursive category member listing.",
)
@add_options(_common_options)
@_json_option
def categorymembers(
    title,
    max_level,
    language,
    user_agent,
    variant,
    extract_format,
    namespace,
    output_format,
):
    r"""List pages in a Wikipedia category.

    TITLE is the category page title (e.g. "Category:Physics").

    Use --max-level to recursively list subcategory members.

    \b
    Examples:
        wikipedia-api categorymembers "Category:Physics"
        wikipedia-api categorymembers "Category:Physics" --max-level 1
        wikipedia-api categorymembers "Category:Physics" --json
    r"""
    try:
        wiki = create_wikipedia_instance(user_agent, language, variant, extract_format)
        members_data = get_category_members(wiki, title, max_level, namespace)
        result = format_category_members(members_data, output_format)
        click.echo(result)
    except PageNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def page(title, language, user_agent, variant, extract_format, namespace, output_format):
    r"""Show metadata and existence info for a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api page "Python (programming language)"
        wikipedia-api page "Python (programming language)" --json
    r"""
    wiki = create_wikipedia_instance(user_agent, language, variant, extract_format)
    info = get_page_info(wiki, title, namespace)
    result = format_page_info(info, output_format)
    click.echo(result)


def main():
    r"""Entry point for the CLI.r"""
    cli()


if __name__ == "__main__":
    main()
