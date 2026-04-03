r"""Shared utilities and common options for CLI commands."""

import json
from typing import TypedDict

import click

import wikipediaapi
from wikipediaapi._enums import CoordinateType  # noqa: F401
from wikipediaapi._enums import GeoSearchSort  # noqa: F401
from wikipediaapi._enums import Globe  # noqa: F401
from wikipediaapi._enums import RedirectFilter  # noqa: F401
from wikipediaapi._enums import SearchSort  # noqa: F401
from wikipediaapi._enums import WikiCoordinateType
from wikipediaapi._enums import WikiGeoSearchSort
from wikipediaapi._enums import WikiGlobe
from wikipediaapi._enums import WikiRedirectFilter
from wikipediaapi._enums import WikiSearchSort
from wikipediaapi._enums import coordinate_type2str  # noqa: F401
from wikipediaapi._enums import geosearch_sort2str  # noqa: F401
from wikipediaapi._enums import globe2str  # noqa: F401
from wikipediaapi._enums import redirect_filter2str  # noqa: F401
from wikipediaapi._enums import search_sort2str  # noqa: F401


# TypedDict classes for type-safe kwargs
class GeoSearchKwargs(TypedDict, total=False):
    """TypedDict for geosearch method keyword arguments."""

    coord: wikipediaapi.GeoPoint
    page: wikipediaapi.WikipediaPage
    bbox: wikipediaapi.GeoBox
    radius: int
    max_dim: int | None
    sort: WikiGeoSearchSort
    limit: int
    globe: WikiGlobe
    ns: int
    primary: WikiCoordinateType | None


class RandomKwargs(TypedDict, total=False):
    """TypedDict for random method keyword arguments."""

    ns: int
    filter_redirect: WikiRedirectFilter
    min_size: int | None
    max_size: int | None
    limit: int


class SearchKwargs(TypedDict, total=False):
    """TypedDict for search method keyword arguments."""

    ns: int
    limit: int
    sort: WikiSearchSort


# TypedDict classes for structured data
class SectionInfo(TypedDict):
    """TypedDict for section information."""

    title: str
    level: int
    indent: int


class PageInfo(TypedDict, total=False):
    """TypedDict for page information."""

    title: str
    pageid: int | None
    namespace: int
    exists: bool
    language: str
    fullurl: str | None
    canonicalurl: str | None
    displaytitle: str | None


class CoordinateInfo(TypedDict, total=False):
    """TypedDict for coordinate information."""

    lat: float
    lon: float
    primary: bool
    globe: str
    type: str | None
    name: str | None
    dim: int | None
    country: str | None
    region: str | None
    dist: float | None


class GeoSearchResult(TypedDict, total=False):
    """TypedDict for geosearch result information."""

    title: str
    dist: float | None
    lat: float | None
    lon: float | None
    primary: bool | None


class CategoryMember(TypedDict):
    """TypedDict for category member information."""

    title: str
    ns: int
    level: int


class RandomPageResult(TypedDict, total=False):
    """TypedDict for random page result information."""

    title: str
    pageid: int | None


class SearchResult(TypedDict, total=False):
    """TypedDict for search result information."""

    title: str
    pageid: int | None
    size: int | None
    wordcount: int | None
    timestamp: str | None
    snippet: str | None


class SearchResults(TypedDict, total=False):
    """TypedDict for search results container."""

    totalhits: int
    pages: list[SearchResult]
    suggestion: str | None


def create_wikipedia_instance(
    user_agent: str,
    language: str,
    variant: str | None,
    extract_format: str,
    max_retries: int = 3,
    retry_wait: float = 1.0,
) -> wikipediaapi.Wikipedia:
    r"""Create a Wikipedia instance from common CLI options."""
    fmt = wikipediaapi.ExtractFormat.WIKI
    if extract_format == "html":
        fmt = wikipediaapi.ExtractFormat.HTML

    return wikipediaapi.Wikipedia(
        user_agent=user_agent,
        language=language,
        variant=variant if variant else None,
        extract_format=fmt,
        max_retries=max_retries,
        retry_wait=retry_wait,
    )


def _make_wiki(user_agent, language, variant, extract_format):
    r"""Legacy wrapper for backward compatibility."""
    return create_wikipedia_instance(user_agent, language, variant, extract_format)


