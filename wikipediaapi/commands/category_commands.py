r"""Category-related CLI commands."""

import json
import sys

import click

import wikipediaapi

from .base import CategoryMember
from .base import PageNotFoundError
from .base import _common_options
from .base import _json_option
from .base import add_options
from .base import create_wikipedia_instance
from .base import fetch_page
from .base import format_page_dict


def get_page_categories(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int = 0
) -> wikipediaapi.PagesDict:
    r"""Get categories for a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace

    Returns:
        Dictionary of category pages

    Raises:
        PageNotFoundError: If the page does not exist
    """
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")
    return page.categories


def get_category_members(
    wiki: wikipediaapi.Wikipedia, title: str, max_level: int = 0, namespace: int = 0
) -> list[CategoryMember]:
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
    """
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
    return members


def format_category_members(members: list[CategoryMember], output_format: str) -> str:
    r"""Format category members in the requested format."""
    if output_format == "json":
        return json.dumps(members, ensure_ascii=False, indent=2)
    else:
        lines = []
        for m in members:
            prefix = "  " * m["level"]
            lines.append(f"{prefix}{m['title']} (ns: {m['ns']})")
        return "\n".join(lines)


def register_commands(cli_group):
    """Register all category commands with the CLI group."""

    @cli_group.command()
    @click.argument("title")
    @add_options(_common_options)
    @_json_option
    def categories(
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
        r"""List categories for a Wikipedia page.

        TITLE is the Wikipedia page title.

        \b
        Examples:
            wikipedia-api categories "Python (programming language)"
            wikipedia-api categories "Python (programming language)" --json
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            categories_data = get_page_categories(wiki, title, namespace=namespace)
            result = format_page_dict(categories_data, output_format)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)

    @cli_group.command()
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
        max_retries,
        retry_wait,
    ):
        r"""List pages in a Wikipedia category.

        TITLE is the category page title (e.g. "Category:Physics").

        Use --max-level to recursively list subcategory members.

        \b
        Examples:
            wikipedia-api categorymembers "Category:Physics"
            wikipedia-api categorymembers "Category:Physics" --max-level 1
            wikipedia-api categorymembers "Category:Physics" --json
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            members_data = get_category_members(
                wiki, title, max_level=max_level, namespace=namespace
            )
            result = format_category_members(members_data, output_format)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)
