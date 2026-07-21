import os
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image


class Command(BaseCommand):
    help = "Finds all .png files in the cover directory, converts them to .jpg and deletes the .png."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only prints what would be done without actually modifying any files.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        cover_dir = os.path.join(settings.MEDIA_ROOT, "cover")

        if not os.path.exists(cover_dir):
            self.stdout.write(
                self.style.ERROR(f"Cover directory {cover_dir} does not exist.")
            )
            return

        self.stdout.write("Scanning for .png files (this might take a moment)...")

        png_files = []
        for entry in os.scandir(cover_dir):
            if entry.is_dir():
                for sub_entry in os.scandir(entry.path):
                    if sub_entry.is_file() and sub_entry.name.lower().endswith(".png"):
                        png_files.append(sub_entry.path)

        self.stdout.write(f"Found {len(png_files)} .png files to convert.")

        converted_count = 0
        error_count = 0

        for png_path in png_files:
            # Change extension from .png to .jpg (or .PNG to .jpg)
            jpg_path = png_path.rsplit(".", 1)[0] + ".jpg"

            if not dry_run:
                try:
                    with Image.open(png_path) as img:
                        rgb_im = img.convert("RGB")
                        rgb_im.save(jpg_path, "JPEG", quality=100)

                    os.remove(png_path)
                    converted_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error converting {png_path}: {e}")
                    )
                    error_count += 1
            else:
                self.stdout.write(f"[DRY RUN] Would convert: {png_path} -> {jpg_path}")
                converted_count += 1

        self.stdout.write(self.style.SUCCESS("\n=== CONVERSION COMPLETED ==="))
        self.stdout.write(f"Converted successfully: {converted_count}")
        self.stdout.write(f"Errors:                 {error_count}")
