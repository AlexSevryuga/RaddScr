'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { stripeApi } from '@/lib/api';
import type { Subscription } from '@/types';

export default function BillingPage() {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    loadSubscription();
  }, []);

  const loadSubscription = async () => {
    try {
      const data = await stripeApi.getSubscription();
      setSubscription(data);
    } catch (err: any) {
      console.error('Failed to load subscription', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (
      !confirm(
        'Are you sure you want to cancel your subscription? You will retain access until the end of your billing period.'
      )
    ) {
      return;
    }

    setCancelling(true);
    try {
      await stripeApi.cancelSubscription();
      await loadSubscription();
      alert('Subscription cancelled successfully');
    } catch (err: any) {
      alert('Failed to cancel subscription. Please try again.');
    } finally {
      setCancelling(false);
    }
  };

  const getPlanName = (plan: string) => {
    return plan.charAt(0).toUpperCase() + plan.slice(1);
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      active: 'bg-green-100 text-green-800',
      past_due: 'bg-yellow-100 text-yellow-800',
      cancelled: 'bg-red-100 text-red-800',
      none: 'bg-gray-100 text-gray-800',
    };

    return (
      <span
        className={`px-3 py-1 rounded-full text-sm font-medium ${
          styles[status as keyof typeof styles] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {status === 'none' ? 'Free' : status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Billing & Subscription</h1>

      {/* Current Plan */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Current Plan</h2>

        {!subscription || subscription.status === 'none' ? (
          <div>
            <div className="flex items-center gap-4 mb-4">
              <span className="text-2xl font-bold text-gray-900">Free Plan</span>
              {getStatusBadge('none')}
            </div>
            <p className="text-gray-600 mb-6">
              You're currently on the free plan. Upgrade to unlock more validations and features.
            </p>
            <Link
              href="/pricing"
              className="inline-block bg-primary-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary-700 transition"
            >
              Upgrade Now
            </Link>
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <span className="text-2xl font-bold text-gray-900">
                  {getPlanName(subscription.plan)} Plan
                </span>
                {getStatusBadge(subscription.status)}
              </div>
              {subscription.status === 'active' && (
                <button
                  onClick={handleCancelSubscription}
                  disabled={cancelling}
                  className="text-red-600 hover:text-red-700 font-medium disabled:opacity-50"
                >
                  {cancelling ? 'Cancelling...' : 'Cancel Subscription'}
                </button>
              )}
            </div>

            {/* Usage */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Validations Used</span>
                <span>
                  {subscription.validations_used} /{' '}
                  {subscription.validations_limit || 'Unlimited'}
                </span>
              </div>
              {subscription.validations_limit && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full"
                    style={{
                      width: `${
                        (subscription.validations_used /
                          subscription.validations_limit) *
                        100
                      }%`,
                    }}
                  ></div>
                </div>
              )}
            </div>

            {/* Billing Period */}
            {subscription.current_period_end && (
              <p className="text-gray-600">
                {subscription.status === 'active' ? 'Next billing date: ' : 'Access until: '}
                {new Date(
                  subscription.current_period_end * 1000
                ).toLocaleDateString()}
              </p>
            )}

            {subscription.status === 'past_due' && (
              <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800 font-semibold">
                  ⚠️ Payment Failed
                </p>
                <p className="text-yellow-700 text-sm mt-1">
                  We couldn't process your payment. Please update your payment method to
                  continue using the service.
                </p>
              </div>
            )}

            {subscription.status === 'cancelled' && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 font-semibold">Subscription Cancelled</p>
                <p className="text-red-700 text-sm mt-1 mb-3">
                  Your subscription has been cancelled. You'll have access until the end of
                  your billing period.
                </p>
                <Link
                  href="/pricing"
                  className="inline-block bg-primary-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-primary-700 transition text-sm"
                >
                  Reactivate Subscription
                </Link>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Upgrade Options */}
      {(!subscription || subscription.status !== 'active') && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
          <h3 className="font-bold text-lg text-primary-900 mb-2">
            Unlock More Features
          </h3>
          <p className="text-primary-800 mb-4">
            Upgrade to get more validations, priority support, and advanced features.
          </p>
          <Link
            href="/pricing"
            className="inline-block bg-primary-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary-700 transition"
          >
            View Plans
          </Link>
        </div>
      )}

      {/* Billing History (placeholder) */}
      <div className="bg-white rounded-lg shadow-sm p-6 mt-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Billing History</h2>
        <p className="text-gray-600">
          View your billing history and download invoices from your{' '}
          <a href="#" className="text-primary-600 hover:text-primary-700 font-medium">
            Stripe customer portal
          </a>
          .
        </p>
      </div>
    </div>
  );
}
