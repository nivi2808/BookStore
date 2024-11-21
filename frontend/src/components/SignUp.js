import React, { useState } from 'react';
// import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const SignUp = () => {
  // State variables to hold form data
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });

  // State variables for handling errors and registration status
  const [error, setError] = useState('');
  const [isRegistered, setIsRegistered] = useState(false);
  const [userName, setUserName] = useState('');

  // const navigate = useNavigate();

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
      console.log('Sending sign-up request with data:', formData);

      const response = await axios.post(
        'http://127.0.0.1:8000/api/auth/signup',
        formData
      );

      // Handle successful sign-up
      setIsRegistered(true);
      setUserName(formData.name);


      // navigate('/signin'); // Replace with your desired route
    } catch (err) {
      // Handle errors
      if (err.response && err.response.data) {
        setError(err.response.data.message || 'An error occurred during sign-up.');
      } else {
        setError('An error occurred. Please try again.');
      }
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-8 rounded shadow">
      {isRegistered ? (
        // Success Message
        <h2 className="text-2xl font-bold mb-6 text-center">
          {userName} registered successfully! Welcome to Bookstore.
        </h2>
      ) : (
        // Sign-Up Form
        <>
          <h2 className="text-2xl font-bold mb-6 text-center">Sign Up</h2>

          {error && <p className="mb-4 text-red-500">{error}</p>}

          <form onSubmit={handleSubmit}>
            {/* Name Field */}
            <div className="mb-4">
              <label className="block text-gray-700">Name</label>
              <input
                type="text"
                name="name"
                className="w-full mt-2 p-2 border rounded"
                placeholder="Enter your name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

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
              Sign Up
            </button>
          </form>
        </>
      )}
    </div>
  );
};

export default SignUp;