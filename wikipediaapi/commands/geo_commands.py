r"""Geographic-related CLI commands."""

import json
import sys

import click

import wikipediaapi

from .base import CoordinateInfo
from .base import CoordinateType
from .base import GeoSearchKwargs
from .base import GeoSearchResult
from .base import GeoSearchSort
from .base import Globe
from .base import PageNotFoundError
from .base import _common_options
from .base import _json_option
from .base import add_options
from .base import coordinate_type2str
from .base import create_wikipedia_instance
from .base import fetch_page
from .base import geosearch_sort2str
from .base import globe2str
from .base import parse_bbox_string
from .base import validate_enum_value


def get_page_coordinates(
    wiki: wikipediaapi.Wikipedia,
    title: str,
    namespace: int = 0,
    limit: int = 10,
    primary: str = "primary",
) -> list[CoordinateInfo]:
    r"""Get geographic coordinates for a Wikipedia page.

    Args:
        wiki: Wikipedia instance
        title: Page title
        namespace: Wikipedia namespace
        limit: Maximum number of coordinates to return
        primary: Which coordinates: primary, secondary, or all

    Returns:
        List of coordinate dictionaries

    Raises:
        PageNotFoundError: If the page does not exist
    """
    page = fetch_page(wiki, title, namespace)
    if not page.exists():
        raise PageNotFoundError(f"Page '{title}' does not exist.")

    # Convert primary parameter to proper enum
    primary_enum = validate_enum_value(primary, CoordinateType, coordinate_type2str, "primary")

    coords = wiki.coordinates(page, limit=limit, primary=primary_enum)
    result: list[CoordinateInfo] = []
    for c in coords:
        entry: CoordinateInfo = {
            "lat": c.lat,
            "lon": c.lon,
            "primary": c.primary,
            "globe": c.globe,
        }
        if c.type is not None:
            entry["type"] = c.type
        if c.name is not None:
            entry["name"] = c.name
        if c.dim is not None:
            entry["dim"] = c.dim
        if c.country is not None:
            entry["country"] = c.country
        if c.region is not None:
            entry["region"] = c.region
        if c.dist is not None:
            entry["dist"] = c.dist
        result.append(entry)
    return result


def format_coordinates(coords: list[CoordinateInfo], output_format: str) -> str:
    r"""Format coordinates in the requested format."""
    if output_format == "json":
        return json.dumps(coords, ensure_ascii=False, indent=2)
    else:
        lines = []
        for c in coords:
            parts = [f"{c['lat']}, {c['lon']}"]
            if c.get("primary"):
                parts.append("(primary)")
            if c.get("globe") and c["globe"] != "earth":
                parts.append(f"globe={c['globe']}")
            if c.get("dist") is not None:
                parts.append(f"dist={c['dist']}m")
            lines.append(" ".join(parts))
        return "\n".join(lines)


def geosearch(
    wiki: wikipediaapi.Wikipedia,
    coord: str | None = None,
    page_title: str | None = None,
    bbox: str | None = None,
    radius: int = 1000,
    max_dim: int | None = None,
    sort: str = "distance",
    limit: int = 10,
    globe: str = "earth",
    ns: int = 0,
    primary: str | None = None,
) -> list[GeoSearchResult]:
    r"""Search for Wikipedia pages near a geographic location.

    Args:
        wiki: Wikipedia instance
        coord: Coordinates as "lat|lon"
        page_title: Page title to use as centre
        bbox: Bounding box as "lat1|lon1|lat2|lon2"
        radius: Search radius in meters
        max_dim: Maximum dimension in meters
        sort: Sort results by distance or relevance
        limit: Maximum results
        globe: Globe to search on
        ns: Namespace to search in
        primary: Filter by primary coordinates

    Returns:
        List of result dictionaries with title, dist, lat, lon
    """

    def _parse_coord(value: str) -> wikipediaapi.GeoPoint:
        """Parse ``lat|lon`` into a validated :class:`wikipediaapi.GeoPoint`.

        Args:
            value: Coordinate string in ``lat|lon`` format.

        Returns:
            Parsed and validated geographic point.

        Raises:
            click.UsageError: If the value format is invalid.
        """
        parts = value.split("|", 1)
        if len(parts) != 2:
            raise click.UsageError("Invalid --coord format, expected 'lat|lon'.")
        try:
            lat = float(parts[0])
            lon = float(parts[1])
            return wikipediaapi.GeoPoint(lat=lat, lon=lon)
        except ValueError as exc:
            raise click.UsageError("Invalid --coord format, expected numeric 'lat|lon'.") from exc

    # Convert enum parameters
    sort_enum = validate_enum_value(sort, GeoSearchSort, geosearch_sort2str, "sort")
    globe_enum = validate_enum_value(globe, Globe, globe2str, "globe")

    kwargs: GeoSearchKwargs = {
        "radius": radius,
        "limit": limit,
        "sort": sort_enum,
        "globe": globe_enum,
    }

    if coord:
        kwargs["coord"] = _parse_coord(coord)
    elif page_title:
        kwargs["page"] = wiki.page(page_title)
    elif bbox:
        kwargs["bbox"] = parse_bbox_string(bbox)
    else:
        raise click.UsageError("Either --coord, --page, or --bbox must be provided.")

    if max_dim is not None:
        kwargs["max_dim"] = max_dim
    if ns != 0:
        kwargs["ns"] = ns
    if primary is not None:
        kwargs["primary"] = validate_enum_value(
            primary, CoordinateType, coordinate_type2str, "primary"
        )

    results = wiki.geosearch(**kwargs)
    output: list[GeoSearchResult] = []
    for title, p in results.items():
        entry: GeoSearchResult = {"title": title}
        if p.geosearch_meta is not None:
            entry["dist"] = p.geosearch_meta.dist
            entry["lat"] = p.geosearch_meta.lat
            entry["lon"] = p.geosearch_meta.lon
            entry["primary"] = p.geosearch_meta.primary
        output.append(entry)
    return output


