import './App.css';

import {
  Routes,
  Route,
} from "react-router-dom";

import Home from './pages/home/Home';
import Settings from './pages/settings/Settings';
import Login from './pages/login/Login';
import ProtectedRoute from './auth/ProtectedRoute';
import Logout from './pages/logout/Logout';
import Chat from './pages/chat/Chat';
import NavBar from './components/nav/NavBar';

export default function App() {
  return (
    <div>
      <nav>
        <NavBar pages={[
          { to: "/", title: "Home" },
          { to: "/chat", title: "Chat" },
          { to: "/settings", title: "Settings" },
          { to: "/login", title: "Login" },
          { to: "/logout", title: "Logout" },
        ]} />
      </nav>
      
      <Routes>
        <Route path="/chat" element={<ProtectedRoute children={<Chat/>} />} />
        <Route path="/settings" element={<ProtectedRoute children={<Settings/>} />} />

        <Route path="/login" element={<Login/>} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/" element={<Home/>} />
      </Routes>
    </div>
  );
}
