from rich import print as rprint, box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import os

import imdb_scraper


def show_movie_details():
    """Show details of a movie"""
    os.system("clear")
    # download data
    movie_id = input("Enter a movie ID: ")
    print("Loading might take a second...")
    # movie_id = "tt0111161"
    movie = imdb_scraper.Movie(movie_id, load_credits=True)
    movie.load()

    # prepare data
    data_to_print = [
        # title
        Panel(Align(movie.original_title, align="left"), style="bright_cyan", width=len(movie.original_title) + 4),
        # plot summary
        "\nPlot Summary:",
        Text(movie.plot_summary, style="", justify="full"),
        "\n"
    ]

    # movie details
    table = Table(title="", box=box.SIMPLE_HEAD)
    table.add_column("Movie Details", justify="left", style="bright_cyan", no_wrap=True)
    table.add_column("", justify="left", style="bright_green", no_wrap=True)
    for variable in ("year", "genres", "metacritic_score", "imdb_rating"):
        value = getattr(movie, variable)
        if variable == "genres":
            value = ", ".join(value)
        table.add_row(variable.capitalize().replace("_", " "), str(value))
    data_to_print.append(table)
    data_to_print.append("\n")

    # present data
    os.system("clear")
    for p in data_to_print:
        rprint(p)

    # cast
    cast_table = Table(title="Cast", box=box.SIMPLE_HEAD)
    cast_table.add_column("Actor", justify="left", style="bright_cyan", no_wrap=True)
    cast_table.add_column("Character", justify="left", style="bright_green", no_wrap=True)
    for actor, character in movie.cast[:5]:
        cast_table.add_row(actor.name, character)
    data_to_print.append(cast_table)
    rprint(cast_table)


if __name__ == '__main__':
    show_movie_details()
    input("Press enter to exit...")
