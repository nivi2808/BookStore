import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const SignIn = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [showWelcome, setShowWelcome] = useState(false); // State for popup window
  const [username, setUsername] = useState(""); // State to hold username
  const navigate = useNavigate();

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
      const name = response.data.user.name; // Ensure your API provides the username

      // Store token and username in localStorage
      localStorage.setItem("authToken", token);
      localStorage.setItem("username", name);

      // Update username in the state
      setUsername(name);

      // Show the welcome popup
      setShowWelcome(true);

      // Automatically close the popup and navigate to the categories page after 3 seconds
      setTimeout(() => {
        setShowWelcome(false);
        navigate("/categories");
      }, 3000);
    } catch (err) {
      console.error("Error during login:", err);
      setError(err.response?.data?.message || "Invalid email or password.");
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-8 rounded shadow">
      {showWelcome && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 rounded shadow text-center">
            <h2 className="text-2xl font-bold mb-4">Welcome, {username}!</h2>
            <p className="text-gray-700">You have successfully logged in. </p>
          </div>
        </div>
      )}

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
    </div>
  );
};

export default SignIn;