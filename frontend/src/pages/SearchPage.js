import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Search, SlidersHorizontal, X } from 'lucide-react';
import api from '../lib/api';
import { formatCurrency, formatTimeRemaining } from '../lib/utils';
import { Button } from '../components/ui/button';

const categories = ['All', 'Electronics', 'Fashion', 'Watches', 'Collectibles', 'Home & Garden', 'Sports', 'Other'];
const conditions = ['All', 'New', 'Used', 'Refurbished'];
const sortOptions = [
  { value: 'created_at', label: 'Newest First' },
  { value: 'ending_soon', label: 'Ending Soon' },
  { value: 'price_low', label: 'Price: Low to High' },
  { value: 'price_high', label: 'Price: High to Low' },
];

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [showFilters, setShowFilters] = useState(false);
  
  const [filters, setFilters] = useState({
    category: searchParams.get('category') || 'All',
    condition: searchParams.get('condition') || 'All',
    minPrice: searchParams.get('min_price') || '',
    maxPrice: searchParams.get('max_price') || '',
    sortBy: searchParams.get('sort') || 'created_at',
  });

  useEffect(() => {
    fetchListings();
  }, [searchQuery, filters]);

  const fetchListings = async () => {
    setLoading(true);
    try {
      const params = {
        status: 'active',
        search: searchQuery || undefined,
        category: filters.category !== 'All' ? filters.category : undefined,
        condition: filters.condition !== 'All' ? filters.condition : undefined,
        min_price: filters.minPrice || undefined,
        max_price: filters.maxPrice || undefined,
        sort_by: filters.sortBy,
      };
      
      const res = await api.getListings(params);
      setListings(res.data);
    } catch (error) {
      console.error('Error fetching listings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchListings();
  };

  const updateFilter = (key, value) => {
    setFilters({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    setFilters({
      category: 'All',
      condition: 'All',
      minPrice: '',
      maxPrice: '',
      sortBy: 'created_at',
    });
    setSearchQuery('');
  };

  return (
    <div data-testid="search-page" className="min-h-screen bg-slate-50 dark:bg-slate-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Search Bar */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                data-testid="search-input"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for anything..."
                className="w-full pl-12 pr-4 py-4 bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-lg"
              />
            </div>
            <Button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              variant="outline"
              className="flex items-center space-x-2 px-6 border-2 border-slate-300"
            >
              <SlidersHorizontal className="w-5 h-5" />
              <span>Filters</span>
            </Button>
          </form>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 mb-8 shadow-lg">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">Filters</h3>
              <button
                onClick={clearFilters}
                className="text-blue-600 hover:text-blue-700 font-medium flex items-center space-x-1"
              >
                <X className="w-4 h-4" />
                <span>Clear All</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Category
                </label>
                <select
                  value={filters.category}
                  onChange={(e) => updateFilter('category', e.target.value)}
                  className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              {/* Condition */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Condition
                </label>
                <select
                  value={filters.condition}
                  onChange={(e) => updateFilter('condition', e.target.value)}
                  className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg"
                >
                  {conditions.map((cond) => (
                    <option key={cond} value={cond}>{cond}</option>
                  ))}
                </select>
              </div>

              {/* Price Range */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Min Price
                </label>
                <input
                  type="number"
                  value={filters.minPrice}
                  onChange={(e) => updateFilter('minPrice', e.target.value)}
                  placeholder="$0"
                  className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Max Price
                </label>
                <input
                  type="number"
                  value={filters.maxPrice}
                  onChange={(e) => updateFilter('maxPrice', e.target.value)}
                  placeholder="$10000"
                  className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg"
                />
              </div>
            </div>

            {/* Sort */}
            <div className="mt-6">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Sort By
              </label>
              <div className="flex flex-wrap gap-2">
                {sortOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => updateFilter('sortBy', option.value)}
                    className={`px-4 py-2 rounded-full font-medium transition-all ${
                      filters.sortBy === option.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        <div className="mb-4">
          <p className="text-slate-600 dark:text-slate-400">
            {loading ? 'Searching...' : `${listings.length} results found`}
          </p>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white dark:bg-slate-800 rounded-xl p-4 animate-pulse">
                <div className="bg-slate-200 h-48 rounded-lg mb-4"></div>
                <div className="bg-slate-200 h-4 rounded mb-2"></div>
                <div className="bg-slate-200 h-4 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : listings.length === 0 ? (
          <div className="text-center py-12">
            <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No listings found. Try adjusting your filters.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {listings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ListingCard({ listing }) {
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
      className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden hover:shadow-xl transition-all"
    >
      <div className="relative">
        <img
          src={listing.images[0] || 'https://via.placeholder.com/400x300'}
          alt={listing.title}
          className="w-full h-48 object-cover"
        />
        {listing.listing_type === 'auction' && timeRemaining && !timeRemaining.isEnded && (
          <div
            className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-mono font-bold ${
              timeRemaining.isUrgent
                ? 'bg-red-500 text-white animate-pulse'
                : 'bg-white/90 text-slate-900'
            }`}
          >
            {timeRemaining.text}
          </div>
        )}
        {listing.listing_type === 'auction' && (
          <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-0.5 rounded text-xs font-bold uppercase">
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
