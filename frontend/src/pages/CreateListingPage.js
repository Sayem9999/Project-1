import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';
import { Upload, X } from 'lucide-react';
import api from '../lib/api';

const categories = ['Electronics', 'Fashion', 'Watches', 'Collectibles', 'Home & Garden', 'Sports', 'Other'];
const conditions = ['New', 'Used', 'Refurbished'];

export default function CreateListingPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'Electronics',
    condition: 'New',
    listing_type: 'auction',
    starting_price: '',
    buy_now_price: '',
    duration_hours: '24',
    images: [],
  });
  const [imageUrls, setImageUrls] = useState(['']);

  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleImageUrlChange = (index, value) => {
    const newUrls = [...imageUrls];
    newUrls[index] = value;
    setImageUrls(newUrls);
    setFormData({ ...formData, images: newUrls.filter(url => url.trim()) });
  };

  const addImageUrlField = () => {
    setImageUrls([...imageUrls, '']);
  };

  const removeImageUrlField = (index) => {
    const newUrls = imageUrls.filter((_, i) => i !== index);
    setImageUrls(newUrls);
    setFormData({ ...formData, images: newUrls.filter(url => url.trim()) });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const submitData = {
        ...formData,
        starting_price: formData.listing_type === 'auction' ? parseFloat(formData.starting_price) : null,
        buy_now_price: formData.listing_type === 'buy_now' ? parseFloat(formData.buy_now_price) : null,
        duration_hours: formData.listing_type === 'auction' ? parseInt(formData.duration_hours) : null,
        images: formData.images.filter(url => url.trim()),
      };

      const res = await api.createListing(submitData);
      toast.success('Listing created successfully!');
      navigate(`/listings/${res.data.id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create listing');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid="create-listing-page" className="min-h-screen bg-slate-50 dark:bg-slate-900 py-12">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-2">List Your Item</h1>
          <p className="text-slate-600 dark:text-slate-400">Create an auction or fixed-price listing</p>
        </div>

        <form data-testid="create-listing-form" onSubmit={handleSubmit} className="bg-white dark:bg-slate-800 rounded-xl p-8 shadow-lg space-y-6">
          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Title *
            </label>
            <input
              id="title"
              data-testid="title-input"
              name="title"
              type="text"
              required
              value={formData.title}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="e.g., Vintage Rolex Watch"
            />
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Description *
            </label>
            <textarea
              id="description"
              data-testid="description-input"
              name="description"
              required
              value={formData.description}
              onChange={handleChange}
              rows={5}
              className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="Describe your item in detail..."
            />
          </div>

          {/* Category & Condition */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label htmlFor="category" className="block text-sm font-semibold text-slate-900 mb-2">
                Category *
              </label>
              <select
                id="category"
                data-testid="category-select"
                name="category"
                required
                value={formData.category}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white border-2 border-slate-300 text-slate-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="condition" className="block text-sm font-semibold text-slate-900 mb-2">
                Condition *
              </label>
              <select
                id="condition"
                data-testid="condition-select"
                name="condition"
                required
                value={formData.condition}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white border-2 border-slate-300 text-slate-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
              >
                {conditions.map((cond) => (
                  <option key={cond} value={cond}>{cond}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Listing Type */}
          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-3">
              Listing Type *
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                data-testid="auction-type-btn"
                onClick={() => setFormData({ ...formData, listing_type: 'auction' })}
                className={`p-4 rounded-lg border-2 transition-all ${
                  formData.listing_type === 'auction'
                    ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-slate-200 dark:border-slate-700'
                }`}
              >
                <p className="font-semibold text-slate-900 dark:text-white">Auction</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">Time-limited bidding</p>
              </button>
              <button
                type="button"
                data-testid="buy-now-type-btn"
                onClick={() => setFormData({ ...formData, listing_type: 'buy_now' })}
                className={`p-4 rounded-lg border-2 transition-all ${
                  formData.listing_type === 'buy_now'
                    ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-slate-200 dark:border-slate-700'
                }`}
              >
                <p className="font-semibold text-slate-900 dark:text-white">Buy Now</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">Fixed price</p>
              </button>
            </div>
          </div>

          {/* Auction Settings */}
          {formData.listing_type === 'auction' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label htmlFor="starting_price" className="block text-sm font-semibold text-slate-900 mb-2">
                  Starting Price (৳) *
                </label>
                <input
                  id="starting_price"
                  data-testid="starting-price-input"
                  name="starting_price"
                  type="number"
                  step="1"
                  min="1"
                  required={formData.listing_type === 'auction'}
                  value={formData.starting_price}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-white border-2 border-slate-300 text-slate-900 placeholder-slate-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                  placeholder="100"
                />
              </div>

              <div>
                <label htmlFor="duration_hours" className="block text-sm font-semibold text-slate-900 mb-2">
                  Duration (hours) *
                </label>
                <select
                  id="duration_hours"
                  data-testid="duration-select"
                  name="duration_hours"
                  required={formData.listing_type === 'auction'}
                  value={formData.duration_hours}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-white border-2 border-slate-300 text-slate-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                >
                  <option value="1">1 hour</option>
                  <option value="6">6 hours</option>
                  <option value="12">12 hours</option>
                  <option value="24">24 hours</option>
                  <option value="48">2 days</option>
                  <option value="72">3 days</option>
                  <option value="168">7 days</option>
                </select>
              </div>
            </div>
          )}

          {/* Buy Now Price */}
          {formData.listing_type === 'buy_now' && (
            <div>
              <label htmlFor="buy_now_price" className="block text-sm font-semibold text-slate-900 mb-2">
                Price (৳) *
              </label>
              <input
                id="buy_now_price"
                data-testid="buy-now-price-input"
                name="buy_now_price"
                type="number"
                step="1"
                min="1"
                required={formData.listing_type === 'buy_now'}
                value={formData.buy_now_price}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white border-2 border-slate-300 text-slate-900 placeholder-slate-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                placeholder="1000"
              />
            </div>
          )}

          {/* Images */}
          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-2">
              Images (URLs)
            </label>
            <div className="space-y-3">
              {imageUrls.map((url, index) => (
                <div key={index} className="flex space-x-2">
                  <input
                    data-testid={`image-url-input-${index}`}
                    type="url"
                    value={url}
                    onChange={(e) => handleImageUrlChange(index, e.target.value)}
                    className="flex-1 px-4 py-3 bg-white border-2 border-slate-300 text-slate-900 placeholder-slate-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    placeholder="https://example.com/image.jpg"
                  />
                  {imageUrls.length > 1 && (
                    <Button
                      type="button"
                      onClick={() => removeImageUrlField(index)}
                      variant="ghost"
                      size="icon"
                      className="flex-shrink-0"
                    >
                      <X className="w-5 h-5" />
                    </Button>
                  )}
                </div>
              ))}
              <Button
                type="button"
                data-testid="add-image-btn"
                onClick={addImageUrlField}
                variant="outline"
                className="w-full flex items-center justify-center space-x-2"
              >
                <Upload className="w-5 h-5" />
                <span>Add Image URL</span>
              </Button>
            </div>
          </div>

          {/* Submit */}
          <Button
            data-testid="submit-listing-btn"
            type="submit"
            disabled={loading}
            className="w-full btn-primary text-lg py-4"
          >
            {loading ? 'Creating Listing...' : 'Create Listing'}
          </Button>
        </form>
      </div>
    </div>
  );
}