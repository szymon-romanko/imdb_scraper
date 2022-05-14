# IMDb scraper in python

### Requirements:

* requests https://pypi.org/project/requests/
* beautifulsoup4  https://pypi.org/project/beautifulsoup4/

## imdb_scraper.get_top_250_movies()

Returns list of top 250 movies

* **Return type**

  `list`[`Movie`]

## imdb_scraper.search(query, n=10, titles=True, actors=True)

Searches imdb for movies/actors matching query.

* **Parameters**

    * **query** (`str`) – string to search for

    * **n** (`int`) – number of results to return

    * **titles** (`bool`) – whether to search for titles

    * **actors** (`bool`) – whether to search for actors


* **Return type**

  `dict`[`str`, `list`]


* **Returns**

  dict of lists of Movie/Actor objects

## _class_ imdb_scraper.Movie(movie_id, load_credits=False)

Bases: `imdb_scraper.Base`

#### \__init__(movie_id, load_credits=False)

Class holding information about movie.
If you want to load credits, set load_credits to True or load them manually with Movie.read_fullcredits()

* **Parameters**

    * **movie_id** – id of movie  (e.g. “tt0111161”)

    * **load_credits** (`bool`) – if True, credits will be loaded from site (default: False)

#### load()

Call this if you want to manually load data from site

## _class_ imdb_scraper.Actor(actor_id)

Bases: `imdb_scraper.Base`

#### \__init__(actor_id)

#### load()

Call this if you want to manually load data from site
