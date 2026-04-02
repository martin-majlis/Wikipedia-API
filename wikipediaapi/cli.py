r"""Command line interface for Wikipedia-API."""

import click

import wikipediaapi
from wikipediaapi.commands import category_commands
from wikipediaapi.commands import geo_commands
from wikipediaapi.commands import image_commands
from wikipediaapi.commands import link_commands
from wikipediaapi.commands import page_commands
from wikipediaapi.commands import search_commands


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    version=".".join(str(s) for s in wikipediaapi.__version__),
    prog_name="wikipedia-api",
)
def cli() -> click.Group:
    r"""Command line tool for querying Wikipedia using Wikipedia-API.

    Supports fetching page summaries, full text, sections, links,
    backlinks, language links, categories, category members,
    coordinates, images, geosearch, random pages, and search.

    Every command requires a TITLE argument — the Wikipedia page title.

    Examples:
    \b
        wikipedia-api summary "Python (programming language)"
        wikipedia-api links "Python (programming language)" --language cs
        wikipedia-api categories "Python (programming language)" --json
        wikipedia-api coordinates "Mount Everest"
        wikipedia-api geosearch --coord "51.5074|-0.1278"
        wikipedia-api search "Python programming"
    """
    return cli


# Register all command modules
page_commands.register_commands(cli)
link_commands.register_commands(cli)
category_commands.register_commands(cli)
geo_commands.register_commands(cli)
image_commands.register_commands(cli)
search_commands.register_commands(cli)


def main() -> None:
    r"""Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
