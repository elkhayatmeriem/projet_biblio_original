from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.cache import cache
from .models import Book
import requests
from urllib.parse import quote
from .models import Book, Category
from django.core.paginator import Paginator

session = requests.Session()


session = requests.Session()


def build_openlibrary_image(cover_id):
    if cover_id:
        return f"https://covers.openlibrary.org/b/id/{cover_id}-S.jpg"
    return "/static/images/no_cover.png"

def fetch_books(query, limit=5):
    if not query:
        return []

    cache_key = f"openlibrary_{query}_{limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    limit = min(limit, 20)

    url = f"https://openlibrary.org/search.json?q={quote(query)}&limit={limit}"

    try:
        res = session.get(url, timeout=10)
        data = res.json()
    except:
        return []

    books = []

    for item in data.get("docs", []):

        title = item.get("title") or "No title"

        authors = item.get("author_name") or []
        author = ", ".join(authors) if authors else "Unknown"

        cover_id = item.get("cover_i")

        if cover_id:
            image = f"https://covers.openlibrary.org/b/id/{cover_id}-S.jpg"
        else:
            image = "/static/images/no_cover.png"

        isbn = item.get("isbn", [None])[0] if item.get("isbn") else None

        books.append({
            "id": None,
            "isbn": isbn,
            "title": title,
            "author": author,
            "image": image,
            "category": item.get("subject", ["Unknown"])[0] if item.get("subject") else "Unknown",
            "is_local": False,
        })

    cache.set(cache_key, books, 60 * 60 * 6)
    return books

class BookList(View):
    def get(self, request):

        category_slug = request.GET.get("category") or "all"
        page_number = request.GET.get("page", 1)

        # -------------------------
        # LOCAL BOOKS
        # -------------------------
        if category_slug == "all":
            local_queryset = Book.objects.select_related("category").all()
        else:
            local_queryset = Book.objects.select_related("category").filter(
                category__slug=category_slug
            )

        # -------------------------
        # PAGINATION
        # -------------------------
        paginator = Paginator(local_queryset, 10)
        page_obj = paginator.get_page(page_number)

        # -------------------------
        # OPTIONAL: format local books (if needed in template)
        # -------------------------
        local_data = [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "image": b.image.url if b.image else "",
                "category": b.category.name if b.category else "No category",
                "is_local": True,
                "available": True
            }
            for b in page_obj
        ]

        # -------------------------
        # EXTERNAL BOOKS (ONLY ON ALL)
        # -------------------------
        external_data = []
        if category_slug == "all":
            external_data = fetch_books("bestsellers", limit=10)

        # -------------------------
        # CONTEXT
        # -------------------------
        return render(request, "products/book_list.html", {
            "books": page_obj,   # IMPORTANT: pagination object
            "page_obj": page_obj,
            "selected_category": category_slug,
            "categories": Category.objects.all(),
            "external_books": external_data
        })
    # -------------------------
# LOCAL BOOK DETAIL
# -------------------------
class BookDetail(View):
    def get(self, request, pk):

        # -------------------------
        # SAFE STATE (IMPORTANT)
        # -------------------------
        category = request.GET.get("category") or "all"
        category = category.strip()

        page = request.GET.get("page", 1)

        book = get_object_or_404(Book, pk=pk)

        return render(request, "products/book_detail.html", {
            "book": {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": getattr(book, "description", ""),
                "image": book.image.url if book.image else "",
                "is_local": True
            },
            "page": page,
            "category": category
        })

# -------------------------
# EXTERNAL BOOK DETAIL
# -------------------------
class ExternalBookDetail(View):
    def get(self, request, isbn):

        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"

        try:
            res = session.get(url, timeout=10)
            data = res.json()
        except:
            data = {}

        book_data = data.get(f"ISBN:{isbn}")

        # -------------------------
        # IF API WORKS
        # -------------------------
        if book_data:
            book = {
                "title": book_data.get("title", "No title"),
                "author": ", ".join(
                    [a.get("name", "") for a in book_data.get("authors", [])]
                ) or "Unknown",
                "image": book_data.get("cover", {}).get("medium", ""),
                "description": book_data.get("notes", "No description"),
            }

        # -------------------------
        # IF API FAILS
        # -------------------------
        else:
            book = {
                "title": "No title",
                "author": "Unknown",
                "image": "",
                "description": "No description available",
            }

        return render(request, "products/book_detail.html", {
            "book": book
        })


# -------------------------
# SEARCH
# -------------------------
def search_books(request):
    query = request.GET.get("q", "").strip()

    # -------------------------
    # LOCAL BOOKS
    # -------------------------
    local_books = Book.objects.filter(title__icontains=query) if query else []

    local_data = [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "image": b.image.url if b.image else "",
            "is_local": True,
            "isbn": b.isbn
        }
        for b in local_books
    ]

    # -------------------------
    # EXTERNAL BOOKS
    # -------------------------
    external_books = fetch_books(query, limit=10) if query else []

    saved_external = []

    for b in external_books:

        # 🔥 NORMALIZE DATA
        raw_title = b.get("title", "")
        raw_author = b.get("author", "")

        title = raw_title.strip()
        author = raw_author.strip()

        title_normalized = title.lower()
        author_normalized = author.lower()

        # 🔥 CLEAN ISBN
        isbn = b.get("isbn")
        if not isbn or str(isbn).strip() == "":
            isbn = None

        book_obj = None

        # -------------------------
        # PRIORITY 1: ISBN MATCH
        # -------------------------
        if isbn:
            book_obj = Book.objects.filter(isbn=isbn).first()

        # -------------------------
        # PRIORITY 2: TITLE + AUTHOR MATCH
        # -------------------------
        if not book_obj:
            book_obj = Book.objects.filter(
                title__iexact=title_normalized,
                author__iexact=author_normalized
            ).first()

        # -------------------------
        # CREATE IF NOT EXISTS
        # -------------------------
        if not book_obj:
            book_obj = Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                image_url=b.get("image"),
                available=True
            )

        # -------------------------
        # PREVENT DUPLICATES IN UI
        # -------------------------
        if any(x["id"] == book_obj.id for x in local_data):
            continue

        # -------------------------
        # ADD TO RESULTS
        # -------------------------
        saved_external.append({
            "id": book_obj.id,
            "title": book_obj.title,
            "author": book_obj.author,
            "image": b.get("image", ""),
            "is_local": False,
            "isbn": isbn
        })

    # -------------------------
    # FINAL RESPONSE
    # -------------------------
    return render(request, "products/search_results.html", {
        "books": local_data + saved_external,
        "query": query
    })

def save(self, *args, **kwargs):
    if self.isbn == "":
        self.isbn = None
    super().save(*args, **kwargs)

