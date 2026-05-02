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
            "history",
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
            response = requests.get(url)

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed for {cat_name}"))
                continue

            data = response.json()

            created_count = 0

            for item in data.get("docs", []):

                title = item.get("title")
                authors = item.get("author_name", [])
                author = ", ".join(authors) if authors else "Unknown"

                isbn_list = item.get("isbn")

                # ⚠️ FIX: generate fallback ID if no ISBN
                isbn = isbn_list[0] if isbn_list else None

                if not title:
                    continue

                # better uniqueness check
                if Book.objects.filter(title=title, author=author).exists():
                    continue

                Book.objects.create(
                    title=title,
                    author=author,
                    isbn=isbn if isbn else "",
                    category=category,
                    available=True
                )

                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"{cat_name}: {created_count} books imported"
                )
            )