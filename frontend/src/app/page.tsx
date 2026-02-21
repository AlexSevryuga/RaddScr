'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex justify-between items-center">
          <div className="text-2xl font-bold text-primary-600">
            Reddit SaaS Validator
          </div>
          <div className="space-x-4">
            <Link
              href="/login"
              className="text-gray-700 hover:text-primary-600 font-medium"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition"
            >
              Get Started
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
          Validate Your SaaS Ideas
          <br />
          <span className="text-primary-600">Before You Build</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Get real market insights from Reddit, Twitter, and LinkedIn. Know if your idea has demand before spending months building it.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/register"
            className="bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700 transition"
          >
            Start Validating
          </Link>
          <Link
            href="/pricing"
            className="bg-white text-primary-600 px-8 py-4 rounded-lg text-lg font-semibold border-2 border-primary-600 hover:bg-primary-50 transition"
          >
            View Pricing
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <div className="grid md:grid-3 gap-8 max-w-5xl mx-auto">
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">🔍</div>
            <h3 className="text-xl font-bold mb-2">Reddit Analysis</h3>
            <p className="text-gray-600">
              Scan relevant subreddits to find pain points and validate demand
            </p>
          </div>
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">🐦</div>
            <h3 className="text-xl font-bold mb-2">Twitter Insights</h3>
            <p className="text-gray-600">
              Analyze tweets to understand market sentiment and trends
            </p>
          </div>
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="text-4xl mb-4">💼</div>
            <h3 className="text-xl font-bold mb-2">LinkedIn B2B</h3>
            <p className="text-gray-600">
              Evaluate B2B potential and enterprise readiness
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-white py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="max-w-3xl mx-auto space-y-8">
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">Describe Your Idea</h3>
                <p className="text-gray-600">
                  Enter your SaaS idea and relevant keywords
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">We Analyze</h3>
                <p className="text-gray-600">
                  Our AI scans Reddit, Twitter, and LinkedIn for market signals
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">Get Insights</h3>
                <p className="text-gray-600">
                  Receive a detailed report with scores, insights, and recommendations
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to Validate Your Idea?</h2>
        <p className="text-xl text-gray-600 mb-8">
          Join hundreds of founders who validated before building
        </p>
        <Link
          href="/register"
          className="bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700 transition inline-block"
        >
          Get Started Free
        </Link>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2026 Reddit SaaS Validator. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
