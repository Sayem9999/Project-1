import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';
import api from '../lib/api';

export default function BkashCheckout({ listingId, amount, onSuccess, onCancel }) {
  const [loading, setLoading] = useState(false);
  const [paymentId, setPaymentId] = useState(null);
  const [bkashScriptLoaded, setBkashScriptLoaded] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Load bKash script
    const script = document.createElement('script');
    script.src = 'https://scripts.sandbox.bka.sh/versions/1.2.0-beta/checkout/bKash-checkout-sandbox.js';
    script.async = true;
    script.onload = () => {
      setBkashScriptLoaded(true);
    };
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const handlePayment = async () => {
    setLoading(true);

    try {
      // Create payment
      const createRes = await api.post('/api/bkash/create', {
        listing_id: listingId,
        amount: amount,
      });

      const { paymentID, bkashURL } = createRes.data;
      setPaymentId(paymentID);

      // Initialize bKash payment
      if (window.bKash && bkashScriptLoaded) {
        window.bKash.init({
          paymentMode: 'checkout',
          paymentRequest: {
            amount: amount.toString(),
            intent: 'sale',
          },
          createRequest: async () => {
            return createRes.data;
          },
          executeRequestOnAuthorization: async () => {
            try {
              const executeRes = await api.post(`/api/bkash/execute/${paymentID}`);
              
              if (executeRes.data.statusCode === '0000') {
                toast.success('Payment successful!');
                if (onSuccess) {
                  onSuccess(executeRes.data);
                }
              } else {
                toast.error('Payment failed: ' + executeRes.data.statusMessage);
              }
            } catch (error) {
              toast.error('Payment execution failed');
            }
          },
          onClose: () => {
            setLoading(false);
            if (onCancel) {
              onCancel();
            }
          },
        });

        window.bKash.create().click();
      } else {
        // Fallback: redirect to bKash URL
        if (bkashURL) {
          window.location.href = bkashURL;
        } else {
          toast.error('bKash payment initialization failed');
        }
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Payment creation failed');
      setLoading(false);
    }
  };

  return (
    <div>
      <Button
        onClick={handlePayment}
        disabled={loading}
        className="w-full bg-pink-600 hover:bg-pink-700 text-white rounded-full py-4 text-lg font-bold flex items-center justify-center space-x-2"
      >
        {loading ? (
          'Processing...'
        ) : (
          <>
            <span>Pay with</span>
            <span className="font-bold">bKash</span>
          </>
        )}
      </Button>

      <div className="mt-4 p-4 bg-pink-50 rounded-lg border border-pink-200">
        <h4 className="font-semibold text-sm mb-2 text-slate-900">Test Payment (Sandbox)</h4>
        <ul className="text-xs space-y-1 text-slate-700">
          <li>• Number: 01619777283</li>
          <li>• OTP: 123456</li>
          <li>• PIN: 12121</li>
        </ul>
      </div>
    </div>
  );
}
