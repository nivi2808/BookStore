import React, { useState } from 'react';
import axios from 'axios';
// import { useNavigate } from 'react-router-dom'; // Uncomment if you plan to navigate

const SignIn = () => {
  // State variables to hold form data and user name
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [error, setError] = useState('');
  const [userName, setUserName] = useState('');
  // const navigate = useNavigate(); // Uncomment if you plan to navigate

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
    setError('');

    try {
      console.log("Sending login request with email:", formData.email, "password:", formData.password);
      const response = await axios.post('http://127.0.0.1:8000/api/auth/signin', formData);

      // Extract the token and user information from the response
      const token = response.data.token;
      const name = response.data.user.name; // Get the user's name

      // Store the token (you can use localStorage or a context)
      localStorage.setItem('authToken', token);

      // Store the user's name in state
      setUserName(name);

      // Redirect to a protected route or display the welcome message
      // navigate('/dashboard'); // Uncomment if you have a dashboard route

    } catch (err) {
      // Handle errors
      if (err.response && err.response.data) {
        setError(err.response.data.message || 'Invalid email or password.');
      } else {
        setError('An error occurred. Please try again.');
      }
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-8 rounded shadow">
      {userName ? (
        // Display the welcome message if the user is logged in
        <h2 className="text-2xl font-bold mb-6 text-center">Welcome, {userName}!</h2>
      ) : (
        // Display the login form if the user is not logged in
        <>
          <h2 className="text-2xl font-bold mb-6 text-center">Log In</h2>

          {error && <p className="mb-4 text-red-500">{error}</p>}

          <form onSubmit={handleSubmit}>
            {/* Email Field */}
            <div className="mb-4">
              <label className="block text-gray-700">Email Address</label>
              <input
                type="email"
                name="email"
                className="w-full mt-2 p-2 border rounded"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            {/* Password Field */}
            <div className="mb-6">
              <label className="block text-gray-700">Password</label>
              <input
                type="password"
                name="password"
                className="w-full mt-2 p-2 border rounded"
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 transition duration-200"
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