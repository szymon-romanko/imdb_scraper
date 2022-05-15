import requests as r
from bs4 import BeautifulSoup as Bs


def read_html_table(element) -> list[list]:
    """Read html table and return it as 2 dimensional list"""
    table_data = []  # hold values that will be returned
    table_body = element.find("tbody")
    if table_body is None:  # for tables that don't use tbody
        table_body = element

    for row in table_body.find_all("tr"):  # iterate over each row
        columns = row.find_all("td")
        table_data.append(columns)
    return table_data


def process_table(table, first_index: int = 0, second_index: int = 1, save_href: bool = False) -> list[list]:
    """Takes 2 dimensional list and returns filtered out list with values in specified columns

    :param table: 2 dimensional list
    :param first_index: index of first column
    :param second_index: index of second column
    :param save_href: if True, href from first column will be saved instead of text
    :return: filtered out 2 dimensional list
    """
    list_data = []  # hold values that will be returned
    for row in table:  # iterate over each row
        if len(row) < max(first_index, second_index):  # if there isn't enough columns, skip the row
            continue
        if row[first_index].text in ("", " ", "\xa0", None):  # if key is empty, skip the row
            continue
        if save_href:  # save href
            key = row[first_index].find("a").get("href").split("/")[2]  # remove "/name/" from href
        else:  # save regular text
            key = row[first_index].text

        list_data.append([sanitize_string(key), sanitize_string(row[second_index].text)])  # save values to list
    return list_data


def sanitize_string(string: str) -> str:
    """Remove unwanted characters from string"""
    if string is None:  # if string is None, return empty string
        return ""
    while "\n" in string:  # remove newlines
        string = string.replace("\n", "")
    while "\xa0" in string:  # remove non-breaking spaces
        string = string.replace("\xa0", "")
    while "  " in string:  # remove double spaces
        string = string.replace("  ", " ")
    return string.strip("\n \xa0")  # remove leading and trailing whitespace


class Base(object):
    """Base for other classes, makes them load site only when data is requested"""

    def __init__(self):
        self.loaded = False

    def __getattribute__(self, item):
        """Calls self.load() when data is requested"""
        if not object.__getattribute__(self, 'loaded') and object.__getattribute__(self, item) is None:
            self.loaded = True
            self.load()  # load data only when its accessed
        return object.__getattribute__(self, item)

    def load(self) -> None:
        """Override this method to load data from site"""
        pass


class Movie(Base):
    def __init__(self, movie_id: str, load_credits: bool = False):
        """Class holding information about movie
        If you want to load credits, set load_credits to True or load them manually with Movie.read_fullcredits()

        :param movie_id: id of movie  (e.g. "tt0111161")
        :param load_credits: if True, credits will be loaded from site (default: False)
        """
        # run __init__ of parent class
        super().__init__()

        # basic info
        self.movie_id = movie_id  # str
        self.base_url = f"https://www.imdb.com/title/{self.movie_id}"  # str
        self.load_credits = load_credits  # bool

        # loaded in read_releaseinfo()
        self.original_title = None  # str
        self.year = None  # int
        self.release_dates = None  # dict
        self.titles = None  # dict
        # loaded in read_fullcredits()
        self.credits = None  # dict
        self.cast = None  # list
        # loaded in read_titlepage()
        self.plot_summary = None  # str
        self.genres = None  # list
        self.metacritic_score = None  # int
        self.imdb_rating = None  # float

    def load(self) -> None:
        """Loads all data from site"""
        self.read_releaseinfo()
        self.read_titlepage()
        if self.load_credits:  # optional data
            self.read_fullcredits()

    def read_releaseinfo(self) -> None:
        """Reads release info page  (https://www.imdb.com/title/{movie_id}/releaseinfo)"""
        releaseinfo_page = r.get(self.base_url + "/releaseinfo")
        soup = Bs(releaseinfo_page.content, "html.parser")

        # get titles  (from the AKAs section)
        title_table = read_html_table(soup.find("table", {"class": "ipl-zebra-list akas-table-test-only"}))
        self.titles = process_table(title_table)

        # get release dates
        release_dates_table = read_html_table(
            soup.find("table", {"class": "ipl-zebra-list ipl-zebra-list--fixed-first release-dates-table-test-only"}))
        self.release_dates = process_table(release_dates_table)

        self.original_title = [title for title in self.titles if title[0] == "(original title)"][0][1]
        try:
            self.year = int(self.release_dates[0][1][-4:])
        except ValueError:
            self.year = None

    def read_fullcredits(self) -> None:
        """Reads full credits page  (https://www.imdb.com/title/{movie_id}/fullcredits)"""
        fullcredits = {}
        fullcredits_page = r.get(self.base_url + "/fullcredits")
        soup = Bs(fullcredits_page.content, "html.parser")

        content = soup.find("div", {"id": "fullcredits_content"})
        headers = content.find_all("h4")
        tables = content.find_all("table")
        for header, table in zip(headers, tables):  # for each section
            if table.get("class") == ["cast_list"]:  # cast section
                fullcredits[sanitize_string(header.text)] = process_table(read_html_table(table), first_index=1,
                                                                          second_index=3, save_href=True)
            else:
                fullcredits[sanitize_string(header.text)] = process_table(read_html_table(table), first_index=0,
                                                                          second_index=-1, save_href=True)

        for key, table in fullcredits.items():  # replace actor_id with Actor class instance
            for row_index in range(len(table)):
                fullcredits[key][row_index][0] = Actor(table[row_index][0])
        self.credits = fullcredits
        self.cast = [self.credits[section] for section in self.credits if "Cast" in section][0]  # get cast list

    def read_titlepage(self) -> None:
        """Reads title page (https://www.imdb.com/title/{movie_id})"""
        titlepage_page = r.get(self.base_url)
        soup = Bs(titlepage_page.content, "html.parser")

        # get plot summary
        plot_summary_tag = soup.find("span", {"data-testid": "plot-l"})
        if plot_summary_tag is not None:
            self.plot_summary = plot_summary_tag.text

        # get genres
        generes_div = soup.find("div", {"data-testid": "genres"})
        self.genres = [genre.text for genre in generes_div.find_all("a")]

        # get metacritic score
        metacritic_score_tag = soup.find("span", {"class": "score-meta"})
        if metacritic_score_tag is not None:
            self.metacritic_score = int(metacritic_score_tag.text)

        # get imdb rating
        imdb_rating_tag = soup.find("span", {"class": "sc-7ab21ed2-1 jGRxWM"})
        if imdb_rating_tag is not None:
            self.imdb_rating = float(imdb_rating_tag.text)


