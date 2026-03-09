import React, { useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import PoemDetail from './components/PoemDetail';
import Category from './components/Category';
import Dashboard from './components/Dashboard';
import AddPoem from './components/AddPoem';
import EditProfile from './components/EditProfile';
import Profile from './components/Profile';
import axios from 'axios';

function App() {
  const handleLogout = () => {
    axios.post('http://localhost:5000/api/logout', {}, { withCredentials: true })
      .then(() => window.location.href = '/')
      .catch(err => console.error(err));
  };
  return (
    <Router>
      <nav>
        <Link to="/">Home</Link> | <Link to="/dashboard">Dashboard</Link> | <Link to="/add-poem">Add Poem</Link> | <Link to="/edit-profile">Edit Profile</Link> | <Link to="/profile">My Profile</Link> | <Link to="/login">Login</Link> | <Link to="/register">Register</Link> | <button onClick={handleLogout}>Logout</button>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/add-poem" element={<AddPoem />} />
        <Route path="/edit-profile" element={<EditProfile />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/poem/:id" element={<PoemDetail />} />
        <Route path="/category/:name" element={<Category />} />
      </Routes>
    </Router>
  );
}

export default App;
