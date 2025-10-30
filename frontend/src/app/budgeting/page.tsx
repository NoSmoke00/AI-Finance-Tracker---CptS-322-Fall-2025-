'use client';

import { useEffect, useState } from 'react';
import AppLayout from '@/components/AppLayout';
import { budgetsApi } from '@/lib/api';
import { BudgetWithStatus, BudgetPeriod } from '@/types';

const CATEGORIES = [
  'FOOD_AND_DRINK',
  'TRAVEL',
  'TRANSPORTATION',
  'GENERAL_MERCHANDISE',
  'RENT_AND_UTILITIES',
  'ENTERTAINMENT',
  'HEALTHCARE',
  'PERSONAL_CARE',
  'HOME',
  'AUTO_AND_TRANSPORT',
  'BILLS',
  'GROCERIES',
  'SHOPPING',
  'LOAN_PAYMENTS',
  'RENT',
  'DINING',
  'SUBSCRIPTIONS',
];

export default function BudgetingPage() {
  const [budgets, setBudgets] = useState<BudgetWithStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingBudget, setEditingBudget] = useState<BudgetWithStatus | null>(null);

  // Form state
  const [category, setCategory] = useState('');
  const [amount, setAmount] = useState('');
  const [period, setPeriod] = useState<BudgetPeriod>('monthly');
  const [alertThreshold, setAlertThreshold] = useState('80');

  const loadBudgets = async () => {
    setLoading(true);
    try {
      const data = await budgetsApi.getStatus();
      setBudgets(data);
    } catch (error) {
      console.error('Failed to load budgets:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBudgets();
  }, []);

  const handleCreate = () => {
    setEditingBudget(null);
    setCategory('');
    setAmount('');
    setPeriod('monthly');
    setAlertThreshold('80');
    setShowModal(true);
  };

  const handleEdit = (budget: BudgetWithStatus) => {
    setEditingBudget(budget);
    setCategory(budget.category);
    setAmount(budget.amount.toString());
    setPeriod(budget.period);
    setAlertThreshold(budget.alert_threshold.toString());
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingBudget) {
        await budgetsApi.update(editingBudget.id, {
          amount: parseFloat(amount),
          period,
          alert_threshold: parseFloat(alertThreshold),
        });
      } else {
        await budgetsApi.create({
          category,
          amount: parseFloat(amount),
          period,
          alert_threshold: parseFloat(alertThreshold),
        });
      }
      setShowModal(false);
      await loadBudgets();
    } catch (error) {
      console.error('Failed to save budget:', error);
      alert('Failed to save budget. Please try again.');
    }
  };

  const handleDelete = async (budgetId: number) => {
    if (!confirm('Are you sure you want to delete this budget?')) return;
    try {
      await budgetsApi.delete(budgetId);
      await loadBudgets();
    } catch (error) {
      console.error('Failed to delete budget:', error);
      alert('Failed to delete budget. Please try again.');
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-red-500';
    if (percentage >= 80) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const formatCategory = (cat: string) => {
    return cat.split('_').map(word => word.charAt(0) + word.slice(1).toLowerCase()).join(' ');
  };

  return (
    <AppLayout>
      <div className="flex-1 overflow-auto">
        <main className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-green-600">Budgeting</h1>
            <button
              onClick={handleCreate}
              className="px-6 py-2 rounded-full bg-gradient-to-r from-blue-600 to-green-600 text-white shadow-md hover:shadow-lg transition-shadow"
            >
              Create Budget
            </button>
          </div>

          {loading ? (
            <div className="bg-white shadow rounded-xl p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading budgets...</p>
            </div>
          ) : budgets.length === 0 ? (
            <div className="bg-white shadow rounded-xl p-12 text-center">
              <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
              <p className="text-gray-600 text-lg mb-4">No budgets set up yet</p>
              <p className="text-gray-500 mb-6">Create a budget to track your spending goals</p>
              <button
                onClick={handleCreate}
                className="px-6 py-3 rounded-full bg-gradient-to-r from-blue-600 to-green-600 text-white shadow-md hover:shadow-lg transition-shadow"
              >
                Create Your First Budget
              </button>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {budgets.map((budget) => (
                <div key={budget.id} className="bg-white shadow-lg rounded-xl p-6 hover:shadow-xl transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-lg text-gray-900">{formatCategory(budget.category)}</h3>
                      <p className="text-sm text-gray-600 capitalize">{budget.period}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(budget)}
                        className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
                        title="Edit"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDelete(budget.id)}
                        className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                        title="Delete"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Budget</span>
                      <span className="text-lg font-bold text-gray-900">${budget.amount.toFixed(2)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all ${getProgressColor(budget.percentage_used)}`}
                        style={{ width: `${Math.min(budget.percentage_used, 100)}%` }}
                      />
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Spent:</span>
                      <span className="font-semibold text-gray-900">${budget.spent.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Remaining:</span>
                      <span className={`font-semibold ${budget.remaining >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ${budget.remaining.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Progress:</span>
                      <span className={`font-semibold ${getProgressColor(budget.percentage_used).replace('bg-', 'text-')}`}>
                        {budget.percentage_used.toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  {budget.is_over_budget && (
                    <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-700 font-medium">⚠️ Over budget</p>
                    </div>
                  )}
                  {budget.is_near_threshold && !budget.is_over_budget && (
                    <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <p className="text-sm text-yellow-700 font-medium">⚠️ Near threshold</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Modal */}
          {showModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowModal(false)}>
              <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
                <h2 className="text-2xl font-bold mb-4 text-gray-900">{editingBudget ? 'Edit Budget' : 'Create Budget'}</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                    {editingBudget ? (
                      <input
                        type="text"
                        value={formatCategory(category)}
                        disabled
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                      />
                    ) : (
                      <select
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
                      >
                        <option value="" className="text-gray-500">Select a category</option>
                        {CATEGORIES.map((cat) => (
                          <option key={cat} value={cat} className="text-gray-900">{formatCategory(cat)}</option>
                        ))}
                      </select>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Amount ($)</label>
                    <input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      required
                      min="0"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Period</label>
                    <select
                      value={period}
                      onChange={(e) => setPeriod(e.target.value as BudgetPeriod)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
                    >
                      <option value="monthly" className="text-gray-900">Monthly</option>
                      <option value="weekly" className="text-gray-900">Weekly</option>
                      <option value="yearly" className="text-gray-900">Yearly</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Alert Threshold (%)</label>
                    <input
                      type="number"
                      value={alertThreshold}
                      onChange={(e) => setAlertThreshold(e.target.value)}
                      required
                      min="0"
                      max="100"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                    />
                    <p className="text-xs text-gray-500 mt-1">Alert when spending reaches this percentage</p>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowModal(false)}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-lg hover:shadow-md transition-shadow"
                    >
                      {editingBudget ? 'Update' : 'Create'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </main>
      </div>
    </AppLayout>
  );
}

