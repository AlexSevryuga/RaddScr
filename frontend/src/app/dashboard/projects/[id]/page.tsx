'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { projectsApi } from '@/lib/api';
import type { ProjectWithAnalysis } from '@/types';

export default function ProjectPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = parseInt(params.id as string);

  const [project, setProject] = useState<ProjectWithAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [retrying, setRetrying] = useState(false);

  useEffect(() => {
    loadProject();
    // Poll every 10s if processing
    const interval = setInterval(() => {
      if (project?.status === 'processing' || project?.status === 'pending') {
        loadProject();
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [projectId, project?.status]);

  const loadProject = async () => {
    try {
      const data = await projectsApi.get(projectId);
      setProject(data);
    } catch (err: any) {
      setError('Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    setRetrying(true);
    try {
      await projectsApi.validate(projectId);
      await loadProject();
    } catch (err: any) {
      alert('Failed to retry validation');
    } finally {
      setRetrying(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this project?')) return;

    try {
      await projectsApi.delete(projectId);
      router.push('/dashboard');
    } catch (err: any) {
      alert('Failed to delete project');
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error || 'Project not found'}</p>
        <Link
          href="/dashboard"
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/dashboard"
          className="text-primary-600 hover:text-primary-700 font-medium mb-4 inline-block"
        >
          ← Back to Projects
        </Link>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
            {project.description && (
              <p className="text-gray-600 mt-2">{project.description}</p>
            )}
          </div>
          <button
            onClick={handleDelete}
            className="text-red-600 hover:text-red-700 font-medium"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Status */}
      {project.status === 'pending' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
          <h3 className="font-semibold text-yellow-900 mb-2">⏳ Queued</h3>
          <p className="text-yellow-800">
            Your validation has been queued and will start shortly...
          </p>
        </div>
      )}

      {project.status === 'processing' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h3 className="font-semibold text-blue-900 mb-2">
            🔄 Processing
          </h3>
          <p className="text-blue-800">
            We're analyzing Reddit, Twitter, and LinkedIn. This usually takes 2-5 minutes...
          </p>
          <div className="mt-4">
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full animate-pulse w-2/3"></div>
            </div>
          </div>
        </div>
      )}

      {project.status === 'failed' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
          <h3 className="font-semibold text-red-900 mb-2">❌ Failed</h3>
          <p className="text-red-800 mb-4">
            Validation failed. This could be due to API limits or temporary issues.
          </p>
          <button
            onClick={handleRetry}
            disabled={retrying}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {retrying ? 'Retrying...' : 'Retry Validation'}
          </button>
        </div>
      )}

      {/* Results */}
      {project.status === 'completed' && project.analysis && (
        <div className="space-y-6">
          {/* Score Card */}
          <div className={`${getScoreBg(project.analysis.overall_score || 0)} rounded-lg p-8 text-center`}>
            <div className="text-6xl font-bold mb-2 ${getScoreColor(project.analysis.overall_score || 0)}">
              {project.analysis.overall_score}/100
            </div>
            <div className="text-2xl font-semibold text-gray-900">
              {project.analysis.verdict}
            </div>
          </div>

          {/* Key Insights */}
          {project.analysis.key_insights && project.analysis.key_insights.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                🔍 Key Insights
              </h2>
              <ul className="space-y-3">
                {project.analysis.key_insights.map((insight, idx) => (
                  <li key={idx} className="flex gap-3">
                    <span className="text-primary-600 font-bold">•</span>
                    <span className="text-gray-700">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {project.analysis.recommendations && project.analysis.recommendations.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                💡 Recommendations
              </h2>
              <ul className="space-y-3">
                {project.analysis.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex gap-3">
                    <span className="text-green-600 font-bold">✓</span>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Platform Data */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* Reddit */}
            {project.analysis.reddit_data && !project.analysis.reddit_data.error && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="font-bold text-lg mb-2">🔴 Reddit</h3>
                <div className="text-3xl font-bold text-primary-600 mb-2">
                  {project.analysis.reddit_data.score || 0}/100
                </div>
                <p className="text-sm text-gray-600">
                  {project.analysis.reddit_data.summary || 'No data'}
                </p>
              </div>
            )}

            {/* Twitter */}
            {project.analysis.twitter_data && !project.analysis.twitter_data.error && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="font-bold text-lg mb-2">🐦 Twitter</h3>
                <div className="text-3xl font-bold text-primary-600 mb-2">
                  {project.analysis.twitter_data.score || 0}/100
                </div>
                <p className="text-sm text-gray-600">
                  {project.analysis.twitter_data.summary || 'No data'}
                </p>
              </div>
            )}

            {/* LinkedIn */}
            {project.analysis.linkedin_data && !project.analysis.linkedin_data.error && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="font-bold text-lg mb-2">💼 LinkedIn</h3>
                <div className="text-3xl font-bold text-primary-600 mb-2">
                  {project.analysis.linkedin_data.score || 0}/100
                </div>
                <p className="text-sm text-gray-600">
                  {project.analysis.linkedin_data.summary || 'No data'}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Keywords */}
      {project.keywords && project.keywords.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6 mt-6">
          <h3 className="font-bold text-lg mb-3">Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {project.keywords.map((keyword, idx) => (
              <span
                key={idx}
                className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
