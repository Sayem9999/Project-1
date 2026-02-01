import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Heart, User, Plus } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <nav data-testid="main-navbar" className="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" data-testid="logo-link" className="flex items-center space-x-2">
            <div className="text-2xl font-bold text-blue-600">Nilam</div>
          </Link>

          {/* Search Bar */}
          <div className="hidden md:flex flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                data-testid="search-input"
                type="text"
                placeholder="Search for anything..."
                className="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-800 border-transparent focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 rounded-lg transition-all"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/create-listing">
                  <Button data-testid="create-listing-btn" className="bg-blue-600 hover:bg-blue-700 text-white rounded-full px-6 py-2 font-semibold shadow-md transition-all flex items-center space-x-2">
                    <Plus className="w-5 h-5" />
                    <span className="hidden sm:inline">List Item</span>
                  </Button>
                </Link>
                <Link to="/dashboard" data-testid="dashboard-link">
                  <Button variant="ghost" size="icon">
                    <Heart className="w-5 h-5" />
                  </Button>
                </Link>
                <Link to="/profile" data-testid="profile-link">
                  <Button variant="ghost" size="icon">
                    <User className="w-5 h-5" />
                  </Button>
                </Link>
                <Button data-testid="logout-btn" onClick={logout} variant="outline" className="btn-secondary">
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button data-testid="login-btn" variant="outline" className="border-2 border-slate-300 text-slate-900 hover:bg-slate-50 rounded-full px-6 py-2 font-medium">
                    Login
                  </Button>
                </Link>
                <Link to="/register">
                  <Button data-testid="register-btn" className="bg-blue-600 hover:bg-blue-700 text-white rounded-full px-6 py-2 font-semibold shadow-md">
                    Sign Up
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}