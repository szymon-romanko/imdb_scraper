from rich.console import Console
from rich.table import Table
import os

import imdb_scraper


def show_top_movies():
    """Show list of the top 250 movies on IMDB"""
    os.system("clear")
    movies = imdb_scraper.get_top_250_movies()

    table = Table(title="IMDb Top 250 Movies")
    table.add_column("Rank", justify="right", style="cyan")
    table.add_column("Title", justify="left", style="bright_cyan", no_wrap=True)
    table.add_column("Rating", style="bright_green")
    for i, movie in enumerate(movies):
        table.add_row(str(i + 1) + ".", movie.original_title, str(movie.imdb_rating))

    console = Console()
    console.print(table)


if __name__ == '__main__':
    show_top_movies()
    input("Press enter to exit...")
