import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { User, Star, Package, TrendingUp, Calendar } from 'lucide-react';
import api from '../lib/api';
import { formatCurrency } from '../lib/utils';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';

export default function UserProfilePage() {
  const { userId } = useParams();
  const [user, setUser] = useState(null);
  const [listings, setListings] = useState([]);
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showRatingForm, setShowRatingForm] = useState(false);
  const [newRating, setNewRating] = useState({
    rating: 5,
    comment: '',
  });

  useEffect(() => {
    fetchUserData();
  }, [userId]);

  const fetchUserData = async () => {
    try {
      const [userRes, ratingsRes] = await Promise.all([
        api.getUserProfile(userId),
        api.getUserRatings(userId),
      ]);
      setUser(userRes.data);
      setRatings(ratingsRes.data);
    } catch (error) {
      console.error('Error fetching user data:', error);
      toast.error('Failed to load user profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitRating = async (e) => {
    e.preventDefault();
    try {
      await api.createRating({
        rated_user_id: userId,
        rating: newRating.rating,
        comment: newRating.comment,
      });
      toast.success('Rating submitted successfully!');
      setShowRatingForm(false);
      setNewRating({ rating: 5, comment: '' });
      fetchUserData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit rating');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>User not found</p>
      </div>
    );
  }

  return (
    <div data-testid="user-profile-page" className="min-h-screen bg-slate-50 dark:bg-slate-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Profile Header */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-8 shadow-lg mb-8">
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-6">
            <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-12 h-12 text-blue-600" />
            </div>
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
                {user.username}
              </h1>
              <div className="flex items-center justify-center md:justify-start space-x-4 text-slate-600 dark:text-slate-400">
                <div className="flex items-center space-x-1">
                  <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                  <span className="font-semibold">{user.rating_score.toFixed(1)}</span>
                  <span>({user.total_ratings} ratings)</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Calendar className="w-5 h-5" />
                  <span>Member since {new Date(user.created_at).getFullYear()}</span>
                </div>
              </div>
              {user.bio && (
                <p className="mt-4 text-slate-600 dark:text-slate-300">{user.bio}</p>
              )}
            </div>
            <Button
              onClick={() => setShowRatingForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-full px-6 py-2"
            >
              Leave Rating
            </Button>
          </div>
        </div>

        {/* Rating Form */}
        {showRatingForm && (
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg mb-8">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
              Rate {user.username}
            </h3>
            <form onSubmit={handleSubmitRating} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Rating
                </label>
                <div className="flex space-x-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setNewRating({ ...newRating, rating: star })}
                      className="focus:outline-none"
                    >
                      <Star
                        className={`w-8 h-8 ${
                          star <= newRating.rating
                            ? 'text-yellow-500 fill-yellow-500'
                            : 'text-slate-300'
                        }`}
                      />
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Comment (optional)
                </label>
                <textarea
                  value={newRating.comment}
                  onChange={(e) => setNewRating({ ...newRating, comment: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg"
                  placeholder="Share your experience..."
                />
              </div>
              <div className="flex space-x-4">
                <Button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white">
                  Submit Rating
                </Button>
                <Button
                  type="button"
                  onClick={() => setShowRatingForm(false)}
                  variant="outline"
                  className="border-2 border-slate-300"
                >
                  Cancel
                </Button>
              </div>
            </form>
          </div>
        )}

        {/* Ratings List */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">
            Ratings & Reviews ({ratings.length})
          </h2>
          {ratings.length === 0 ? (
            <p className="text-slate-500 text-center py-8">No ratings yet</p>
          ) : (
            <div className="space-y-4">
              {ratings.map((rating) => (
                <div
                  key={rating.id}
                  className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-slate-900 dark:text-white">
                        {rating.rater_username}
                      </span>
                      <div className="flex">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`w-4 h-4 ${
                              i < rating.rating
                                ? 'text-yellow-500 fill-yellow-500'
                                : 'text-slate-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                    <span className="text-sm text-slate-500">
                      {new Date(rating.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {rating.comment && (
                    <p className="text-slate-600 dark:text-slate-300">{rating.comment}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
