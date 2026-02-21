'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { projectsApi } from '@/lib/api';

export default function NewProjectPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [keywordsInput, setKeywordsInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Parse keywords
      const keywords = keywordsInput
        .split(',')
        .map((k) => k.trim())
        .filter((k) => k.length > 0);

      const project = await projectsApi.create({
        name,
        description: description || undefined,
        keywords: keywords.length > 0 ? keywords : undefined,
      });

      // Redirect to project page
      router.push(`/dashboard/projects/${project.id}`);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Failed to create project. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <Link
          href="/dashboard"
          className="text-primary-600 hover:text-primary-700 font-medium mb-4 inline-block"
        >
          ← Back to Projects
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Create New Project</h1>
        <p className="text-gray-600 mt-2">
          Tell us about your SaaS idea and we'll validate it across multiple platforms
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Project Name */}
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Project Name *
            </label>
            <input
              id="name"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
              placeholder="AI-powered email assistant"
            />
            <p className="mt-1 text-sm text-gray-500">
              A clear, descriptive name for your SaaS idea
            </p>
          </div>

          {/* Description */}
          <div>
            <label
              htmlFor="description"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Description
            </label>
            <textarea
              id="description"
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
              placeholder="A tool that helps busy professionals manage their inbox using AI. It automatically categorizes emails, suggests responses, and prioritizes important messages."
            />
            <p className="mt-1 text-sm text-gray-500">
              Describe what your SaaS does and who it's for
            </p>
          </div>

          {/* Keywords */}
          <div>
            <label
              htmlFor="keywords"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Keywords
            </label>
            <input
              id="keywords"
              type="text"
              value={keywordsInput}
              onChange={(e) => setKeywordsInput(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
              placeholder="email management, AI assistant, productivity, inbox zero"
            />
            <p className="mt-1 text-sm text-gray-500">
              Comma-separated keywords related to your idea
            </p>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex gap-3">
              <div className="text-2xl">💡</div>
              <div>
                <h3 className="font-semibold text-blue-900 mb-1">
                  What happens next?
                </h3>
                <p className="text-sm text-blue-800">
                  We'll analyze Reddit, Twitter, and LinkedIn to find discussions about your keywords,
                  identify pain points, and evaluate market demand. You'll get a detailed report with
                  scores and recommendations in a few minutes.
                </p>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create & Start Validation'}
            </button>
            <Link
              href="/dashboard"
              className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition"
            >
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
