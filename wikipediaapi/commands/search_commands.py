r"""Search-related CLI commands."""

import json

import click

import wikipediaapi

from .base import RandomKwargs
from .base import RandomPageResult
from .base import RedirectFilter
from .base import SearchKwargs
from .base import SearchResult
from .base import SearchResults
from .base import SearchSort
from .base import _common_options
from .base import _json_option
from .base import add_options
from .base import create_wikipedia_instance
from .base import redirect_filter2str
from .base import search_sort2str
from .base import validate_enum_value


def get_random_pages(
    wiki: wikipediaapi.Wikipedia,
    limit: int = 1,
    ns: int = 0,
    filter_redirect: str = "nonredirects",
    min_size: int | None = None,
    max_size: int | None = None,
) -> list[RandomPageResult]:
    r"""Get random Wikipedia pages.

    Args:
        wiki: Wikipedia instance
        limit: Number of random pages
        ns: Namespace to restrict to
        filter_redirect: Filter for redirects: all, redirects, nonredirects
        min_size: Minimum page size in bytes
        max_size: Maximum page size in bytes

    Returns:
        List of page dictionaries with title and pageid
    """
    # Convert enum parameters
    filter_redirect_enum = validate_enum_value(
        filter_redirect, RedirectFilter, redirect_filter2str, "filter_redirect"
    )

    kwargs: RandomKwargs = {"limit": limit, "filter_redirect": filter_redirect_enum}
    if ns != 0:
        kwargs["ns"] = ns
    if min_size is not None:
        kwargs["min_size"] = min_size
    if max_size is not None:
        kwargs["max_size"] = max_size

    results = wiki.random(**kwargs)
    output: list[RandomPageResult] = []
    for title, p in results.items():
        entry: RandomPageResult = {"title": title}
        if "pageid" in p._attributes:
            entry["pageid"] = p._attributes["pageid"]
        output.append(entry)
    return output


def format_random(results: list[RandomPageResult], output_format: str) -> str:
    r"""Format random page results in the requested format."""
    if output_format == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    else:
        return "\n".join(r["title"] for r in results)


def get_search_results(
    wiki: wikipediaapi.Wikipedia,
    query: str,
    limit: int = 10,
    ns: int = 0,
    sort: str = "relevance",
) -> SearchResults:
    r"""Search Wikipedia for pages matching a query.

    Args:
        wiki: Wikipedia instance
        query: Search query string
        limit: Maximum results
        ns: Namespace to search
        sort: Sort results by relevance, create_timestamp, etc.

    Returns:
        Dictionary with pages list, totalhits, and suggestion
    """
    # Convert enum parameters
    sort_enum = validate_enum_value(sort, SearchSort, search_sort2str, "sort")

    kwargs: SearchKwargs = {"limit": limit, "sort": sort_enum}
    if ns != 0:
        kwargs["ns"] = ns

    sr = wiki.search(query, **kwargs)
    pages_list: list[SearchResult] = []
    for title, p in sr.pages.items():
        entry: SearchResult = {"title": title}
        if "pageid" in p._attributes:
            entry["pageid"] = p._attributes["pageid"]
        if p.search_meta is not None:
            if p.search_meta.size > 0:
                entry["size"] = p.search_meta.size
            if p.search_meta.wordcount > 0:
                entry["wordcount"] = p.search_meta.wordcount
            if p.search_meta.timestamp:
                entry["timestamp"] = p.search_meta.timestamp
            if p.search_meta.snippet:
                entry["snippet"] = p.search_meta.snippet
        pages_list.append(entry)
    result: SearchResults = {
        "totalhits": sr.totalhits,
        "pages": pages_list,
    }
    if sr.suggestion is not None:
        result["suggestion"] = sr.suggestion
    return result


def format_search(results: SearchResults, output_format: str) -> str:
    r"""Format search results in the requested format."""
    if output_format == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    else:
        lines = []
        lines.append(f"Total hits: {results['totalhits']}")
        if "suggestion" in results:
            lines.append(f"Suggestion: {results['suggestion']}")
        lines.append("")
        for p in results["pages"]:
            lines.append(p["title"])
        return "\n".join(lines)


def register_commands(cli_group):
    """Register all search commands with the CLI group."""

    @cli_group.command(name="random")
    @click.option(
        "--limit",
        type=int,
        default=1,
        show_default=True,
        help="Number of random pages to return.",
    )
    @click.option(
        "--filter-redirect",
        type=click.Choice(["all", "redirects", "nonredirects"], case_sensitive=False),
        default="nonredirects",
        show_default=True,
        help="Filter for redirects: all, redirects, nonredirects.",
    )
    @click.option(
        "--min-size",
        type=int,
        default=None,
        help="Minimum page size in bytes.",
    )
    @click.option(
        "--max-size",
        type=int,
        default=None,
        help="Maximum page size in bytes.",
    )
    @add_options(_common_options)
    @_json_option
    def random_cmd(
        limit,
        filter_redirect,
        min_size,
        max_size,
        language,
        user_agent,
        variant,
        extract_format,
        namespace,
        output_format,
        max_retries,
        retry_wait,
    ):
        r"""Get random Wikipedia pages.

        \b
        Examples:
            wikipedia-api random
            wikipedia-api random --limit 5
            wikipedia-api random --filter-redirect all --json
            wikipedia-api random --min-size 1000 --max-size 10000
            wikipedia-api random --language de
        """
        wiki = create_wikipedia_instance(
            user_agent, language, variant, extract_format, max_retries, retry_wait
        )
        results_data = get_random_pages(
            wiki,
            limit=limit,
            ns=namespace,
            filter_redirect=filter_redirect,
            min_size=min_size,
            max_size=max_size,
        )
        result = format_random(results_data, output_format)
        click.echo(result)

    @cli_group.command()
    @click.argument("query")
    @click.option(
        "--limit",
        type=int,
        default=10,
        show_default=True,
        help="Maximum number of search results.",
    )
    @click.option(
        "--search-sort",
        "sort",
        type=click.Choice(
            [
                "relevance",
                "none",
                "random",
                "create_timestamp_asc",
                "create_timestamp_desc",
                "incoming_links_asc",
                "incoming_links_desc",
                "just_match",
                "last_edit_asc",
                "last_edit_desc",
                "title_natural_asc",
                "title_natural_desc",
                "user_random",
            ],
            case_sensitive=False,
        ),
        default="relevance",
        show_default=True,
        help="Sort search results by relevance, timestamp, etc.",
    )
    @add_options(_common_options)
    @_json_option
    def search(
        query,
        limit,
        sort,
        language,
        user_agent,
        variant,
        extract_format,
        namespace,
        output_format,
        max_retries,
        retry_wait,
    ):
        r"""Search Wikipedia for pages matching a query.

        QUERY is the search string.

        \b
        Examples:
            wikipedia-api search "Python programming"
            wikipedia-api search "Python programming" --search-sort create_timestamp_desc
            wikipedia-api search "машинное обучение" --language ru --json
        """
        wiki = create_wikipedia_instance(
            user_agent, language, variant, extract_format, max_retries, retry_wait
        )
        results_data = get_search_results(wiki, query, limit=limit, ns=namespace, sort=sort)
        result = format_search(results_data, output_format)
        click.echo(result)
