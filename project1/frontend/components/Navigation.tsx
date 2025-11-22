'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { getCurrentUserInfo } from '../lib/api';
import LoginModal from './LoginModal';

export default function Navigation() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, loading, signOut } = useAuth();
  const [userCoins, setUserCoins] = useState<number>(1000); // Default starting coins
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  // Load user coins from localStorage (or API in the future)
  useEffect(() => {
    const storedCoins = localStorage.getItem('userCoins');
    if (storedCoins) {
      setUserCoins(parseInt(storedCoins, 10));
    }
  }, []);

  // Check if user is admin
  useEffect(() => {
    const checkAdmin = async () => {
      if (!user || loading) {
        setIsAdmin(false);
        return;
      }

      try {
        const userInfo = await getCurrentUserInfo();
        setIsAdmin(userInfo?.role === 'admin');
      } catch {
        setIsAdmin(false);
      }
    };

    checkAdmin();
  }, [user, loading]);

  const isActive = (path: string) => pathname === path;

  const handleSignOut = async () => {
    try {
      await signOut();
      router.push('/');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const handleSignIn = () => {
    setIsLoginModalOpen(true);
  };

  const getUserInitials = () => {
    if (!user?.email) return '👤';
    const email = user.email;
    const name = user.user_metadata?.full_name || email.split('@')[0];
    if (name.includes(' ')) {
      return name
        .split(' ')
        .map((n: string) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <>
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
            {isAdmin && (
              <button
                className={`nav-link ${isActive('/manage') ? 'active' : ''}`}
                onClick={() => router.push('/manage')}
                type="button"
              >
                Manage
              </button>
            )}
          </div>

          <div className="nav-right">
            {!loading && (
              <>
                {user ? (
                  <>
                    <div className="coin-balance">
                      <span className="coin-icon">🪙</span>
                      <span className="coin-amount">{userCoins.toLocaleString()}</span>
                    </div>
                    <div className="user-info" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div
                        className="user-avatar"
                        style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          backgroundColor: '#4285f4',
                          color: 'white',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.875rem',
                          fontWeight: '500',
                        }}
                        title={user.email || ''}
                      >
                        {getUserInitials()}
                      </div>
                      <button
                        onClick={handleSignOut}
                        style={{
                          padding: '0.5rem 1rem',
                          backgroundColor: 'transparent',
                          border: '1px solid #ccc',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '0.875rem',
                        }}
                      >
                        Sign Out
                      </button>
                    </div>
                  </>
                ) : (
                  <button
                    onClick={handleSignIn}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: '#4285f4',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                    }}
                  >
                    Sign In
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </nav>
      <LoginModal isOpen={isLoginModalOpen} onClose={() => setIsLoginModalOpen(false)} />
    </>
  );
}

