from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.cache import cache
from .models import Book
import requests
from urllib.parse import quote
from .models import Book, Category
from django.core.paginator import Paginator

session = requests.Session()


def build_openlibrary_image(cover_id):
    if cover_id:
        return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
    return "/static/images/nocover.png"


def fetch_books(query, limit=5):
    if not query:
        return []

    cache_key = f"openlibrary_{query}_{limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    if limit>20:
        limit=20;

    url = f"https://openlibrary.org/search.json?q={quote(query)}&limit={limit}"

    try:
        res = session.get(url, timeout=10)
        data = res.json()
    except:
        return []

    books = []

    for item in data.get("docs", []):
        books.append({
            "id": None,
            "isbn": item.get("isbn", [None])[0] if item.get("isbn") else None,
            "title": item.get("title", "No title"),
            "author": ", ".join(item.get("author_name", [])) or "Unknown",
            "category": query,
            "available": True,
            "image": build_openlibrary_image(item.get("cover_i")),
            "is_local": False
        })

    cache.set(cache_key, books, 60 * 60 * 6)
    return books



class BookList(View):
    def get(self, request):

        category_slug = request.GET.get("category", "").strip()

        category_map = {
            "romance": ["romance"],
            "thriller-horror": ["thriller", "horror"],
            "scifi-fantasy": ["science fiction", "fantasy"],
            "business": ["business"],
            "history": ["history"],
            "manga": ["manga"],
            "poetry": ["poetry"],
        }

        # ✅ LOCAL BOOKS
        if category_slug:
            local_books = Book.objects.filter(category__slug=category_slug)
        else:
            local_books = Book.objects.all()

        local_data = [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "image": b.image.url if b.image else "",
                "is_local": True,
                "isbn": None,
                "category": b.category.name if b.category else "Unknown"
    
            }
            for b in local_books
        ]

        # ✅ EXTERNAL BOOKS
        external_data = []

        if category_slug in category_map:
            queries = category_map[category_slug]
        else:
            queries = ["fiction", "romance", "fantasy"]

        for q in queries:
            external_data.extend(fetch_books(q, limit=10))

        # remove duplicates
        seen = set()
        unique_books = []

        for b in external_data:
            key = b.get("isbn") or b.get("title")
            if key not in seen:
                seen.add(key)
                unique_books.append(b)

        # ✅ COMBINE ALL BOOKS
        all_books = local_data + unique_books

        # 🔥 PAGINATION ADDED HERE
        paginator = Paginator(all_books, 9)  # 9 books per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        categories = Category.objects.all()

        return render(request, "products/book_list.html", {
            "books": page_obj,   # 👈 IMPORTANT CHANGE
            "page_obj": page_obj,
            "selected_category": category_slug,
            "categories": categories
        })
    # -------------------------
# LOCAL BOOK DETAIL
# -------------------------
class BookDetail(View):
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)

        return render(request, "products/book_detail.html", {
            "book": {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": getattr(book, "description", ""),
                "image": book.image.url if book.image else "",
                "is_local": True
            }
        })


# -------------------------
# EXTERNAL BOOK DETAIL
# -------------------------
class ExternalBookDetail(View):
    def get(self, request, isbn):

        if not isbn:
            return render(request, "products/external_detail.html", {"book": None})

        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"

        try:
            res = session.get(url, timeout=10)
            data = res.json()
        except:
            data = {}

        book_data = data.get(f"ISBN:{isbn}")

        if not book_data:
            return render(request, "products/external_detail.html", {"book": None})

        book = {
            "title": book_data.get("title", "No title"),
            "author": ", ".join([a["name"] for a in book_data.get("authors", [])]) if book_data.get("authors") else "Unknown",
            "description": book_data.get("notes", "No description"),
            "image": book_data.get("cover", {}).get("medium", ""),
            "isbn": isbn
        }

        return render(request, "products/external_detail.html", {
            "book": book
        })


# -------------------------
# SEARCH
# -------------------------
def search_books(request):
    query = request.GET.get("q", "").strip()

    local_books = Book.objects.filter(title__icontains=query) if query else []

    local_data = [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "image": b.image.url if b.image else "",
            "is_local": True,
            "isbn": None
        }
        for b in local_books
    ]

    external_data = fetch_books(query, limit=6) if query else []

    return render(request, "products/search_results.html", {
        "books": local_data + external_data,
        "query": query
    })