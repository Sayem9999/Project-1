import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Clock, Heart, User, Package, Shield, TrendingUp } from 'lucide-react';
import api from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { formatCurrency, formatTimeRemaining, formatRelativeTime } from '../lib/utils';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';
import BkashCheckout from '../components/BkashCheckout';

export default function ProductDetailPage() {
  const { id } = useParams();
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [listing, setListing] = useState(null);
  const [bids, setBids] = useState([]);
  const [bidAmount, setBidAmount] = useState('');
  const [loading, setLoading] = useState(true);
  const [bidding, setBidding] = useState(false);
  const [selectedImage, setSelectedImage] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [showBkashCheckout, setShowBkashCheckout] = useState(false);

  useEffect(() => {
    fetchListing();
    fetchBids();
  }, [id]);

  useEffect(() => {
    if (!listing || !listing.ends_at || listing.listing_type !== 'auction') return;

    const interval = setInterval(() => {
      setTimeRemaining(formatTimeRemaining(listing.ends_at));
    }, 1000);

    return () => clearInterval(interval);
  }, [listing]);

  const fetchListing = async () => {
    try {
      const res = await api.getListing(id);
      setListing(res.data);
      if (res.data.ends_at) {
        setTimeRemaining(formatTimeRemaining(res.data.ends_at));
      }
    } catch (error) {
      toast.error('Failed to load listing');
    } finally {
      setLoading(false);
    }
  };

  const fetchBids = async () => {
    try {
      const res = await api.getListingBids(id);
      setBids(res.data);
    } catch (error) {
      console.error('Error fetching bids:', error);
    }
  };

  const handlePlaceBid = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      toast.error('Please login to place a bid');
      navigate('/login');
      return;
    }

    setBidding(true);
    try {
      await api.placeBid({ listing_id: id, amount: parseFloat(bidAmount) });
      toast.success('Bid placed successfully!');
      setBidAmount('');
      fetchListing();
      fetchBids();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to place bid');
    } finally {
      setBidding(false);
    }
  };

  const handleBuyNow = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to buy');
      navigate('/login');
      return;
    }

    try {
      const originUrl = window.location.origin;
      const res = await api.createCheckout({ listing_id: id, origin_url: originUrl });
      window.location.href = res.data.url;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create checkout');
    }
  };

  if (loading) {
    return (
      <div data-testid="loading-spinner" className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Listing not found</p>
      </div>
    );
  }

  const minBid = listing.current_price + 1;

  return (
    <div data-testid="product-detail-page" className="min-h-screen bg-slate-50 dark:bg-slate-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Left: Image Gallery */}
          <div className="lg:col-span-3">
            <div className="bg-white dark:bg-slate-800 rounded-xl overflow-hidden shadow-lg">
              <div className="aspect-square">
                <img
                  src={listing.images[selectedImage] || 'https://via.placeholder.com/600'}
                  alt={listing.title}
                  className="w-full h-full object-cover"
                />
              </div>
              {listing.images.length > 1 && (
                <div className="flex space-x-2 p-4 overflow-x-auto">
                  {listing.images.map((img, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedImage(idx)}
                      className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 ${
                        selectedImage === idx ? 'border-blue-600' : 'border-transparent'
                      }`}
                    >
                      <img src={img} alt="" className="w-full h-full object-cover" />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Description */}
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 mt-6 shadow-lg">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">Description</h2>
              <p className="text-slate-600 dark:text-slate-300 whitespace-pre-wrap">{listing.description}</p>

              <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
                <div className="flex items-center space-x-3">
                  <Package className="w-5 h-5 text-slate-400" />
                  <div>
                    <p className="text-xs text-slate-500">Condition</p>
                    <p className="font-semibold text-slate-900 dark:text-white">{listing.condition}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Shield className="w-5 h-5 text-slate-400" />
                  <div>
                    <p className="text-xs text-slate-500">Category</p>
                    <p className="font-semibold text-slate-900 dark:text-white">{listing.category}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Bid History */}
            {listing.listing_type === 'auction' && bids.length > 0 && (
              <div className="bg-white dark:bg-slate-800 rounded-xl p-6 mt-6 shadow-lg">
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4 flex items-center space-x-2">
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                  <span>Bid History</span>
                </h2>
                <div className="space-y-3">
                  {bids.slice(0, 10).map((bid) => (
                    <div
                      key={bid.id}
                      data-testid={`bid-history-${bid.id}`}
                      className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <User className="w-5 h-5 text-slate-400" />
                        <span className="font-medium text-slate-900 dark:text-white">{bid.bidder_username}</span>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-blue-600">{formatCurrency(bid.amount)}</p>
                        <p className="text-xs text-slate-500">{formatRelativeTime(bid.timestamp)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right: Bidding Box (Sticky) */}
          <div className="lg:col-span-2">
            <div className="sticky top-20 bg-white dark:bg-slate-800 rounded-xl p-6 shadow-xl border-2 border-blue-100 dark:border-blue-900">
              <h1 data-testid="listing-title" className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
                {listing.title}
              </h1>

              {/* Seller Info */}
              <div className="flex items-center space-x-3 mb-6 pb-6 border-b border-slate-200 dark:border-slate-700">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">Seller</p>
                  <p className="font-semibold text-slate-900 dark:text-white">{listing.seller_username}</p>
                </div>
              </div>

              {/* Auction Info */}
              {listing.listing_type === 'auction' && (
                <>
                  {timeRemaining && !timeRemaining.isEnded && (
                    <div
                      data-testid="countdown-timer"
                      className={`mb-6 p-4 rounded-lg ${
                        timeRemaining.isUrgent
                          ? 'bg-red-50 border-2 border-red-500'
                          : 'bg-blue-50 border-2 border-blue-200'
                      }`}
                    >
                      <div className="flex items-center justify-center space-x-2">
                        <Clock className={`w-6 h-6 ${timeRemaining.isUrgent ? 'text-red-600' : 'text-blue-600'}`} />
                        <div className="text-center">
                          <p className="text-xs text-slate-600">Time Remaining</p>
                          <p
                            className={`text-3xl font-mono font-bold ${
                              timeRemaining.isUrgent ? 'text-red-600' : 'text-blue-600'
                            }`}
                          >
                            {timeRemaining.text}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="mb-6">
                    <p className="text-sm text-slate-500 mb-1">Current Bid</p>
                    <p data-testid="current-bid-amount" className="text-4xl font-bold text-blue-600">
                      {formatCurrency(listing.current_price)}
                    </p>
                    <p className="text-sm text-slate-500 mt-1">{listing.bid_count} bids</p>
                  </div>

                  {/* Place Bid Form */}
                  {!timeRemaining?.isEnded && listing.status === 'active' && user?.id !== listing.seller_id && (
                    <form data-testid="bid-form" onSubmit={handlePlaceBid} className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                          Your Bid (min: {formatCurrency(minBid)})
                        </label>
                        <input
                          data-testid="bid-amount-input"
                          type="number"
                          step="0.01"
                          min={minBid}
                          value={bidAmount}
                          onChange={(e) => setBidAmount(e.target.value)}
                          required
                          className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-lg font-mono"
                          placeholder={`$${minBid}.00`}
                        />
                      </div>
                      <Button
                        data-testid="place-bid-btn"
                        type="submit"
                        disabled={bidding}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-full text-lg py-4 font-bold shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all disabled:bg-slate-400"
                      >
                        {bidding ? 'Placing Bid...' : 'Place Bid'}
                      </Button>
                    </form>
                  )}
                </>
              )}

              {/* Buy Now */}
              {listing.listing_type === 'buy_now' && listing.status === 'active' && (
                <>
                  <div className="mb-6">
                    <p className="text-sm text-slate-500 mb-1">Price</p>
                    <p data-testid="buy-now-price" className="text-4xl font-bold text-blue-600">
                      {formatCurrency(listing.buy_now_price)}
                    </p>
                  </div>
                  <Button
                    data-testid="buy-now-btn"
                    onClick={handleBuyNow}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-full text-lg py-4 font-bold shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all"
                  >
                    Buy Now
                  </Button>
                </>
              )}

              {listing.status !== 'active' && (
                <div className="bg-slate-100 dark:bg-slate-700 rounded-lg p-4 text-center">
                  <p className="font-semibold text-slate-600 dark:text-slate-300">
                    This listing is {listing.status}
                  </p>
                </div>
              )}

              {/* Watchlist */}
              <Button
                data-testid="add-to-watchlist-btn"
                variant="outline"
                className="w-full mt-4 flex items-center justify-center space-x-2"
              >
                <Heart className="w-5 h-5" />
                <span>Add to Watchlist</span>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}