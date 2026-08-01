import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Sparkles, MessageSquare, ArrowRight, BarChart } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="container animate-fade-in" style={{ padding: '80px 24px', textAlign: 'center' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ 
          display: 'inline-flex', 
          alignItems: 'center', 
          gap: '8px', 
          padding: '8px 16px', 
          background: 'rgba(168, 85, 247, 0.1)', 
          border: '1px solid rgba(168, 85, 247, 0.2)',
          borderRadius: '999px',
          marginBottom: '24px',
          fontSize: '0.9rem',
          fontWeight: '600',
          color: 'var(--accent-secondary)'
        }}>
          <Sparkles size={14} /> Production-Grade Media Intelligence
        </div>

        <h1 style={{ fontSize: '3.5rem', marginBottom: '16px', lineHeight: '1.1' }}>
          Personalized News Digest with <span className="gradient-text">Bias Detection</span>
        </h1>
        
        <p style={{ 
          fontSize: '1.25rem', 
          color: 'var(--text-muted)', 
          marginBottom: '40px',
          lineHeight: '1.6'
        }}>
          Combat information overload, isolate media slants, and extract objective facts instantly. Our system analyzes article bias and reconstructs neutral coverage side-by-side.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginBottom: '80px' }}>
          <Link to="/auth" className="btn btn-primary" style={{ fontSize: '1.1rem', padding: '14px 32px' }}>
            Get Started Free
            <ArrowRight size={18} />
          </Link>
          <a href="https://github.com/vinodkantineni/Web-scraping" target="_blank" rel="noopener noreferrer" className="btn btn-secondary" style={{ fontSize: '1.1rem', padding: '14px 32px' }}>
            View GitHub Documentation
          </a>
        </div>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: '24px',
        textAlign: 'left',
        marginTop: '40px'
      }}>
        <div className="glass-panel" style={{ padding: '32px' }}>
          <div style={{ 
            background: 'rgba(99, 102, 241, 0.1)', 
            width: '48px', 
            height: '48px', 
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '20px',
            color: 'var(--accent-primary)'
          }}>
            <Shield size={24} />
          </div>
          <h3 style={{ marginBottom: '12px', fontWeight: '600' }}>Bias Detection</h3>
          <p style={{ color: 'var(--text-muted)', lineHeight: '1.5' }}>
            Scans news text using zero-shot AI classification to estimate leanings along the Left, Center, and Right spectrum.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '32px' }}>
          <div style={{ 
            background: 'rgba(168, 85, 247, 0.1)', 
            width: '48px', 
            height: '48px', 
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '20px',
            color: 'var(--accent-secondary)'
          }}>
            <Sparkles size={24} />
          </div>
          <h3 style={{ marginBottom: '12px', fontWeight: '600' }}>Neutral Debiasing</h3>
          <p style={{ color: 'var(--text-muted)', lineHeight: '1.5' }}>
            Rewrites slanted coverage to compile a factual, objective, and neutral article free of political framing.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '32px' }}>
          <div style={{ 
            background: 'rgba(6, 182, 212, 0.1)', 
            width: '48px', 
            height: '48px', 
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '20px',
            color: 'var(--accent-cyan)'
          }}>
            <BarChart size={24} />
          </div>
          <h3 style={{ marginBottom: '12px', fontWeight: '600' }}>Personal History</h3>
          <p style={{ color: 'var(--text-muted)', lineHeight: '1.5' }}>
            Store your news research directly to a secure SQLite database. Retrieve past bias reports and digests on demand.
          </p>
        </div>
      </div>
    </div>
  );
}
