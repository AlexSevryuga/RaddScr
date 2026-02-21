'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';

export default function Navigation() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  const navItems = [
    { href: '/dashboard', label: 'Projects' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/billing', label: 'Billing' },
  ];

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/dashboard" className="text-xl font-bold text-primary-600">
            Reddit SaaS Validator
          </Link>

          {/* Navigation Items */}
          <div className="flex items-center space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`font-medium transition ${
                  pathname === item.href
                    ? 'text-primary-600'
                    : 'text-gray-600 hover:text-primary-600'
                }`}
              >
                {item.label}
              </Link>
            ))}

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                {user?.email}
              </div>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-600 hover:text-gray-900 font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