class Actor(Base):
    def __init__(self, actor_id: str, load_filography: bool = False):
        super().__init__()
        # basic info
        self.actor_id = actor_id  # str
        self.base_url = f"https://www.imdb.com/name/{self.actor_id}"  # str
        self.soup = None  # html soup of main page
        self.load_filography = load_filography  # bool

        self.name = None  # str
        self.biography = None  # str
        self.filmography = None  # dict

    def load(self) -> None:
        # get main page
        main_page = r.get(self.base_url)
        self.soup = Bs(main_page.content, "html.parser")
        # get name
        self.name = sanitize_string(self.soup.find("span", {"class": "itemprop"}).text)
        # get biography
        bio_page = r.get(self.base_url + "/bio")
        bio_page_soup = Bs(bio_page.content, "html.parser")
        self.biography = sanitize_string(bio_page_soup.find("div", {"class": "soda odd"}).find("p").text)
        # get filmography
        if self.load_filography:
            self.read_filmography()

    def read_filmography(self) -> None:
        """Reads filmography page (https://www.imdb.com/name/{actor_id})"""
        filmography = {}
        filmography_div = self.soup.find("div", {"id": "filmography"})
        headers = filmography_div.find_all("div", {"class": "head"})
        tables = filmography_div.find_all("div", {"class": "filmo-category-section"})
        for header, table in zip(headers, tables):  # for each section/category
            tmp_entries = []
            rows = [p for p in table.find_all("div") if p.get("class") is not None and "filmo-row" in p.get("class")]
            for row in rows:  # for each movie/series
                year, category, role = None, None, None
                # year
                year = sanitize_string(row.find("span", {"class": "year_column"}).text)[:4]  # 4 frist digits only
                if year != "":
                    year = int(year)
                # category and role
                br_tag = row.find("br")
                if br_tag is not None:
                    category = sanitize_string(br_tag.previousSibling.text)
                    role = sanitize_string(br_tag.nextSibling.text)
                # combine into dict

                tmp_entries.append({
                    "title": sanitize_string(row.find("b").text),
                    "movie": Movie(row.find("a").get("href").split("/")[2]),
                    "year": year,
                    "type": category,
                    "role": role
                })

            filmography[sanitize_string(header.text)[8:]] = tmp_entries
        self.filmography = filmography


def search(query: str, n: int = 10, titles: bool = True, actors: bool = True) -> dict[str, list]:
    """Searches imdb for movies/actors matching query.

    :param query: string to search for
    :param n: number of results to return
    :param titles: whether to search for titles
    :param actors: whether to search for actors
    :return: dict of lists of Movie/Actor objects
    """
    search_results = {}

    # search for titles
    if titles:
        search_results["titles"] = []
        # get search page
        search_page = r.get(f"https://www.imdb.com/find?q={query}&s=tt")  # add &tty=ft to search for movies only
        search_page_soup = Bs(search_page.content, "html.parser")
        # get results
        results = search_page_soup.find_all("td", {"class": "result_text"})
        for result in results[:n]:
            search_results["titles"].append(Movie(result.find("a").get("href").split("/")[2]))
            search_results["titles"][-1].original_title = sanitize_string(result.find("a").text)

    # search for actors
    if actors:
        search_results["actors"] = []
        # get search page
        search_page = r.get(f"https://www.imdb.com/find?q={query}&s=nm")  # add &tty=ft to search for movies only
        search_page_soup = Bs(search_page.content, "html.parser")
        # get results
        results = search_page_soup.find_all("td", {"class": "result_text"})
        for result in results[:n]:
            search_results["actors"].append(Actor(result.find("a").get("href").split("/")[2]))
            search_results["actors"][-1].original_title = sanitize_string(result.find("a").text)

    return search_results


def get_top_250_movies() -> list[Movie]:
    """Returns list of top 250 movies"""
    movies = []
    page = r.get("https://www.imdb.com/chart/top")
    soup = Bs(page.content, "html.parser")

    table = soup.find("table", {"class": "chart"})
    html_table = read_html_table(table)
    for row in html_table:
        title_cell = row[1]
        rating_cell = row[2]
        title = title_cell.find("a").text
        movie_id = title_cell.find("a").get("href").split("/")[2]
        rating = float(rating_cell.text)
        movies.append(Movie(movie_id))
        movies[-1].original_title = title
        movies[-1].imdb_rating = rating

    return movies
