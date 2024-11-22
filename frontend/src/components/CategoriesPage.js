import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";

const CategoriesPage = () => {
  const [categories, setCategories] = useState([]); // State to store categories
  const [error, setError] = useState(""); // State to handle errors
  const [username, setUsername] = useState(""); // State to store username
  const navigate = useNavigate();

  // Fetch categories from the backend
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        console.log("Fetching categories from API...");
        const response = await axios.get("http://localhost:8000/api/categories");
        console.log("API Response:", response.data);
        setCategories(response.data.data);
      } catch (err) {
        console.error("Error fetching categories:", err);
        setError("Failed to load categories. Please try again later.");
      }
    };

    fetchCategories();

    // Retrieve username from localStorage
    const storedUsername = localStorage.getItem("username");
    if (storedUsername) {
      setUsername(storedUsername);
    } else {
      console.warn("Username not found in localStorage.");
    }
  }, []);

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem("authToken"); // Remove auth token
    localStorage.removeItem("username"); // Remove username
    navigate("/"); // Redirect to HomePage page
  };

  return (
    <div>
      <header className="bg-gray-800 text-white p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">Book Categories</h1>
        <div className="flex items-center space-x-4">
          {username && <span className="text-blue-300">Welcome, {username}!</span>}
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white py-1 px-4 rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      </header>
      <nav className="mt-4 flex justify-center space-x-4">
        {categories.length > 0 ? (
          categories.map((category, index) => (
            <Link
              key={index}
              to={`/category/${category.toLowerCase()}`}
              className="text-blue-300 hover:underline"
            >
              {category}
            </Link>
          ))
        ) : (
          <p className="text-red-500">{error || "Loading categories..."}</p>
        )}
      </nav>
      <main className="p-4">
        <p>Select a category from the header to view books.</p>
      </main>
    </div>
  );
};

export default CategoriesPage;