def fetch_page(
    wiki: wikipediaapi.Wikipedia, title: str, namespace: int
) -> wikipediaapi.WikipediaPage:
    r"""Get a WikipediaPage from the given Wikipedia instance."""
    return wiki.page(title, ns=namespace)


def _get_page(wiki, title, namespace):
    r"""Legacy wrapper for backward compatibility."""
    return fetch_page(wiki, title, namespace)


def format_page_dict(pages: wikipediaapi.PagesDict, output_format: str) -> str:
    r"""Format a PagesDict in the requested format as a string."""
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
    r"""Print a PagesDict in the requested format."""
    formatted_output = format_page_dict(pages, output_format)
    click.echo(formatted_output)


class PageNotFoundError(Exception):
    r"""Raised when a Wikipedia page does not exist."""

    pass


class SectionNotFoundError(Exception):
    r"""Raised when a Wikipedia section does not exist."""

    pass


def validate_enum_value(value: str, enum_class, converter_func, param_name: str):
    """Validate and convert enum value with helpful error message.

    Args:
        value: String value from CLI
        enum_class: Enum class to validate against
        converter_func: Converter function for the enum
        param_name: Parameter name for error messages

    Returns:
        Converted enum value or original string for backward compatibility

    Raises:
        click.BadParameter: If value is invalid
    """
    try:
        # Try to find matching enum member (case-insensitive)
        for member in enum_class:
            if member.value.lower() == value.lower():
                return member
        # If no enum match, return string (for backward compatibility)
        return value
    except Exception as exc:
        valid_values = ", ".join(m.value for m in enum_class)
        raise click.BadParameter(
            f"Invalid {param_name}: {value}. Valid values are: {valid_values}"
        ) from exc


def parse_bbox_string(bbox_str: str) -> wikipediaapi.GeoBox:
    """Parse bounding box string in format 'lat1|lon1|lat2|lon2'.

    Args:
        bbox_str: Bounding box string

    Returns:
        GeoBox object

    Raises:
        click.BadParameter: If format is invalid
    """
    parts = bbox_str.split("|")
    if len(parts) != 4:
        raise click.BadParameter(f"Invalid bbox format: {bbox_str}. Expected 'lat1|lon1|lat2|lon2'")
    try:
        lat1, lon1, lat2, lon2 = map(float, parts)
        top_left = wikipediaapi.GeoPoint(lat=lat1, lon=lon1)
        bottom_right = wikipediaapi.GeoPoint(lat=lat2, lon=lon2)
        return wikipediaapi.GeoBox(top_left=top_left, bottom_right=bottom_right)
    except ValueError as exc:
        raise click.BadParameter(
            f"Invalid bbox coordinates: {bbox_str}. All values must be numeric"
        ) from exc


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
    click.option(
        "--max-retries",
        type=int,
        default=3,
        show_default=True,
        help="Maximum number of retry attempts for transient errors "
        "(HTTP 429, 5xx, timeouts, connection errors). Set to 0 to disable retries entirely.",
    ),
    click.option(
        "--retry-wait",
        type=float,
        default=1.0,
        show_default=True,
        help="Base wait time in seconds between retries; actual wait uses exponential backoff "
        "(retry_wait * 2^attempt). For HTTP 429 the Retry-After header value is used instead.",
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
    r"""Add a list of a list of click options to a command."""

    def wrapper(func):
        for option in reversed(options):
            func = option(func)
        return func

    return wrapper


def format_sections(sections: list[SectionInfo], output_format: str) -> str:
    r"""Format sections list in the requested format."""
    if output_format == "json":
        return json.dumps(sections, ensure_ascii=False, indent=2)
    else:
        lines = []
        for s in sections:
            prefix = "  " * s["indent"]
            lines.append(f"{prefix}{s['title']}")
        return "\n".join(lines)


def format_page_info(info: PageInfo, output_format: str) -> str:
    r"""Format page info in the requested format."""
    if output_format == "json":
        return json.dumps(info, ensure_ascii=False, indent=2)
    else:
        lines = []
        for k, v in info.items():
            lines.append(f"{k}: {v}")
        return "\n".join(lines)
