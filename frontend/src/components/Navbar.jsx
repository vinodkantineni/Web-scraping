import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LogOut, History, LayoutDashboard, ShieldAlert } from 'lucide-react';

export default function Navbar({ user, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();

  if (!user) return null;

  return (
    <nav className="glass-panel animate-fade-in" style={{
      margin: '24px auto',
      maxWidth: '1200px',
      padding: '16px 24px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      position: 'sticky',
      top: '20px',
      zIndex: 100
    }}>
      <Link to="/dashboard" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <ShieldAlert className="gradient-text" size={28} style={{ color: '#a855f7' }} />
        <span style={{ fontSize: '1.4rem', fontWeight: '700', letterSpacing: '-0.5px' }}>
          Bias<span className="gradient-text">Digest</span>
        </span>
      </Link>

      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        <Link 
          to="/dashboard" 
          className="btn btn-secondary" 
          style={{
            padding: '8px 16px',
            fontSize: '0.9rem',
            border: 'none',
            background: location.pathname === '/dashboard' ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
            color: location.pathname === '/dashboard' ? 'var(--accent-primary)' : 'var(--text-main)'
          }}
        >
          <LayoutDashboard size={18} />
          Dashboard
        </Link>
        
        <Link 
          to="/history" 
          className="btn btn-secondary"
          style={{
            padding: '8px 16px',
            fontSize: '0.9rem',
            border: 'none',
            background: location.pathname === '/history' ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
            color: location.pathname === '/history' ? 'var(--accent-primary)' : 'var(--text-main)'
          }}
        >
          <History size={18} />
          History
        </Link>

        <div style={{ width: '1px', height: '24px', background: 'rgba(255,255,255,0.1)' }} />

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            Hi, <strong style={{ color: 'var(--text-main)' }}>{user.username}</strong>
          </span>
          <button 
            onClick={() => {
              onLogout();
              navigate('/');
            }}
            className="btn btn-danger"
            style={{ padding: '8px 12px', fontSize: '0.9rem' }}
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
