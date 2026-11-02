import difflib
from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import Movie, Actor, Director, Studio


class Command(BaseCommand):
    help = "Cleans up dirty data in Actor, Director, and Studio M2M models."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without making any changes to the database (Simulation).",
        )
        parser.add_argument(
            "--fuzzy",
            action="store_true",
            help="Run the slow fuzzy matching algorithm to find typos.",
        )
        parser.add_argument(
            "--fix-caps",
            nargs="+",
            choices=["actors", "directors", "studios", "all"],
            help='Optional: Fix ALL CAPS entries for specified M2M fields. Use "all" or specific names (e.g. --fix-caps actors directors).',
        )

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.run_fuzzy = options["fuzzy"]

        # Parse which M2M relations should receive the CAPS fix
        caps_args = options.get("fix_caps") or []
        self.caps_models = []
        if "all" in caps_args:
            self.caps_models = ["actors", "directors", "studios"]
        else:
            self.caps_models = caps_args

        self.stdout.write(self.style.WARNING("=== Starting Cleanup ==="))
        if self.dry_run:
            self.stdout.write(
                self.style.NOTICE("DRY RUN MODE: No database changes will be made.\n")
            )
        else:
            self.stdout.write(self.style.ERROR("DANGER: Database will be modified!\n"))

        # Configuration: (Model Class, ManyToMany Field Name on Movie Model)
        models_config = [
            (Actor, "actors"),
            (Director, "directors"),
            (Studio, "studios"),
        ]

        # 1. Clean up comma separated entries AND (optionally) all-caps entries
        for model, m2m_field_name in models_config:
            self.stdout.write(
                self.style.SUCCESS(
                    f"--- Processing {model.__name__} (M2M: {m2m_field_name}) ---"
                )
            )

            # Check if this specific model should get the caps fix
            apply_caps = m2m_field_name in self.caps_models

            self.clean_comma_separated(model, m2m_field_name, apply_caps)

            if apply_caps:
                self.fix_all_caps(model, m2m_field_name)

        # 2. Check for potentially split names (e.g. "Emma", "Whatson")
        self.stdout.write(
            self.style.SUCCESS("--- Checking for split names in Movies ---")
        )
        self.find_split_names()

        # 3. Fuzzy matching for typos
        if self.run_fuzzy:
            self.stdout.write(self.style.SUCCESS("--- Running Fuzzy Matching ---"))
            self.find_similar_names(Actor)

        self.stdout.write(self.style.SUCCESS("\n=== Cleanup Script Finished ==="))

    @transaction.atomic
    def clean_comma_separated(self, model_class, m2m_field_name, apply_caps):
        bad_entries = model_class.objects.filter(name__contains=",")
        is_person = m2m_field_name in ("actors", "directors")

        for entry in bad_entries:
            parts = [
                " ".join(p.split())
                for p in entry.name.split(",")
                if " ".join(p.split())
            ]
            cleaned_names = []

            if is_person and len(parts) > 1:
                i = 0
                while i < len(parts):
                    current_part = parts[i]

                    if i + 1 < len(parts):
                        next_part = parts[i + 1]
                        combo_first_last = f"{next_part} {current_part}"
                        combo_last_first = f"{current_part} {next_part}"

                        if model_class.objects.filter(name=combo_first_last).exists():
                            cleaned_names.append(combo_first_last)
                            i += 2
                            continue

                        elif model_class.objects.filter(name=combo_last_first).exists():
                            cleaned_names.append(combo_last_first)
                            i += 2
                            continue

                        if " " not in current_part or " " not in next_part:
                            cleaned_names.append(combo_first_last)
                            i += 2
                            continue

                    cleaned_names.append(current_part)
                    i += 1
            else:
                cleaned_names = parts

            if apply_caps:
                cleaned_names = [n.title() if n.isupper() else n for n in cleaned_names]

            self.stdout.write(f"[CLEAN] '{entry.name}' -> {cleaned_names}")

            if not self.dry_run:
                self.replace_entity(entry, cleaned_names, model_class, m2m_field_name)

    @transaction.atomic
    def fix_all_caps(self, model_class, m2m_field_name):
        """
        Finds and fixes entries that don't have a comma, but are entirely uppercase.
        """
        all_entries = model_class.objects.exclude(name__contains=",")
        for entry in all_entries:
            if entry.name.isupper() and any(c.isalpha() for c in entry.name):
                new_name = entry.name.title()
                self.stdout.write(f"[CAPS FIX] '{entry.name}' -> '{new_name}'")
                if not self.dry_run:
                    self.replace_entity(entry, [new_name], model_class, m2m_field_name)

    def replace_entity(self, old_entry, new_name_list, model_class, m2m_field_name):
        new_entities = []
        for name in new_name_list:
            new_entity, created = model_class.objects.get_or_create(name=name)
            new_entities.append(new_entity)

        related_movies = getattr(old_entry, "movies").all()

        for movie in related_movies:
            m2m_manager = getattr(movie, m2m_field_name)
            m2m_manager.add(*new_entities)
            m2m_manager.remove(old_entry)

        old_entry.delete()

    def find_split_names(self):
        # 1. Clean whitespace and non-breaking spaces (\xa0) for all actors
        for actor in Actor.objects.all():
            normalized_name = " ".join(actor.name.split())
            if normalized_name != actor.name:
                self.stdout.write(f"[SPACE FIX] '{actor.name}' -> '{normalized_name}'")
                if not self.dry_run:
                    existing, created = Actor.objects.get_or_create(
                        name=normalized_name
                    )
                    if existing != actor:
                        for movie in actor.movies.all():
                            movie.actors.add(existing)
                            movie.actors.remove(actor)
                        actor.delete()
                    else:
                        actor.name = normalized_name
                        actor.save()

        # 2. Identify true single-word actors using Python's split() to accurately catch unicode whitespace
        single_word_actor_ids = [
            actor.id for actor in Actor.objects.all() if len(actor.name.split()) == 1
        ]

        for movie in Movie.objects.filter(
            actors__id__in=single_word_actor_ids
        ).distinct():
            # Retrieve single-word actor instances ordered by creation ID
            split_actors = list(
                movie.actors.filter(id__in=single_word_actor_ids).order_by("id")
            )

            # Recombine pairwise when an even count of single-word actors is detected
            if len(split_actors) > 1 and len(split_actors) % 2 == 0:
                i = 0
                while i < len(split_actors):
                    actor1 = split_actors[i]
                    actor2 = split_actors[i + 1]

                    # Normalize names in memory to ensure clean formatting during dry-run mode
                    name1 = " ".join(actor1.name.split())
                    name2 = " ".join(actor2.name.split())

                    # Reconstruct: Amazon format was "Lastname, Firstname" -> convert to "Firstname Lastname"
                    combined_name = f"{name2} {name1}"

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[FIX SPLIT] Movie '{movie.title_clean}': '{name1}' + '{name2}' -> '{combined_name}'"
                        )
                    )

                    if not self.dry_run:
                        new_actor, _ = Actor.objects.get_or_create(name=combined_name)
                        movie.actors.add(new_actor)
                        movie.actors.remove(actor1, actor2)

                        # Remove orphaned actor entries from the database
                        if not actor1.movies.exists():
                            actor1.delete()
                        if not actor2.movies.exists():
                            actor2.delete()

                    i += 2

    def find_similar_names(self, model_class):
        all_names = list(model_class.objects.values_list("name", flat=True))
        checked = set()

        for name in all_names:
            checked.add(name)
            matches = difflib.get_close_matches(name, all_names, n=3, cutoff=0.9)
            valid_matches = [m for m in matches if m != name and m not in checked]

            if valid_matches:
                self.stdout.write(
                    self.style.WARNING(
                        f"[TYPO CANDIDATES LOG] '{name}' is very similar to: {valid_matches}"
                    )
                )
