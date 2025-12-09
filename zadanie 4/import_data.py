import csv
import os
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()


def import_movies():
    file_path = os.path.join("database", "movies.csv")
    if not os.path.exists(file_path):
        print(f"Plik {file_path} nie istnieje!")
        return

    print("Importowanie filmów...")
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing = db.query(models.Movie).filter(models.Movie.id == int(row['movieId'])).first()
            if not existing:
                movie = models.Movie(
                    id=int(row['movieId']),
                    title=row['title'],
                    genres=row['genres']
                )
                db.add(movie)
    db.commit()
    print("Filmy zaimportowane.")


def import_links():
    file_path = os.path.join("database", "links.csv")
    if not os.path.exists(file_path):
        return

    print("Importowanie linków...")
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing = db.query(models.Link).filter(models.Link.movie_id == int(row['movieId'])).first()
            if not existing:
                link = models.Link(
                    movie_id=int(row['movieId']),
                    imdb_id=row['imdbId'],
                    tmdb_id=row['tmdbId']
                )
                db.add(link)
    db.commit()
    print("Linki zaimportowane.")


def import_tags():
    file_path = os.path.join("database", "tags.csv")
    if not os.path.exists(file_path):
        return

    print("Importowanie tagów...")
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tag = models.Tag(
                user_id=int(row['userId']),
                movie_id=int(row['movieId']),
                tag=row['tag'],
                timestamp=int(row['timestamp'])
            )
            db.add(tag)
    db.commit()
    print("Tagi zaimportowane.")


def import_ratings():
    file_path = os.path.join("database", "ratings.csv")
    if not os.path.exists(file_path):
        return

    print("Importowanie ocen (to może chwilę potrwać)...")
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            rating = models.Rating(
                user_id=int(row['userId']),
                movie_id=int(row['movieId']),
                rating=float(row['rating']),
                timestamp=int(row['timestamp'])
            )
            db.add(rating)
            count += 1
            if count > 1000:
                break

    db.commit()
    print(f"Zaimportowano {count} ocen.")


if __name__ == "__main__":
    import_movies()
    import_links()
    import_tags()
    import_ratings()

    db.close()
    print("Zakończono import danych.")