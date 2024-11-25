import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

const CategoryBooksPage = () => {
  const { category } = useParams(); // Get the category from the URL
  const [books, setBooks] = useState([]); // State to store books
  const [selectedBook, setSelectedBook] = useState(null); // State for selected book details
  const [error, setError] = useState(""); // State to handle errors
  const [loading, setLoading] = useState(true); // State to handle loading
  const [detailsLoading, setDetailsLoading] = useState(false); // State for loading book details
  const [username, setUsername] = useState(""); // State for username
  const navigate = useNavigate(); // To navigate on logout

  // Fetch username from localStorage on component mount
  useEffect(() => {
    const storedUsername = localStorage.getItem("username");
    if (storedUsername) {
      setUsername(storedUsername);
    } else {
      // If no username, redirect to login page
      navigate("/signin");
    }
  }, [navigate]);

  // Fetch books for the category when the component mounts
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          `http://localhost:8000/api/categories/${category.toUpperCase()}/books`
        );
        console.log("API Response:", response.data);

        if (Array.isArray(response.data)) {
          setBooks(response.data); // Assuming `response.data` is an array of books
        } else {
          throw new Error("Invalid data format received from the server.");
        }
      } catch (err) {
        console.error("Error fetching books:", err.response || err);
        const errorMessage =
          err.response?.data?.detail || err.response?.data?.msg || "Failed to load books.";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchBooks();
  }, [category]);

  // Fetch details of a selected book
  const fetchBookDetails = async (bookId) => {
    try {
      setDetailsLoading(true);
      const response = await axios.get(`http://localhost:8000/api/bookstore/books/${bookId}`);
      console.log("Book Details:", response.data);

      if (response.data?.data) {
        setSelectedBook(response.data.data);
      } else {
        throw new Error("Invalid book details received from the server.");
      }
    } catch (err) {
      console.error("Error fetching book details:", err.response || err);
      const errorMessage =
        err.response?.data?.detail || err.response?.data?.msg || "Failed to load book details.";
      setError(errorMessage);
    } finally {
      setDetailsLoading(false);
    }
  };

  // Logout function
  const handleLogout = () => {
    localStorage.removeItem("authToken"); // Remove auth token
    localStorage.removeItem("username"); // Remove username
    navigate("/signin"); // Redirect to login page
  };

  return (
    <div>
      <header className="bg-gray-800 text-white p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">{category} Books</h1>
        <div className="flex items-center space-x-4">
          {username && <p>Welcome, {username}</p>}
          <button
            onClick={handleLogout}
            className="bg-red-500 px-4 py-2 rounded text-white hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      </header>
      <main className="p-4">
        {loading && <p>Loading books...</p>}
        {error && <p className="text-red-500">{error}</p>}

        {books.length > 0 ? (
          <ul className="list-disc pl-5">
            {books.map((book) => (
              <li
                key={book.id}
                className="mb-2 cursor-pointer text-blue-500 hover:underline"
                onClick={() => fetchBookDetails(book.id)} // Fetch book details on click
              >
                <span className="font-bold">{book.title}</span> by {book.author}
              </li>
            ))}
          </ul>
        ) : (
          !loading && !error && <p>No books available for this category.</p>
        )}

        {/* Show book details in a table if a book is selected */}
        {selectedBook && !detailsLoading && (
          <div className="mt-8">
            <h2 className="text-xl font-bold mb-4">Book Details</h2>
            <table className="table-auto border-collapse border border-gray-400 w-full">
              <tbody>
                <tr>
                  <td className="border px-4 py-2 font-bold">Title</td>
                  <td className="border px-4 py-2">{selectedBook.title}</td>
                </tr>
                <tr>
                  <td className="border px-4 py-2 font-bold">Author</td>
                  <td className="border px-4 py-2">{selectedBook.author}</td>
                </tr>
                <tr>
                  <td className="border px-4 py-2 font-bold">Price</td>
                  <td className="border px-4 py-2">${selectedBook.price}</td>
                </tr>
                <tr>
                  <td className="border px-4 py-2 font-bold">Total Count</td>
                  <td className="border px-4 py-2">{selectedBook.totalCount}</td>
                </tr>
                <tr>
                  <td className="border px-4 py-2 font-bold">Sold</td>
                  <td className="border px-4 py-2">{selectedBook.sold}</td>
                </tr>
                <tr>
                  <td className="border px-4 py-2 font-bold">Reviews</td>
                  <td className="border px-4 py-2">
                    {selectedBook.reviews?.length > 0 ? (
                      <ul>
                        {selectedBook.reviews.map((review, index) => (
                          <li key={index}>
                            <span className="font-bold">Rating:</span> {review.rating},{" "}
                            <span className="font-bold">Comment:</span> {review.comment || "No comment"}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      "No reviews available"
                    )}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}

        {detailsLoading && <p>Loading book details...</p>}
      </main>
    </div>
  );
};

export default CategoryBooksPage;