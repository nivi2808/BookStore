import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const SignIn = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [userName, setUserName] = useState("");
  const navigate = useNavigate();

  // Check if the user is already logged in (on component mount)
  useEffect(() => {
    const storedUserName = localStorage.getItem("username");
    if (storedUserName) {
      setUserName(storedUserName);
    }
  }, []);

  // Handle input changes
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await axios.post("http://localhost:8000/api/auth/signin", formData);

      // Extract the token and user name from the response
      const token = response.data.token;
      const name = response.data.user.name;

      // Store token and username in localStorage
      localStorage.setItem("authToken", token);
      localStorage.setItem("username", name);
      console.log("Stored username:", localStorage.getItem("username"));

      // Update username in the state
      setUserName(name);

      // Navigate to the categories page
      navigate("/categories");
    } catch (err) {
      console.error("Error during login:", err);
      setError(err.response?.data?.message || "Invalid email or password.");
    }
  };

  // Handle "Book" button click
  const book = () => {
    navigate("/categories");
  };

  // Handle logout
  const handleLogout = () => {
    setUserName("");
    localStorage.removeItem("authToken");
    localStorage.removeItem("username");
    navigate("/signin");
  };

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-8 rounded shadow">
      {userName ? (
        <>
          <h2 className="text-2xl font-bold mb-6 text-center">Welcome, {userName}!</h2>

          <button
            onClick={book}
            className="mt-1 w-full bg-red-500 text-white py-2 rounded hover:bg-red-600"
          >
            Book
          </button>
          <button
            onClick={handleLogout}
            className="mt-4 w-full bg-gray-500 text-white py-2 rounded hover:bg-gray-600"
          >
            Log Out
          </button>
        </>
      ) : (
        <>
          <h2 className="text-2xl font-bold mb-6 text-center">Log In</h2>

          {error && <p className="mb-4 text-red-500">{error}</p>}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-gray-700">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-3 py-2 border rounded"
                required
              />
            </div>
            <div className="mb-6">
              <label className="block text-gray-700">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-3 py-2 border rounded"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
            >
              Log In
            </button>
          </form>
        </>
      )}
    </div>
  );
};

export default SignIn;