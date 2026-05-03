from django.core.management.base import BaseCommand
from products.models import Book, Category
import requests


class Command(BaseCommand):
    help = "Import books from Open Library API"

    def handle(self, *args, **kwargs):

        categories = [
            "fiction",
            "romance",
            "thriller",
            "fantasy",
            "historical fiction",
            "business",
            "science fiction",
            "poetry",
            "manga"
        ]

        for cat_name in categories:

            category_slug = cat_name.lower().replace(" ", "-")

            category, _ = Category.objects.get_or_create(
                slug=category_slug,
                defaults={"name": cat_name.title()}
            )

            url = f"https://openlibrary.org/search.json?q={cat_name}&limit=30"

            #  FIX 1: add timeout + error handling
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"{cat_name} failed: {e}"))
                continue

            data = response.json()

            created_count = 0

            for item in data.get("docs", []):

                title = item.get("title")
                if not title:
                    continue

                authors = item.get("author_name", [])
                author = ", ".join(authors) if authors else "Unknown"

                isbn_list = item.get("isbn")
                isbn = isbn_list[0] if isbn_list else None

                #  FIX 2: safer duplicate check
                if isbn:
                    if Book.objects.filter(isbn=isbn).exists():
                        continue
                else:
                    if Book.objects.filter(title=title, author=author).exists():
                        continue

                #  FIX 3: never pass empty string for ISBN
                Book.objects.create(
                    title=title,
                    author=author,
                    isbn=isbn,   # keep None if missing
                    category=category,
                    available=True
                )

                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"{cat_name}: {created_count} books imported"
                )
            )