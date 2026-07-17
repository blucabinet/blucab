from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.apps import apps
from django.db import connection


class Command(BaseCommand):
    help = "Automatically fixes PostgreSQL auto-increment sequences after a database import."

    def add_arguments(self, parser):
        # Allow passing an app name, but default to 'main'
        parser.add_argument(
            "app_label",
            nargs="?",
            type=str,
            default="main",
            help='The app label to reset sequences for (defaults to "main").',
        )

    def handle(self, *args, **options):
        app_label = options["app_label"]

        try:
            # Fetch the configuration and models of the specified app
            app_config = apps.get_app_config(app_label)
        except LookupError:
            self.stderr.write(
                self.style.ERROR(f"App '{app_label}' could not be found.")
            )
            return

        models = list(app_config.get_models())
        if not models:
            self.stdout.write(
                self.style.WARNING(f"No models found in app '{app_label}'.")
            )
            return

        # Generate the database-specific SQL statements to reset sequences
        # (e.g., SELECT setval(...) for PostgreSQL)
        statements = connection.ops.sequence_reset_sql(no_style(), models)

        if not statements:
            self.stdout.write(
                self.style.WARNING(f"No sequence reset required for app '{app_label}'.")
            )
            return

        # Execute the generated SQL statements directly on the database
        with connection.cursor() as cursor:
            for sql in statements:
                try:
                    cursor.execute(sql)
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(f"Error executing SQL: {sql}\nException: {e}")
                    )
                    return

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully reset auto-increment sequences for app '{app_label}'."
            )
        )
