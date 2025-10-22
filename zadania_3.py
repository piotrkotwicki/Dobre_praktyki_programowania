from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "app.db"
CSV_DIR = BASE_DIR / "database"

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Movie(Base):
    __tablename__ = "movies"

    movieId = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    genres = Column(String)

    links = relationship("Link", back_populates="movie")
    ratings = relationship("Rating", back_populates="movie")
    tags = relationship("Tag", back_populates="movie")


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    movieId = Column(Integer, ForeignKey("movies.movieId"))
    imdbId = Column(String)
    tmdbId = Column(String)

    movie = relationship("Movie", back_populates="links")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey("movies.movieId"))
    rating = Column(Float)
    timestamp = Column(String)

    movie = relationship("Movie", back_populates="ratings")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey("movies.movieId"))
    tag = Column(String)
    timestamp = Column(String)

    movie = relationship("Movie", back_populates="tags")


Base.metadata.create_all(engine)


def load_csv(path: Path):
    with path.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def import_data():
    db: Session = SessionLocal()
    for row in load_csv(CSV_DIR / "movies.csv"):
        db.add(Movie(movieId=row["movieId"], title=row["title"], genres=row["genres"]))
    db.commit()

    for row in load_csv(CSV_DIR / "links.csv"):
        db.add(Link(movieId=row["movieId"], imdbId=row.get("imdbId", ""), tmdbId=row.get("tmdbId", "")))
    db.commit()

    for row in load_csv(CSV_DIR / "ratings.csv"):
        db.add(Rating(userId=row["userId"], movieId=row["movieId"], rating=row["rating"], timestamp=row["timestamp"]))
    db.commit()

    for row in load_csv(CSV_DIR / "tags.csv"):
        db.add(Tag(userId=row["userId"], movieId=row["movieId"], tag=row["tag"], timestamp=row["timestamp"]))
    db.commit()
    db.close()
    print("Dane z CSV poprawnie zaimportowane do bazy danych.")


app = FastAPI(title="Zadanie 3- Sqlite i SQLalchemy")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"hello": "this is my database application"}


def to_dict(obj):
    data = obj.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


@app.get("/movies")
def get_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).all()
    return [to_dict(m) for m in movies]


@app.get("/links")
def get_links(db: Session = Depends(get_db)):
    links = db.query(Link).all()
    return [to_dict(l) for l in links]


@app.get("/ratings")
def get_ratings(limit: int = 100, db: Session = Depends(get_db)):
    ratings = db.query(Rating).limit(limit).all()
    return [to_dict(r) for r in ratings]


@app.get("/tags")
def get_tags(db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return [to_dict(t) for t in tags]
