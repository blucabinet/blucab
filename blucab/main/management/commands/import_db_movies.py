import MySQLdb
import MySQLdb.cursors
import datetime
from django.core.management.base import BaseCommand
from main.models import Movie, Format, Actor, Director, Studio, Language, ContentRating
from contenthandler.amazon import REMOVE_ITEMS


class Command(BaseCommand):
    help = "Imports movie data from an external MySQL export and safely links M2M sub-tables."

    def get_related_ids(self, cursor, table_name, id_column, movie_id):
        """
        Helper function to safely load relations from MySQL.
        Catches exceptions in case a table doesn't exist in the old export.
        """
        try:
            cursor.execute(
                f"SELECT {id_column} FROM {table_name} WHERE movie_id = %s", (movie_id,)
            )
            return [rel[id_column] for rel in cursor.fetchall()]
        except MySQLdb.OperationalError:
            return []

    def handle(self, *args, **kwargs):
        # 1. Establish connection to the temporary MariaDB/MySQL database
        try:
            connection = MySQLdb.connect(
                host="blucab-flickrack-db",
                port=3306,
                user="root",
                password="insecure-flickrack_root_password",
                database="flickrack",
                cursorclass=MySQLdb.cursors.DictCursor,
            )
        except MySQLdb.Error as e:
            self.stdout.write(self.style.ERROR(f"Database connection error: {e}"))
            return

        with connection.cursor() as cursor:
            self.stdout.write(
                self.style.SUCCESS("Connected to MariaDB. Loading helper tables...")
            )

            # --- 2. IMPORT HELPER TABLES ---

            # Formats
            cursor.execute("SELECT * FROM format")
            format_map = {}
            for row in cursor.fetchall():
                obj, _ = Format.objects.get_or_create(
                    id=row["format_id"], defaults={"name": row["name"]}
                )
                format_map[row["format_id"]] = obj

            # Content Ratings
            cursor.execute("SELECT * FROM audience_rating")
            rating_map = {}
            for row in cursor.fetchall():
                obj, _ = ContentRating.objects.get_or_create(name=row["name"].strip())
                rating_map[row["audience_rating_id"]] = obj

            # Actors
            cursor.execute("SELECT * FROM actor")
            actor_map = {}
            for row in cursor.fetchall():
                obj, _ = Actor.objects.get_or_create(name=row["name"].strip())
                actor_map[row["actor_id"]] = obj

            # Directors
            cursor.execute("SELECT * FROM director")
            director_map = {}
            for row in cursor.fetchall():
                obj, _ = Director.objects.get_or_create(name=row["name"].strip())
                director_map[row["director_id"]] = obj

            # Studios
            cursor.execute("SELECT * FROM studio")
            studio_map = {}
            for row in cursor.fetchall():
                obj, _ = Studio.objects.get_or_create(name=row["name"].strip())
                studio_map[row["studio_id"]] = obj

            self.stdout.write(
                self.style.SUCCESS("Helper tables loaded. Importing movies...")
            )

            # --- 3. IMPORT MOVIES (SMART MERGE LOGIC) ---
            cursor.execute("SELECT * FROM movie")
            movies = cursor.fetchall()

            stats = {"created": 0, "updated": 0}

            for row in movies:
                # Convert Unix timestamps to pure Date objects (for models.DateField)
                added_date = (
                    datetime.datetime.fromtimestamp(row["added"]).date()
                    if row["added"]
                    else None
                )
                updated_date = (
                    datetime.datetime.fromtimestamp(row["updated"]).date()
                    if row.get("updated")
                    else None
                )

                # Get Content Rating object
                content_rating_obj = rating_map.get(row["audience_rating_id"])

                # Clean identifiers
                ean_clean = row["ean"].strip() if row.get("ean") else ""
                asin_clean = row["movie_id"].strip() if row.get("movie_id") else ""

                # 3.1 Check if the movie already exists
                movie = None
                if ean_clean:
                    movie = Movie.objects.filter(ean=ean_clean).first()
                if not movie and asin_clean:
                    movie = Movie.objects.filter(asin=asin_clean).first()

                if movie:
                    # CASE A: MOVIE ALREADY EXISTS -> Only add missing/empty data (Merge)
                    if not movie.flickrack_id and row.get("flickrack_id"):
                        movie.flickrack_id = row["flickrack_id"]

                    if not movie.content and row.get("content"):
                        movie.content = row["content"]

                    if not movie.release_year and row.get("year"):
                        movie.release_year = row["year"]

                    # Only set content_rating if the current movie doesn't have one
                    if not movie.content_rating and content_rating_obj:
                        movie.content_rating = content_rating_obj

                    # Overwrite values that are safe to update continuously
                    movie.runtime = row["runtime"] if row["runtime"] else movie.runtime
                    movie.activated = bool(row["active"])

                    if updated_date:
                        movie.date_updated = updated_date
                    else:
                        movie.date_updated = datetime.date.today()

                    movie.save()
                    stats["updated"] += 1

                else:
                    # CASE B: NEW MOVIE -> Create entirely

                    title_db = row["title"]
                    title_db_clean = ""

                    for item in REMOVE_ITEMS:
                        title_db_clean = title_db.replace(item, "")

                    movie = Movie.objects.create(
                        ean=ean_clean,
                        asin=asin_clean,
                        title=title_db,
                        title_clean=title_db_clean,
                        flickrack_id=row.get("flickrack_id"),
                        format=format_map.get(row["format_id"]),
                        release_year=row.get("year"),
                        runtime=row.get("runtime"),
                        content_rating=content_rating_obj,
                        content=row.get("content"),
                        activated=bool(row["active"]),
                        date_added=added_date or datetime.date.today(),
                        date_updated=updated_date or datetime.date.today(),
                        needs_parsing=True,
                    )
                    stats["created"] += 1

                # --- 4. SAFELY ADD MANY-TO-MANY RELATIONS ---

                # 4.1 Actors
                actor_ids = self.get_related_ids(
                    cursor, "movie_has_actor", "actor_id", row["movie_id"]
                )
                actors_to_add = [
                    actor_map[aid] for aid in actor_ids if aid in actor_map
                ]
                if actors_to_add:
                    movie.actors.add(*actors_to_add)

                # 4.2 Directors
                director_ids = self.get_related_ids(
                    cursor, "movie_has_director", "director_id", row["movie_id"]
                )
                directors_to_add = [
                    director_map[did] for did in director_ids if did in director_map
                ]
                if directors_to_add:
                    movie.directors.add(*directors_to_add)

                # 4.3 Studios
                studio_ids = self.get_related_ids(
                    cursor, "movie_has_studio", "studio_id", row["movie_id"]
                )
                studios_to_add = [
                    studio_map[sid] for sid in studio_ids if sid in studio_map
                ]
                if studios_to_add:
                    movie.studios.add(*studios_to_add)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Import successfully completed! {stats['created']} movies created, {stats['updated']} movies updated."
                )
            )
