import uuid
import json
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime

# ============================================================================
# Book Rental API
# This API allows users to rent books, view book details, and manage rentals.
# It supports operations such as listing books, renting a book, returning a book,
# and viewing a user's rented books.
# ============================================================================

# Define the Book model using Pydantic library
# This model represents the structure of a book in the system.
class Book(BaseModel):
    isbn: str
    title: str
    author: str
    published_year: int = None
    total_copies: int = 0
    available_copies: int = 0
    description: str = None

# Initialize global dictionaries to store books and rentals
# These will be populated from a JSON file at startup.
books: dict[str, dict] = {}
rentals: dict[str, dict] = {}

# Load books from a JSON file
# This function reads the books from a JSON file and populates the global `books` dictionary
# It also ensures that each book has an `available_copies` field initialized.
def load():
    global books
    try:
        with open("books.json", "r") as file:
            data = json.load(file)
            books = {book["isbn"]: book for book in data.get("books", [])}
            
            for book in books.values():
                if "available_copies" not in book:
                    book["available_copies"] = book["totalCopies"]

    except Exception as e:
        print(f"Error loading books: {e}")
        books = {}

load()
app = FastAPI()

# ============================================================================
# First route: List all books
# This endpoint returns a list of all books in the system.
# It retrieves the books from the global `books` dictionary and returns them in a JSON format
@app.get("/v1/books")
def list_books():
    return {"books": list(books.values())}

# ============================================================================
# Second route: Display book details
# This endpoint retrieves the details of a specific book by its ID (ISBN).
# It checks if the book exists in the global `books` dictionary and returns its details.
# If the book is not found, it returns a 404 error with an appropriate message.
@app.get("/v1/books/{book_id}")
def display_details(book_id: str):
    book = books.get(book_id)
    if book:
        return {"book": book}
    raise HTTPException(status_code=404, detail="Book was not found")

# ============================================================================
# Third route: Rent a book
# This endpoint allows a user to rent a book by providing the book ID and user ID.
# It checks if the book exists and if there are available copies.
@app.post("/v1/books/{book_id}/rent")
def rent_book(book_id: str, user_id: str):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book was not found")
    
    book = books.get(book_id)
    if book["available_copies"] <= 0:
        raise HTTPException(status_code=400, detail="There are no copies of this book available for rent")
    
    user_has_book = any(
        rental["user_id"] == user_id and 
        rental["book_id"] == book_id and 
        rental["returned_at"] is None
        for rental in rentals.values()
    )

    if user_has_book:
        raise HTTPException(status_code=400, detail="Book already rented by this user")
    
    rental_id = str(uuid.uuid4())
    rentals[rental_id] = {
        "user_id": user_id,
        "book_id": book_id,
        "rented_at": datetime.now().isoformat(),
        "returned_at": None
    }
    book["available_copies"] -= 1

    return {
        "message": "Book rented successfully", 
        "rental_id": rental_id,  # Return the rental ID!
        "book": book
    }

# ============================================================================
# Fourth route: List books rented by a user
# This endpoint retrieves all books currently rented by a specific user.
# It checks the global "rentals" dictionary for ongoing rentals of the user
@app.get("/v1/users/{user_id}/books")
def list_user_books(user_id: str):
    user_rentals = [
        rental for rental in rentals.values()
        if rental["user_id"] == user_id and rental["returned_at"] is None
    ]

    user_books = []
    for rental in user_rentals:
        book_id = rental["book_id"]
        if book_id in books:
            book_info = books[book_id].copy()
            book_info["rental_id"] = rental["rental_id"] if "rental_id" in rental else None
            book_info["rented_at"] = rental["rented_at"]
            user_books.append(book_info)
    
    return {"books": user_books}

# ============================================================================
# Fifth route: Return a rented book
# This endpoint allows a user to return a book they have rented.
# It checks if the rental exists, verifies ownership, and updates the book's available copies.
@app.post("/v1/rentals/{rental_id}/return")
def return_book(rental_id: str, user_id: str):
    if rental_id not in rentals:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    rental = rentals[rental_id]
    
    if rental["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: This rental belongs to another user")
    
    if rental["returned_at"] is not None:
        raise HTTPException(status_code=400, detail="Book already returned")
    
    book_id = rental["book_id"]
    book = books.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    rental["returned_at"] = datetime.now().isoformat()
    book["available_copies"] += 1

    return {
        "message": "Book returned successfully", 
        "rental_id": rental_id,
        "book": book
    }