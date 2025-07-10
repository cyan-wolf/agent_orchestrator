import './App.css';

import {
  Routes,
  Route,
  Link
} from "react-router-dom";

import Home from './pages/home/Home';
import About from './pages/about/About';
import Login from './pages/login/Login';
import ProtectedRoute from './auth/ProtectedRoute';
import Logout from './pages/logout/Logout';

export default function App() {
  return (
    <div>
      <nav>
        <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/about">About</Link>
          </li>
          <li>
            <Link to="/login">Login</Link>
          </li>
          <li>
            <Link to="/logout">Logout</Link>
          </li>
        </ul>
      </nav>
      
      <Routes>
        <Route path="/about" element={<ProtectedRoute children={<About/>} />} />
        <Route path="/login" element={<Login/>} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/" element={<Home/>} />
      </Routes>
    </div>
  );
}
