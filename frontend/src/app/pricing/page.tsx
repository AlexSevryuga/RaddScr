'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { stripeApi } from '@/lib/api';

const plans = [
  {
    name: 'Starter',
    price: 29,
    plan_id: 'starter',
    validations: 100,
    features: [
      '100 validations per month',
      'Reddit + Twitter + LinkedIn analysis',
      'Detailed insights & recommendations',
      'Email notifications',
      'Basic support',
    ],
    popular: false,
  },
  {
    name: 'Pro',
    price: 79,
    plan_id: 'pro',
    validations: 500,
    features: [
      '500 validations per month',
      'Everything in Starter',
      'Priority email support',
      'API access',
      'Export reports (PDF/CSV)',
      'Custom branding',
    ],
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 199,
    plan_id: 'enterprise',
    validations: 'Unlimited',
    features: [
      'Unlimited validations',
      'Everything in Pro',
      'Dedicated account manager',
      'Custom integrations',
      'SLA guarantee',
      'White-label option',
    ],
    popular: false,
  },
];

export default function PricingPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState<string | null>(null);

  const handleSubscribe = async (planId: string) => {
    if (!user) {
      router.push('/register');
      return;
    }

    setLoading(planId);

    try {
      const { checkout_url } = await stripeApi.createCheckoutSession(planId);
      window.location.href = checkout_url;
    } catch (err: any) {
      alert('Failed to start checkout. Please try again.');
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white py-16">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Choose the plan that fits your validation needs. All plans include core features.
          </p>
        </div>

        {/* Plans Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16">
          {plans.map((plan) => (
            <div
              key={plan.plan_id}
              className={`bg-white rounded-xl shadow-lg p-8 relative ${
                plan.popular ? 'ring-2 ring-primary-600' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <span className="bg-primary-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {plan.name}
                </h3>
                <div className="text-5xl font-bold text-primary-600 mb-2">
                  ${plan.price}
                </div>
                <p className="text-gray-600">per month</p>
              </div>

              <div className="mb-6 text-center">
                <p className="text-gray-700 font-semibold">
                  {typeof plan.validations === 'number'
                    ? `${plan.validations} validations/mo`
                    : plan.validations}
                </p>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex gap-3">
                    <span className="text-green-600 font-bold flex-shrink-0">
                      ✓
                    </span>
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleSubscribe(plan.plan_id)}
                disabled={loading === plan.plan_id}
                className={`w-full py-3 rounded-lg font-semibold transition ${
                  plan.popular
                    ? 'bg-primary-600 text-white hover:bg-primary-700'
                    : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {loading === plan.plan_id
                  ? 'Loading...'
                  : user
                  ? 'Subscribe Now'
                  : 'Get Started'}
              </button>
            </div>
          ))}
        </div>

        {/* FAQ */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6 bg-white rounded-xl shadow-sm p-8">
            <div>
              <h3 className="font-bold text-lg mb-2">What counts as a validation?</h3>
              <p className="text-gray-600">
                Each unique SaaS idea you analyze counts as one validation. You can re-run
                the same project without using additional validations.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">Can I cancel anytime?</h3>
              <p className="text-gray-600">
                Yes! All plans are month-to-month with no long-term commitment. Cancel
                anytime from your billing dashboard.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">What payment methods do you accept?</h3>
              <p className="text-gray-600">
                We accept all major credit cards (Visa, Mastercard, Amex) via Stripe.
                Enterprise customers can also pay via invoice.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">Do you offer refunds?</h3>
              <p className="text-gray-600">
                Yes! If you're not satisfied within the first 7 days, contact us for a
                full refund, no questions asked.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">Need a custom plan?</h3>
              <p className="text-gray-600">
                Contact us at support@redditsaasvalidator.com for custom enterprise plans
                with higher limits and additional features.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
