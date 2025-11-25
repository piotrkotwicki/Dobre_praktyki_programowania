from fastapi import FastAPI, HTTPException
import csv
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "database"

app = FastAPI(title="Zadanie 2- Fast Api")

class Movie:
    def __init__(self, movieId: int, title: str, genres: str):
        self.movieId = int(movieId)
        self.title = title
        self.genres = genres

class Link:
    def __init__(self, movieId: int, imdbId: str, tmdbId: str):
        self.movieId = int(movieId)
        self.imdbId = imdbId
        self.tmdbId = tmdbId

class Rating:
    def __init__(self, userId: int, movieId: int, rating: float, timestamp: str):
        self.userId = int(userId)
        self.movieId = int(movieId)
        self.rating = float(rating)
        self.timestamp = timestamp

class Tag:
    def __init__(self, userId: int, movieId: int, tag: str, timestamp: str):
        self.userId = int(userId)
        self.movieId = int(movieId)
        self.tag = tag
        self.timestamp = timestamp


def load_csv_rows(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {path}")
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def load_movies() -> List[Movie]:
    path = DATA_DIR / "movies.csv"
    movies = []
    for row in load_csv_rows(path):
        movies.append(Movie(movieId=row["movieId"], title=row["title"], genres=row["genres"]))
    return movies


def load_links() -> List[Link]:
    path = DATA_DIR / "links.csv"
    links = []
    for row in load_csv_rows(path):
        links.append(Link(movieId=row["movieId"], imdbId=row.get("imdbId", ""), tmdbId=row.get("tmdbId", "")))
    return links


def load_ratings() -> List[Rating]:
    path = DATA_DIR / "ratings.csv"
    ratings = []
    for row in load_csv_rows(path):
        ratings.append(Rating(userId=row["userId"], movieId=row["movieId"], rating=row["rating"], timestamp=row["timestamp"]))
    return ratings


def load_tags() -> List[Tag]:
    path = DATA_DIR / "tags.csv"
    tags = []
    for row in load_csv_rows(path):
        tags.append(Tag(userId=row["userId"], movieId=row["movieId"], tag=row["tag"], timestamp=row["timestamp"]))
    return tags


DB = {"movies": [], "links": [], "ratings": [], "tags": []}


@app.on_event("startup")
def load_data():
    try:
        DB["movies"] = load_movies()
        DB["links"] = load_links()
        DB["ratings"] = load_ratings()
        DB["tags"] = load_tags()
        print("Dane wczytane pomyślnie!")
        for name, data in DB.items():
            print(f"{name}: {len(data)} rekordów")
    except Exception as e:
        print("Błąd podczas wczytywania danych:", e)


@app.get("/")
def root():
    return {"hello": "world"}


@app.get("/movies")
def get_movies():
    if not DB["movies"]:
        raise HTTPException(status_code=500, detail="Dane filmów nie są wczytane.")
    return [m.__dict__ for m in DB["movies"]]


@app.get("/links")
def get_links():
    if not DB["links"]:
        raise HTTPException(status_code=500, detail="Dane linków nie są wczytane.")
    return [l.__dict__ for l in DB["links"]]


@app.get("/ratings")
def get_ratings(limit: int = 100):
    if not DB["ratings"]:
        raise HTTPException(status_code=500, detail="Dane ocen nie są wczytane.")
    return [r.__dict__ for r in DB["ratings"][:limit]]


@app.get("/tags")
def get_tags():
    if not DB["tags"]:
        raise HTTPException(status_code=500, detail="Dane tagów nie są wczytane.")
    return [t.__dict__ for t in DB["tags"]]
