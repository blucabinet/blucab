import re
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import Movie, Format
from contenthandler.amazon import (
    REMOVE_ITEMS,
    BLURAY_ITEMS,
    DVD_ITEMS,
    BLURAY_UHD_ITEMS,
    BLURAY_3D_ITEMS,
    FORMAT_BLURAY,
    FORMAT_DVD,
    FORMAT_UNKNOWN,
    PRODUCT_DESCRIPTION_ITEMS,
)


class Command(BaseCommand):
    help = "Cleans up movie titles and automatically sets formats/flags based on the original title."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        all_items_to_remove = (
            REMOVE_ITEMS | BLURAY_ITEMS | DVD_ITEMS | BLURAY_UHD_ITEMS | BLURAY_3D_ITEMS
        )

        self.cleanup_strings = sorted(all_items_to_remove, key=len, reverse=True)
        self.print_output = False

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run the script without saving changes to the database.",
        )
        parser.add_argument(
            "--print-log",
            action="store_true",
            help="Show a full debug output about each changed content.",
        )

    def handle(self, *args, **options):
        start_time = time.time()

        is_dry_run = options["dry_run"]

        if is_dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN MODE: No changes will be saved to the database."
                )
            )

        fmt_bluray, _ = Format.objects.get_or_create(name=FORMAT_BLURAY)
        fmt_dvd, _ = Format.objects.get_or_create(name=FORMAT_DVD)
        fmt_unknown, _ = Format.objects.get_or_create(name=FORMAT_UNKNOWN)

        movies = Movie.objects.all().iterator()

        updated_count = 0
        movies_to_update = []
        BATCH_SIZE = 5000

        for movie in movies:
            needs_update = False

            if self._clean_title(movie):
                needs_update = True

            if self._clean_content(movie):
                needs_update = True

            if self._update_media_flags_and_format(
                movie, fmt_bluray, fmt_dvd, fmt_unknown
            ):
                needs_update = True

            if needs_update:
                movies_to_update.append(movie)
                updated_count += 1

            if len(movies_to_update) >= BATCH_SIZE:
                if not is_dry_run:
                    Movie.objects.bulk_update(
                        movies_to_update,
                        [
                            "title_clean",
                            "is_bluray_uhd",
                            "is_bluray_3d",
                            "format",
                            "content",
                        ],
                    )
                movies_to_update = []

        if movies_to_update and not is_dry_run:
            Movie.objects.bulk_update(
                movies_to_update,
                [
                    "title_clean",
                    "is_bluray_uhd",
                    "is_bluray_3d",
                    "format",
                    "content",
                ],
            )

        end_time = time.time()
        duration = round(end_time - start_time, 2)

        action_verb = "would be" if is_dry_run else "were"
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully finished in {duration} seconds. "
                f"{updated_count} movies {action_verb} updated."
            )
        )

    # -------------------------------------------------------------------------
    # CLEANUP MODULES
    # -------------------------------------------------------------------------

    def _clean_title(self, movie: Movie) -> bool:
        """
        Cleans the title by removing substrings defined in various item sets
        and resolving HTML entities like &amp; to &.
        Never touches the original 'title', only updates 'title_clean'.
        Returns True if 'title_clean' was changed.
        """
        new_clean_title = movie.title

        # Skip whole process already, if title_clean is different already
        if new_clean_title != movie.title_clean:
            return False

        # Remove all combined items (longest first to avoid partial string replacements)
        for item in self.cleanup_strings:
            new_clean_title = new_clean_title.replace(item, "")

        junk_words = (
            r"\bBonus\b|\bUV\s*Copy\b|\bCD\b|\bMediabook\b|\bSet\b|\bOVA\b|\bDoku-BD\b"
        )

        regex_junk = rf"(?:\s|\+|-|&|\b\d{{1,2}}\b|\bs\b|{junk_words})*"

        new_clean_title = re.sub(
            rf"\[{regex_junk}\]", "", new_clean_title, flags=re.IGNORECASE
        )
        new_clean_title = re.sub(
            rf"\({regex_junk}\)", "", new_clean_title, flags=re.IGNORECASE
        )
        # ------------------------------

        # Replace HTML encoded ampersands
        new_clean_title = new_clean_title.replace("&amp;", "&")

        # Clean up multiple whitespaces left by removals and strip edges
        new_clean_title = re.sub(" +", " ", new_clean_title).strip()

        # Only mark as changed if the new clean title differs from the current one
        if movie.title_clean != new_clean_title:
            if self.print_output:
                self.stdout.write(
                    f"Title cleaned: '{movie.title_clean}' -> '{new_clean_title}'"
                )
            movie.title_clean = new_clean_title
            return True

        return False

    def _update_media_flags_and_format(
        self, movie: Movie, fmt_bluray: Format, fmt_dvd: Format, fmt_unknown: Format
    ) -> bool:
        """
        Sets is_bluray_uhd, is_bluray_3d, and format based on the original title.
        Only updates values if they are not already set.
        Returns True if any field was changed.
        """
        has_changed = False
        original_title = movie.title

        # Check UHD (Only update if currently False)
        if not movie.is_bluray_uhd:
            if any(item in original_title for item in BLURAY_UHD_ITEMS):
                movie.is_bluray_uhd = True
                if self.print_output:
                    self.stdout.write(f"Flag set: UHD for '{original_title}'")
                has_changed = True

        # Check 3D (Only update if currently False)
        if not movie.is_bluray_3d:
            if any(item in original_title for item in BLURAY_3D_ITEMS):
                movie.is_bluray_3d = True
                if self.print_output:
                    self.stdout.write(f"Flag set: 3D for '{original_title}'")
                has_changed = True

        # Check Format
        # Only update if format is currently missing OR set to "Unknown"
        if not movie.format or movie.format == fmt_unknown:
            if any(item in original_title for item in BLURAY_ITEMS):
                movie.format = fmt_bluray
                if self.print_output:
                    self.stdout.write(f"Format set: Blu-Ray for '{original_title}'")
                has_changed = True
            elif any(item in original_title for item in DVD_ITEMS):
                movie.format = fmt_dvd
                if self.print_output:
                    self.stdout.write(f"Format set: DVD for '{original_title}'")
                has_changed = True

        return has_changed

    def _clean_content(self, movie: Movie) -> bool:
        """
        Cleans the content field by removing unwanted promotional
        phrases or prefixes defined in PRODUCT_DESCRIPTION_ITEMS.
        Returns True if the 'content' field was changed.
        """
        # Skip if the movie has no content (None or empty string)
        if not movie.content:
            return False

        new_content = movie.content

        # Remove all predefined items
        for item in PRODUCT_DESCRIPTION_ITEMS:
            new_content = new_content.replace(item, "")

        # Strip any remaining whitespaces or newlines at the edges
        new_content = new_content.strip()

        # Update the model and return True if changes were made
        if movie.content != new_content:
            movie.content = new_content
            return True

        return False
