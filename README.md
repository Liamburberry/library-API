

# library-API
A simple Rest-API for a small library

Installation:

1. Install Unvicorn:
    - pip install fastapi uvicorn
 
2. Run the application:
    - uvicorn main:app --reload
    - API is available at: http://localhost:8000
 
Use:

Option 1. Swagger:
    - URL: http://localhost:8000/docs
    - 1. Start the server: uvicorn main:app --reload
    - 2. Open http://localhost:8000/docs in your browser
    - 3. Click on any endpoint to expand it
    - 4. Click "Try it out" button
    - 5. Fill in the required parameters
    - 6. Click "Execute" to test the API
    
Option 2. Terminal using Curl:
    - URL: http://localhost:8000
    - Example of use: 
        - List books: curl -X GET "http://localhost:8000/v1/books"
        - Rent book: curl -X POST "http://localhost:8000/v1/books/{book_name}/rent?user_id={user_id}"
        - Return book: curl -X POST "http://localhost:8000/v1/rentals/{rental_id}/return?user_id={user_id}"
        - List users loaned books: curl -X GET "http://localhost:8000/v1/users/{user_id}/books"
        - Display book details: "http://localhost:8000/v1/books/{book_id}"
