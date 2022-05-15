from rich.console import Console
from rich.table import Table
import os

import imdb_scraper


def search_for_movie():
    """Searches for a movie on IMDb"""
    os.system("clear")
    title = input("Enter a movie title: ")
    movies = imdb_scraper.search(title, actors=False)

    table = Table(title="Search Results")
    table.add_column("Title", justify="left", style="bright_cyan", no_wrap=True)
    table.add_column("Movie ID", style="bright_green")
    for movie in movies["titles"]:
        table.add_row(movie.original_title, movie.movie_id)

    console = Console()
    console.print(table)


if __name__ == '__main__':
    search_for_movie()
    input("Press enter to exit...")
