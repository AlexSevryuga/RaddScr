'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { projectsApi } from '@/lib/api';
import type { Project } from '@/types';

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await projectsApi.list();
      setProjects(data);
    } catch (err: any) {
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };

    return (
      <span
        className={`px-3 py-1 rounded-full text-sm font-medium ${
          styles[status as keyof typeof styles] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {status.charAt(0).toUpperCase() + status.slice(1)}
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
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-600 mt-2">
            Manage and track your SaaS validation projects
          </p>
        </div>
        <Link
          href="/dashboard/new"
          className="bg-primary-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary-700 transition"
        >
          + New Project
        </Link>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Projects List */}
      {projects.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <div className="text-6xl mb-4">🚀</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            No projects yet
          </h2>
          <p className="text-gray-600 mb-6">
            Create your first project to start validating your SaaS idea
          </p>
          <Link
            href="/dashboard/new"
            className="inline-block bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition"
          >
            Create First Project
          </Link>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              href={`/dashboard/projects/${project.id}`}
              className="bg-white rounded-lg shadow-sm hover:shadow-md transition p-6 block"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-900 flex-1">
                  {project.name}
                </h3>
                {getStatusBadge(project.status)}
              </div>

              {project.description && (
                <p className="text-gray-600 mb-4 line-clamp-2">
                  {project.description}
                </p>
              )}

              {project.keywords && project.keywords.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {project.keywords.slice(0, 3).map((keyword, idx) => (
                    <span
                      key={idx}
                      className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm"
                    >
                      {keyword}
                    </span>
                  ))}
                  {project.keywords.length > 3 && (
                    <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">
                      +{project.keywords.length - 3} more
                    </span>
                  )}
                </div>
              )}

              <div className="text-sm text-gray-500">
                Created {new Date(project.created_at).toLocaleDateString()}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
