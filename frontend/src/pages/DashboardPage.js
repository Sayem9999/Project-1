import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Package, TrendingUp, Heart } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../lib/api';
import { formatCurrency, formatTimeRemaining } from '../lib/utils';

export default function DashboardPage() {
  const { user, isAuthenticated } = useAuth();
  const [myListings, setMyListings] = useState([]);
  const [myBids, setMyBids] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('listings');

  useEffect(() => {
    if (!isAuthenticated) return;
    fetchDashboardData();
  }, [isAuthenticated]);

  const fetchDashboardData = async () => {
    try {
      const [listingsRes, bidsRes, watchlistRes] = await Promise.all([
        api.getMyListings(),
        api.getUserBids(user.id),
        api.getWatchlist(),
      ]);
      setMyListings(listingsRes.data);
      setMyBids(bidsRes.data);
      setWatchlist(watchlistRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'listings', label: 'My Listings', icon: Package, count: myListings.length },
    { id: 'bids', label: 'My Bids', icon: TrendingUp, count: myBids.length },
    { id: 'watchlist', label: 'Watchlist', icon: Heart, count: watchlist.length },
  ];

  return (
    <div data-testid="dashboard-page" className="min-h-screen bg-slate-50 dark:bg-slate-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-2">My Dashboard</h1>
          <p className="text-slate-600 dark:text-slate-400">Manage your listings, bids, and watchlist</p>
        </div>

        {/* Tabs */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg mb-8">
          <div className="flex border-b border-slate-200 dark:border-slate-700">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                data-testid={`tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 px-6 py-4 flex items-center justify-center space-x-2 font-semibold transition-all ${
                  activeTab === tab.id
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
                <span className="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 rounded-full text-xs">
                  {tab.count}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {activeTab === 'listings' && (
                <div>
                  {myListings.length === 0 ? (
                    <div className="text-center py-12">
                      <Package className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                      <p className="text-slate-500">You haven't created any listings yet</p>
                      <Link
                        to="/create-listing"
                        className="inline-block mt-4 px-6 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition"
                      >
                        Create Your First Listing
                      </Link>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                      {myListings.map((listing) => (
                        <ListingCard key={listing.id} listing={listing} />
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'bids' && (
                <div>
                  {myBids.length === 0 ? (
                    <div className="text-center py-12">
                      <TrendingUp className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                      <p className="text-slate-500">You haven't placed any bids yet</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {myBids.map((bid) => (
                        <div
                          key={bid.id}
                          data-testid={`bid-item-${bid.id}`}
                          className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700 rounded-lg"
                        >
                          <div>
                            <Link
                              to={`/listings/${bid.listing_id}`}
                              className="font-semibold text-blue-600 hover:text-blue-700"
                            >
                              View Listing
                            </Link>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-slate-900 dark:text-white">{formatCurrency(bid.amount)}</p>
                            <p className="text-xs text-slate-500">{new Date(bid.timestamp).toLocaleDateString()}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'watchlist' && (
                <div>
                  {watchlist.length === 0 ? (
                    <div className="text-center py-12">
                      <Heart className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                      <p className="text-slate-500">Your watchlist is empty</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                      {watchlist.map((listingId) => (
                        <div key={listingId} className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                          <Link to={`/listings/${listingId}`} className="text-blue-600 hover:text-blue-700">
                            View Listing
                          </Link>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function ListingCard({ listing }) {
  return (
    <Link
      to={`/listings/${listing.id}`}
      data-testid={`listing-card-${listing.id}`}
      className="card-auction overflow-hidden"
    >
      <div className="relative">
        <img
          src={listing.images[0] || 'https://via.placeholder.com/400x300'}
          alt={listing.title}
          className="w-full h-48 object-cover"
        />
        <div
          className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-bold ${
            listing.status === 'active'
              ? 'bg-green-500 text-white'
              : 'bg-slate-500 text-white'
          }`}
        >
          {listing.status.toUpperCase()}
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-slate-900 dark:text-white mb-2 line-clamp-1">
          {listing.title}
        </h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {listing.listing_type === 'auction' ? 'Current Bid' : 'Price'}
            </p>
            <p className="text-lg font-bold text-blue-600">
              {formatCurrency(listing.current_price || listing.buy_now_price || 0)}
            </p>
          </div>
          {listing.listing_type === 'auction' && (
            <div className="text-right">
              <p className="text-xs text-slate-500 dark:text-slate-400">Bids</p>
              <p className="text-sm font-semibold text-slate-900 dark:text-white">
                {listing.bid_count || 0}
              </p>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}