import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import SignIn from "./components/SignIn";
import SignUp from './components/SignUp';


function App() {
  return (
      <Router>
        <Routes>
          <Route path = "/" element={<HomePage />} />
           <Route path= "/SignIn" element={<SignIn />} />
            <Route path= "/SignUp" element={<SignUp />} />
        </Routes>
      </Router>

  );
}

export default App;
