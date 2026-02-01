import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Receipt, ArrowUpRight, ArrowDownLeft, Clock, CheckCircle, XCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../lib/api';
import { formatCurrency } from '../lib/utils';

export default function TransactionHistoryPage() {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      const res = await api.get('/api/transactions');
      setTransactions(res.data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      COMPLETED: { icon: CheckCircle, color: 'bg-green-100 text-green-700', label: 'Completed' },
      CREATED: { icon: Clock, color: 'bg-yellow-100 text-yellow-700', label: 'Pending' },
      FAILED: { icon: XCircle, color: 'bg-red-100 text-red-700', label: 'Failed' },
    };

    const config = statusConfig[status] || statusConfig.CREATED;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-semibold ${config.color}`}>
        <Icon className="w-4 h-4" />
        <span>{config.label}</span>
      </span>
    );
  };

  const getTransactionType = (transaction) => {
    if (transaction.buyer_id === user?.id) {
      return { type: 'purchase', icon: ArrowUpRight, color: 'text-red-600' };
    } else {
      return { type: 'sale', icon: ArrowDownLeft, color: 'text-green-600' };
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div data-testid="transaction-history-page" className="min-h-screen bg-slate-50 dark:bg-slate-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-2 flex items-center space-x-3">
            <Receipt className="w-10 h-10 text-blue-600" />
            <span>Transaction History</span>
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            View all your payment transactions
          </p>
        </div>

        {transactions.length === 0 ? (
          <div className="bg-white dark:bg-slate-800 rounded-xl p-12 text-center shadow-lg">
            <Receipt className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No transactions yet</p>
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 dark:bg-slate-700 border-b border-slate-200 dark:border-slate-600">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                      Transaction ID
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                  {transactions.map((transaction) => {
                    const transactionType = getTransactionType(transaction);
                    const Icon = transactionType.icon;

                    return (
                      <tr
                        key={transaction.id}
                        className="hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                      >
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-white">
                          {new Date(transaction.created_at).toLocaleDateString('en-GB', {
                            day: '2-digit',
                            month: 'short',
                            year: 'numeric',
                          })}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-600 dark:text-slate-300">
                          {transaction.trx_id || transaction.payment_id?.substring(0, 12) || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className={`flex items-center space-x-2 ${transactionType.color}`}>
                            <Icon className="w-4 h-4" />
                            <span className="font-semibold capitalize">{transactionType.type}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-slate-900 dark:text-white">
                          {formatCurrency(transaction.amount)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {getStatusBadge(transaction.status)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <Link
                            to={`/listings/${transaction.listing_id}`}
                            className="text-blue-600 hover:text-blue-700 font-medium"
                          >
                            View Listing →
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        {transactions.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg">
              <h3 className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
                Total Transactions
              </h3>
              <p className="text-3xl font-bold text-slate-900 dark:text-white">
                {transactions.length}
              </p>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg">
              <h3 className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
                Successful Payments
              </h3>
              <p className="text-3xl font-bold text-green-600">
                {transactions.filter((t) => t.status === 'COMPLETED').length}
              </p>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg">
              <h3 className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
                Total Amount
              </h3>
              <p className="text-3xl font-bold text-blue-600">
                {formatCurrency(
                  transactions
                    .filter((t) => t.status === 'COMPLETED')
                    .reduce((sum, t) => sum + t.amount, 0)
                )}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
