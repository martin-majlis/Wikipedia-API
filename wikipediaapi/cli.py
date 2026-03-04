"""Command line interface for Wikipedia-API."""

import json
import sys

import click

import wikipediaapi


def _make_wiki(user_agent, language, variant, extract_format):
    """Create a Wikipedia instance from common CLI options."""
    fmt = wikipediaapi.ExtractFormat.WIKI
    if extract_format == "html":
        fmt = wikipediaapi.ExtractFormat.HTML

    return wikipediaapi.Wikipedia(
        user_agent=user_agent,
        language=language,
        variant=variant if variant else None,
        extract_format=fmt,
    )


def _get_page(wiki, title, namespace):
    """Get a WikipediaPage from the given Wikipedia instance."""
    return wiki.page(title, ns=namespace)


def _print_page_dict(pages, output_format):
    """Print a PagesDict in the requested format."""
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
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for title in sorted(pages.keys()):
            click.echo(title)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    version=".".join(str(s) for s in wikipediaapi.__version__),
    prog_name="wikipedia-api",
)
def cli():
    """Command line tool for querying Wikipedia using Wikipedia-API.

    Supports fetching page summaries, full text, sections, links,
    backlinks, language links, categories, and category members.

    Every command requires a TITLE argument — the Wikipedia page title.

    Examples:

    \b
        wikipedia-api summary "Python (programming language)"
        wikipedia-api links "Python (programming language)" --language cs
        wikipedia-api categories "Python (programming language)" --json
    """


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
    """Decorator that adds a list of click options to a command."""

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
    """Print the summary of a Wikipedia page.

    TITLE is the Wikipedia page title (e.g. "Python_(programming_language)").

    \b
    Examples:
        wikipedia-api summary "Python (programming language)"
        wikipedia-api summary "Ostrava" -l cs
        wikipedia-api summary "Python" -l zh -v zh-cn
    """
    wiki = _make_wiki(user_agent, language, variant, extract_format)
    page = _get_page(wiki, title, namespace)
    if not page.exists():
        click.echo(f"Page '{title}' does not exist.", err=True)
        sys.exit(1)
    click.echo(page.summary)


@cli.command()
@click.argument("title")
@add_options(_common_options)
def text(title, language, user_agent, variant, extract_format, namespace):
    """Print the full text of a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api text "Python (programming language)"
        wikipedia-api text "Ostrava" -l cs -f html
    """
    wiki = _make_wiki(user_agent, language, variant, extract_format)
    page = _get_page(wiki, title, namespace)
    if not page.exists():
        click.echo(f"Page '{title}' does not exist.", err=True)
        sys.exit(1)
    click.echo(page.text)


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def sections(title, language, user_agent, variant, extract_format, namespace, output_format):
    """List sections of a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api sections "Python (programming language)"
        wikipedia-api sections "Python (programming language)" --json
    """
    wiki = _make_wiki(user_agent, language, variant, extract_format)
    page = _get_page(wiki, title, namespace)
    if not page.exists():
        click.echo(f"Page '{title}' does not exist.", err=True)
        sys.exit(1)

    def _collect_sections(section_list, level=0):
        result = []
        for s in section_list:
            result.append({"title": s.title, "level": s.level, "indent": level})
            result.extend(_collect_sections(s.sections, level + 1))
        return result

    all_sections = _collect_sections(page.sections)

    if output_format == "json":
        click.echo(json.dumps(all_sections, ensure_ascii=False, indent=2))
    else:
        for s in all_sections:
            prefix = "  " * s["indent"]
            click.echo(f"{prefix}{s['title']}")


