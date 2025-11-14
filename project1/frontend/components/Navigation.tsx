'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function Navigation() {
  const router = useRouter();
  const pathname = usePathname();
  const [userCoins, setUserCoins] = useState<number>(1000); // Default starting coins

  // Load user coins from localStorage (or API in the future)
  useEffect(() => {
    const storedCoins = localStorage.getItem('userCoins');
    if (storedCoins) {
      setUserCoins(parseInt(storedCoins, 10));
    }
  }, []);

  const isActive = (path: string) => pathname === path;

  return (
    <nav className="top-navigation">
      <div className="nav-container">
        <div className="nav-left">
          <button
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
            onClick={() => router.push('/')}
            type="button"
          >
            Graph
          </button>
          <button
            className={`nav-link ${isActive('/add') ? 'active' : ''}`}
            onClick={() => router.push('/add')}
            type="button"
          >
            Add Data
          </button>
        </div>

        <div className="nav-right">
          <div className="coin-balance">
            <span className="coin-icon">🪙</span>
            <span className="coin-amount">{userCoins.toLocaleString()}</span>
          </div>
          <div className="user-avatar">
            <span className="avatar-icon">👤</span>
          </div>
        </div>
      </div>
    </nav>
  );
}