def format_geosearch(results: list[GeoSearchResult], output_format: str) -> str:
    r"""Format geosearch results in the requested format."""
    if output_format == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    else:
        if not results:
            return "No results found"
        lines = []
        for r in results:
            parts = [r["title"]]
            if "dist" in r:
                parts.append(f"({r['dist']}m)")
            if "lat" in r and "lon" in r:
                parts.append(f"[{r['lat']}, {r['lon']}]")
            lines.append(" ".join(parts))
        return "\n".join(lines)


def get_geosearch_results(wiki: wikipediaapi.Wikipedia, **kwargs) -> list[GeoSearchResult]:
    """Wrap geosearch function for backward compatibility with tests."""
    return geosearch(wiki, **kwargs)


def register_commands(cli_group):
    """Register all geographic commands with the CLI group."""

    @cli_group.command()
    @click.argument("title")
    @click.option(
        "--limit",
        type=int,
        default=10,
        show_default=True,
        help="Maximum number of coordinates to return.",
    )
    @click.option(
        "--primary",
        type=click.Choice(["primary", "secondary", "all"], case_sensitive=False),
        default="primary",
        show_default=True,
        help="Which coordinates to return.",
    )
    @add_options(_common_options)
    @_json_option
    def coordinates(
        title,
        limit,
        primary,
        language,
        user_agent,
        variant,
        extract_format,
        namespace,
        output_format,
        max_retries,
        retry_wait,
    ):
        r"""Show geographic coordinates for a Wikipedia page.

        TITLE is the Wikipedia page title.

        \b
        Examples:
            wikipedia-api coordinates "Mount Everest"
            wikipedia-api coordinates "Mount Everest" --primary all
            wikipedia-api coordinates "Mount Everest" --json
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            coords_data = get_page_coordinates(
                wiki, title, namespace=namespace, limit=limit, primary=primary
            )
            result = format_coordinates(coords_data, output_format)
            click.echo(result)
        except PageNotFoundError as e:
            click.echo(str(e), err=True)
            sys.exit(1)

    @cli_group.command()
    @click.option(
        "--coord",
        default=None,
        help='Coordinates as "lat|lon" (e.g. "51.5074|-0.1278").',
    )
    @click.option(
        "--page",
        "page_title",
        default=None,
        help="Page title to use as centre point.",
    )
    @click.option(
        "--bbox",
        default=None,
        help='Bounding box as "lat1|lon1|lat2|lon2".',
    )
    @click.option(
        "--radius",
        type=int,
        default=500,
        show_default=True,
        help="Search radius in meters (max 10000).",
    )
    @click.option(
        "--max-dim",
        type=int,
        default=None,
        help="Maximum dimension in meters.",
    )
    @click.option(
        "--sort",
        type=click.Choice(["distance", "relevance"], case_sensitive=False),
        default="distance",
        show_default=True,
        help="Sort results by distance or relevance.",
    )
    @click.option(
        "--limit",
        type=int,
        default=10,
        show_default=True,
        help="Maximum number of results.",
    )
    @click.option(
        "--globe",
        type=click.Choice(["earth", "mars", "moon", "venus"], case_sensitive=False),
        default="earth",
        show_default=True,
        help="Globe to search on.",
    )
    @click.option(
        "--primary",
        type=click.Choice(["primary", "secondary", "all"], case_sensitive=False),
        default=None,
        help="Filter by primary coordinates.",
    )
    @add_options(_common_options)
    @_json_option
    def geosearch(
        coord,
        page_title,
        bbox,
        radius,
        max_dim,
        sort,
        limit,
        globe,
        primary,
        language,
        user_agent,
        variant,
        extract_format,
        namespace,
        output_format,
        max_retries,
        retry_wait,
    ):
        r"""Search for Wikipedia pages near a geographic location.

        Requires either --coord, --page, or --bbox to specify the search area.

        \b
        Examples:
            wikipedia-api geosearch --coord "51.5074|-0.1278"
            wikipedia-api geosearch --page "Big Ben" --radius 1000
            wikipedia-api geosearch --bbox "51.5|-0.2|51.6|-0.1" --sort relevance
            wikipedia-api geosearch --coord "48.8566|2.3522" --globe mars --json
        """
        try:
            wiki = create_wikipedia_instance(
                user_agent, language, variant, extract_format, max_retries, retry_wait
            )
            results_data = get_geosearch_results(
                wiki,
                coord=coord,
                page_title=page_title,
                bbox=bbox,
                radius=radius,
                max_dim=max_dim,
                sort=sort,
                limit=limit,
                globe=globe,
                ns=namespace,
                primary=primary,
            )
            result = format_geosearch(results_data, output_format)
            click.echo(result)
        except click.UsageError as e:
            click.echo(str(e), err=True)
            sys.exit(1)
