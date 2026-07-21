import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import F
from main.models import Movie
from contenthandler.picture_helper import pictureHelper
from contenthandler.content_handler import handler as ch


class Command(BaseCommand):
    help = "Renames cover folders from ASIN to EAN. Keeps ASIN if EAN already exists."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only prints what would be done without actually modifying any files.",
        )
        parser.add_argument(
            "--update-db",
            action="store_true",
            help="Update the movies within database. This might take a while.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        update_db = options["update_db"]
        helper = pictureHelper()

        cover_dir = os.path.join(settings.MEDIA_ROOT, "cover")
        if not os.path.exists(cover_dir):
            self.stdout.write(
                self.style.ERROR(f"Cover directory {cover_dir} does not exist.")
            )
            return

        self.stdout.write("Reading directory contents (for maximum performance)...")
        existing_folders = set(os.listdir(cover_dir))

        self.stdout.write("Loading affected movies from the database...")

        movies_query = (
            Movie.objects.exclude(asin="")
            .exclude(ean="")
            .exclude(asin__isnull=True)
            .exclude(ean__isnull=True)
            .exclude(asin=F("ean"))
            .values_list("asin", "ean")
            .distinct()
        )

        total_movies = movies_query.count()
        self.stdout.write(f"Found unique ASIN/EAN pairs to check: {total_movies}")

        renamed_count = 0
        skipped_count = 0
        not_found_count = 0

        for asin, ean in movies_query.iterator(chunk_size=10000):
            if asin in existing_folders:
                if ean in existing_folders:
                    # EAN version is already available -> keep ASIN
                    skipped_count += 1
                else:
                    # Rename ASIN folder to EAN folder
                    if not dry_run:
                        helper.picture_folder_rename(old_folder=asin, new_folder=ean)

                        # Update in-memory set in case subsequent movies reference the same EAN
                        existing_folders.remove(asin)
                        existing_folders.add(ean)

                    renamed_count += 1
            else:
                not_found_count += 1

            # Console feedback for long-running script
            processed = renamed_count + skipped_count + not_found_count
            if processed % 10000 == 0:
                self.stdout.write(f"{processed} records processed...")

        # Final report
        self.stdout.write(self.style.SUCCESS("\n=== PROCESS COMPLETED ==="))
        self.stdout.write(f"Successfully renamed:       {renamed_count}")
        self.stdout.write(f"Skipped (EAN exists):       {skipped_count}")
        self.stdout.write(f"No ASIN folder found:       {not_found_count}")

        self.stdout.write("\nChecking for 'mobile_cover.jpg' files to delete...")
        deleted_mobile_covers = 0

        # We iterate over the up-to-date in-memory list of folders
        for folder_name in existing_folders:
            mobile_cover_path = os.path.join(cover_dir, folder_name, "mobile_cover.jpg")

            if os.path.exists(mobile_cover_path):
                if not dry_run:
                    try:
                        os.remove(mobile_cover_path)
                        deleted_mobile_covers += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error deleting {mobile_cover_path}: {e}")
                        )
                else:
                    deleted_mobile_covers += 1

        self.stdout.write(self.style.SUCCESS("=== CLEANUP COMPLETED ==="))
        self.stdout.write(f"Deleted 'mobile_cover.jpg': {deleted_mobile_covers}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\nNOTE: This was a DRY RUN. No files were renamed.")
            )

        if update_db:
            self.stdout.write(f"\nCheck Movie picture availability flags now. ")

            handler = ch()
            handler.check_all_picture_available()
            self.stdout.write(self.style.SUCCESS("DONE"))
