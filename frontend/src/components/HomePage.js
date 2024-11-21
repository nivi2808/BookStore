import React from 'react';
import { Link } from 'react-router-dom'
const HomePage = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
            {/* Header Section */}
            <header className="w-full bg-blue-600 text-white py-6">
                <div className="container mx-auto flex justify-between items-center px-4">
                    <h1 className="text-3xl font-bold">Welcome to the Bookstore</h1>
                    <nav>
                        <Link to="/SignUp" className="mr-4 hover:underline">
                            SignUp
                        </Link>
                        <Link to="/SignIn" className="mr-4 hover:underline">
                            signIn
                        </Link>
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto flex-1 px-4 py-8 text-center">
                <h2 className="text-2xl font-semibold mb-4">Discover Your Next Great Read</h2>
                <p className="mb-6 text-gray-700">
                    Browse our extensive collection of books across various genres. Sign up to keep track of
                    your favorite books and authors.
                </p>

            </main>

            {/* Footer Section */}
            <footer className="w-full bg-gray-800 text-white py-4">
                <div className="container mx-auto text-center">
                    &copy; {new Date().getFullYear()} Bookstore. All rights reserved.
                </div>
            </footer>
        </div>
    );
};
export default HomePage;
