import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Clock, TrendingUp, Sparkles } from 'lucide-react';
import api from '../lib/api';
import { formatCurrency, formatTimeRemaining } from '../lib/utils';
import { Button } from './ui/button';

const categories = [
  { name: 'Electronics', icon: '💻', color: 'bg-blue-100 text-blue-600' },
  { name: 'Fashion', icon: '👕', color: 'bg-pink-100 text-pink-600' },
  { name: 'Watches', icon: '⌚', color: 'bg-purple-100 text-purple-600' },
  { name: 'Collectibles', icon: '🎨', color: 'bg-orange-100 text-orange-600' },
];

export default function HomePage() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchListings();
  }, []);

  const fetchListings = async () => {
    try {
      const res = await api.getListings({ status: 'active' });
      setListings(res.data);
    } catch (error) {
      console.error('Error fetching listings:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid="home-page" className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-blue-50 to-white dark:from-slate-900 dark:to-slate-800 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 data-testid="hero-title" className="text-5xl sm:text-6xl lg:text-7xl font-bold text-slate-900 dark:text-white mb-6">
              Discover Unique Items
              <br />
              <span className="text-blue-600">Win Big Deals</span>
            </h1>
            <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto mb-8">
              Join thousands of buyers and sellers in the most exciting auction marketplace.
              Bid on rare finds or sell your treasures.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
              <Link to="/listings">
                <Button data-testid="browse-auctions-btn" className="btn-primary flex items-center space-x-2">
                  <Sparkles className="w-5 h-5" />
                  <span>Browse Auctions</span>
                </Button>
              </Link>
              <Link to="/create-listing">
                <Button data-testid="start-selling-btn" variant="outline" className="btn-secondary">
                  Start Selling
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Browse by Category</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {categories.map((cat) => (
            <Link
              key={cat.name}
              to={`/listings?category=${cat.name}`}
              data-testid={`category-${cat.name.toLowerCase()}`}
              className="card-auction p-6 text-center hover:scale-105 transition-transform"
            >
              <div className={`text-4xl mb-3 w-16 h-16 mx-auto rounded-full ${cat.color} flex items-center justify-center`}>
                {cat.icon}
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white">{cat.name}</h3>
            </Link>
          ))}
        </div>
      </section>

      {/* Trending Auctions */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <TrendingUp className="w-8 h-8 text-blue-600" />
            <span>Trending Auctions</span>
          </h2>
          <Link to="/listings">
            <Button data-testid="view-all-btn" variant="ghost" className="text-blue-600 hover:text-blue-700">
              View All →
            </Button>
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="card-auction p-4 animate-pulse">
                <div className="bg-slate-200 h-48 rounded-lg mb-4"></div>
                <div className="bg-slate-200 h-4 rounded mb-2"></div>
                <div className="bg-slate-200 h-4 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {listings.slice(0, 8).map((listing) => (
              <AuctionCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function AuctionCard({ listing }) {
  const [timeRemaining, setTimeRemaining] = useState(
    listing.ends_at ? formatTimeRemaining(listing.ends_at) : null
  );

  useEffect(() => {
    if (!listing.ends_at || listing.listing_type !== 'auction') return;

    const interval = setInterval(() => {
      setTimeRemaining(formatTimeRemaining(listing.ends_at));
    }, 1000);

    return () => clearInterval(interval);
  }, [listing.ends_at, listing.listing_type]);

  return (
    <Link
      to={`/listings/${listing.id}`}
      data-testid={`auction-card-${listing.id}`}
      className="card-auction overflow-hidden"
    >
      <div className="relative">
        <img
          src={listing.images[0] || 'https://via.placeholder.com/400x300'}
          alt={listing.title}
          className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
        />
        {listing.listing_type === 'auction' && timeRemaining && !timeRemaining.isEnded && (
          <div
            data-testid="time-badge"
            className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-mono font-bold ${
              timeRemaining.isUrgent
                ? 'bg-red-500 text-white animate-pulse'
                : 'bg-white/90 text-slate-900'
            }`}
          >
            <Clock className="inline w-3 h-3 mr-1" />
            {timeRemaining.text}
          </div>
        )}
        {listing.listing_type === 'auction' && (
          <div data-testid="live-badge" className="absolute top-2 left-2 bg-red-100 text-red-600 px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider">
            LIVE
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-slate-900 dark:text-white mb-2 line-clamp-1">
          {listing.title}
        </h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {listing.listing_type === 'auction' ? 'Current Bid' : 'Buy Now'}
            </p>
            <p data-testid="listing-price" className="text-lg font-bold text-blue-600">
              {formatCurrency(listing.current_price || listing.buy_now_price || 0)}
            </p>
          </div>
          {listing.listing_type === 'auction' && (
            <div className="text-right">
              <p className="text-xs text-slate-500 dark:text-slate-400">Bids</p>
              <p data-testid="bid-count" className="text-sm font-semibold text-slate-900 dark:text-white">
                {listing.bid_count || 0}
              </p>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}