@cli.command()
@click.argument("title")
@click.argument("section_title")
@add_options(_common_options)
def section(title, section_title, language, user_agent, variant, extract_format, namespace):
    """Print the text of a specific section.

    TITLE is the Wikipedia page title.
    SECTION_TITLE is the name of the section to retrieve.

    \b
    Examples:
        wikipedia-api section "Python (programming language)" "Features and philosophy"
    """
    wiki = _make_wiki(user_agent, language, variant, extract_format)
    page = _get_page(wiki, title, namespace)
    if not page.exists():
        click.echo(f"Page '{title}' does not exist.", err=True)
        sys.exit(1)
    sec = page.section_by_title(section_title)
    if sec is None:
        click.echo(f"Section '{section_title}' not found in '{title}'.", err=True)
        sys.exit(1)
    click.echo(sec.full_text())


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def links(title, language, user_agent, variant, extract_format, namespace, output_format):
    """List pages linked from a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api links "Python (programming language)"
        wikipedia-api links "Python (programming language)" --json
    """
    wiki = _make_wiki(user_agent, language, variant, extract_format)
    page = _get_page(wiki, title, namespace)
    if not page.exists():
        click.echo(f"Page '{title}' does not exist.", err=True)
        sys.exit(1)
    _print_page_dict(page.links, output_format)


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def backlinks(title, language, user_agent, variant, extract_format, namespace, output_format):
    """List pages that link to a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api backlinks "Python (programming language)"
        wikipedia-api backlinks "Python (programming language)" --json
    """
    wiki = _make_wiki(user_agent, language, variant, extract_format)
    page = _get_page(wiki, title, namespace)
    if not page.exists():
        click.echo(f"Page '{title}' does not exist.", err=True)
        sys.exit(1)
    _print_page_dict(page.backlinks, output_format)


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def langlinks(title, language, user_agent, variant, extract_format, namespace, output_format):
    """List language links for a Wikipedia page.

    Shows the page title in other language editions of Wikipedia.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api langlinks "Python (programming language)"
        wikipedia-api langlinks "Python (programming language)" --json
    """
    wiki = _make_wiki(user_agent, language, variant, extract_format)
    page = _get_page(wiki, title, namespace)
    if not page.exists():
        click.echo(f"Page '{title}' does not exist.", err=True)
        sys.exit(1)

    ll = page.langlinks
    if output_format == "json":
        result = {}
        for lang in sorted(ll.keys()):
            p = ll[lang]
            result[lang] = {
                "title": p.title,
                "language": p.language,
                "url": p._attributes.get("fullurl", ""),
            }
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for lang in sorted(ll.keys()):
            p = ll[lang]
            url = p._attributes.get("fullurl", "")
            click.echo(f"{lang}: {p.title} ({url})")


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def categories(title, language, user_agent, variant, extract_format, namespace, output_format):
    """List categories for a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api categories "Python (programming language)"
        wikipedia-api categories "Python (programming language)" --json
    """
    wiki = _make_wiki(user_agent, language, variant, extract_format)
    page = _get_page(wiki, title, namespace)
    if not page.exists():
        click.echo(f"Page '{title}' does not exist.", err=True)
        sys.exit(1)
    _print_page_dict(page.categories, output_format)


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
    """List pages in a Wikipedia category.

    TITLE is the category page title (e.g. "Category:Physics").

    Use --max-level to recursively list subcategory members.

    \b
    Examples:
        wikipedia-api categorymembers "Category:Physics"
        wikipedia-api categorymembers "Category:Physics" --max-level 1
        wikipedia-api categorymembers "Category:Physics" --json
    """
    wiki = _make_wiki(user_agent, language, variant, extract_format)
    page = _get_page(wiki, title, namespace)
    if not page.exists():
        click.echo(f"Page '{title}' does not exist.", err=True)
        sys.exit(1)

    def _collect_members(members, level=0):
        result = []
        for p in sorted(members.values(), key=lambda x: x.title):
            entry = {"title": p.title, "ns": p.namespace, "level": level}
            result.append(entry)
            if p.namespace == wikipediaapi.Namespace.CATEGORY and level < max_level:
                result.extend(_collect_members(p.categorymembers, level + 1))
        return result

    all_members = _collect_members(page.categorymembers)

    if output_format == "json":
        click.echo(json.dumps(all_members, ensure_ascii=False, indent=2))
    else:
        for m in all_members:
            prefix = "  " * m["level"]
            click.echo(f"{prefix}{m['title']} (ns: {m['ns']})")


@cli.command()
@click.argument("title")
@add_options(_common_options)
@_json_option
def page(title, language, user_agent, variant, extract_format, namespace, output_format):
    """Show metadata and existence info for a Wikipedia page.

    TITLE is the Wikipedia page title.

    \b
    Examples:
        wikipedia-api page "Python (programming language)"
        wikipedia-api page "Python (programming language)" --json
    """
    wiki = _make_wiki(user_agent, language, variant, extract_format)
    p = _get_page(wiki, title, namespace)

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

    if output_format == "json":
        click.echo(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        for k, v in info.items():
            click.echo(f"{k}: {v}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
