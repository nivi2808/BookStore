import React from "react";
import { useParams } from "react-router-dom";

const CategoryBooksPage = () => {
  const { category } = useParams(); // Get the category from the URL

  return (
    <div>
      <header className="bg-gray-800 text-white p-4">
        <h1 className="text-center text-2xl font-bold">{category} Books</h1>
      </header>
      <main className="p-4">
        <p>Displaying books for the "{category}" category.</p>
        {/* You can fetch and display the books for this category here */}
      </main>
    </div>
  );
};

export default CategoryBooksPage;