import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import SignIn from "./components/SignIn";
import SignUp from './components/SignUp';
import CategoriesPage from "./components/CategoriesPage";
import CategoryBooksPage from "./components/CategoryBooksPage";


function App() {
  return (
      <Router>
        <Routes>
          <Route path = "/" element={<HomePage />} />
           <Route path= "/SignIn" element={<SignIn />} />
            <Route path= "/SignUp" element={<SignUp />} />
            <Route path="/categories" element={<CategoriesPage />} />
             <Route path="/category/:category" element={<CategoryBooksPage />} />
        </Routes>
      </Router>

  );
}

export default App;
