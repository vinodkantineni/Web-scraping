import React, { useState } from 'react';
import { Sparkles, Globe, FileText, ArrowRight, ShieldAlert, BadgeInfo } from 'lucide-react';
import BiasChart from '../components/BiasChart';

export default function DashboardPage({ onUnauthorized }) {
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [inputType, setInputType] = useState('url'); // 'url' or 'text'
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);

    const token = localStorage.getItem('token');
    const payload = inputType === 'url' ? { url } : { text };

    try {
      const response = await fetch('/api/analysis/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        if (response.status === 401) {
          if (onUnauthorized) {
            onUnauthorized();
          } else {
            localStorage.removeItem('token');
          }
          throw new Error('Your session has expired or is invalid. Please log in again to continue.');
        }

        if (response.status === 502 || response.status === 503 || response.status === 504) {
          throw new Error('Server timeout or unavailable. Please try again later.');
        }
        
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          throw new Error(`Server error (${response.status}). Please try again later.`);
        }
        throw new Error(errorData.detail || 'Analysis failed. Please verify the URL or text input.');
      }

      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error('Received an invalid or empty response from the server.');
      }

      setResult(data);
    } catch (err) {
      setError(err.message || 'An error occurred during bias analysis.');
    } finally {
      setLoading(false);
    }
  };

  // Determine the dominant bias category based on original scores
  const getDominantBias = (left, center, right) => {
    const maxVal = Math.max(left, center, right);
    if (maxVal === left) return { text: 'Left-Leaning Slant', color: '#ef4444' };
    if (maxVal === right) return { text: 'Right-Leaning Slant', color: '#3b82f6' };
    return { text: 'Relatively Balanced', color: '#10b981' };
  };

  return (
    <div className="container animate-fade-in" style={{ paddingBottom: '80px' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto 40px auto', textAlign: 'center' }}>
        <h2 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>
          Analyze News <span className="gradient-text">Bias & Neutrality</span>
        </h2>
        <p style={{ color: 'var(--text-muted)' }}>
          Enter an article link or paste raw text to isolate media spin, view bias distributions, and generate a neutral version.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: result ? '1fr' : '1fr', // Keep it clean
        gap: '32px',
        maxWidth: '900px',
        margin: '0 auto'
      }}>
        {/* Input Form Panel */}
        <div className="glass-panel" style={{ padding: '32px' }}>
          {/* Input Type Toggler */}
          <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
            <button
              onClick={() => { setInputType('url'); setError(''); }}
              className={`btn ${inputType === 'url' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1, padding: '10px', fontSize: '0.95rem' }}
            >
              <Globe size={18} />
              Analyze Article URL
            </button>
            <button
              onClick={() => { setInputType('text'); setError(''); }}
              className={`btn ${inputType === 'text' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1, padding: '10px', fontSize: '0.95rem' }}
            >
              <FileText size={18} />
              Analyze Raw Text
            </button>
          </div>

          <form onSubmit={handleAnalyze}>
            {inputType === 'url' ? (
              <div style={{ marginBottom: '24px' }}>
                <label htmlFor="article-url">Article URL</label>
                <input
                  id="article-url"
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/news/article-headline"
                  required
                />
              </div>
            ) : (
              <div style={{ marginBottom: '24px' }}>
                <label htmlFor="article-text">Article Text</label>
                <textarea
                  id="article-text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste the full text of the news article here (minimum 150 characters)..."
                  required
                  rows={8}
                  style={{ resize: 'vertical' }}
                />
              </div>
            )}

            {error && (
              <div style={{
                padding: '12px',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.2)',
                color: '#ef4444',
                borderRadius: '8px',
                fontSize: '0.9rem',
                marginBottom: '24px'
              }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ width: '100%', padding: '14px', fontSize: '1.05rem' }}
            >
              {loading ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span className="loading-spinner" style={{ width: '20px', height: '20px' }} />
                  Processing Article & Running Bias Models...
                </div>
              ) : (
                <>
                  Run Analysis & Debiasing
                  <Sparkles size={18} />
                </>
              )}
            </button>
          </form>
        </div>

        {/* Loading Skeleton Mockup */}
        {loading && (
          <div className="glass-panel animate-fade-in" style={{ padding: '32px', textAlign: 'center' }}>
            <LoaderSkeleton />
          </div>
        )}

        {/* Results Panel */}
        {result && (
          <div className="glass-panel animate-fade-in" style={{ padding: '32px' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              flexWrap: 'wrap',
              gap: '16px',
              borderBottom: '1px solid rgba(255,255,255,0.05)',
              paddingBottom: '20px',
              marginBottom: '28px'
            }}>
              <div>
                <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--accent-cyan)', fontWeight: '700', letterSpacing: '1px' }}>
                  Analysis Complete
                </span>
                <h3 style={{ fontSize: '1.6rem', marginTop: '4px', fontWeight: '600' }}>{result.title}</h3>
                {result.url && (
                  <a href={result.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.85rem', color: 'var(--accent-primary)', textDecoration: 'none' }}>
                    View Original Source Link
                  </a>
                )}
              </div>
              
              {/* Bias Badges */}
              <div style={{ display: 'flex', gap: '12px' }}>
                <div style={{
                  padding: '8px 16px',
                  borderRadius: '999px',
                  fontSize: '0.9rem',
                  fontWeight: '600',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  <ShieldAlert size={16} />
                  <span>{getDominantBias(result.original_left, result.original_center, result.original_right).text}</span>
                </div>

                <div style={{
                  padding: '8px 16px',
                  borderRadius: '999px',
                  fontSize: '0.9rem',
                  fontWeight: '700',
                  background: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  color: '#10b981'
                }}>
                  Bias Reduced by {result.bias_reduction}%
                </div>
              </div>
            </div>

            {/* Split Panel: Summary & Debiased Text */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
              gap: '28px',
              marginBottom: '32px'
            }}>
              <div className="glass-card">
                <h4 style={{ marginBottom: '12px', color: 'var(--accent-cyan)', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <BadgeInfo size={16} />
                  Fact-Based Summary
                </h4>
                <p style={{ color: 'var(--text-main)', fontSize: '0.95rem', lineHeight: '1.6' }}>
                  {result.summary}
                </p>
              </div>

              <div className="glass-card" style={{ borderLeft: '3px solid var(--accent-secondary)' }}>
                <h4 style={{ marginBottom: '12px', color: 'var(--accent-secondary)', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Sparkles size={16} />
                  Debiased Objective Text
                </h4>
                <p style={{ color: 'var(--text-main)', fontSize: '0.95rem', lineHeight: '1.6' }}>
                  {result.debiased_text}
                </p>
              </div>
            </div>

            {/* Graph Visualizer */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h4 style={{ marginBottom: '20px', fontWeight: '600', fontSize: '1.1rem' }}>Bias Metric Comparison</h4>
              <BiasChart
                original={{
                  left: result.original_left,
                  center: result.original_center,
                  right: result.original_right
                }}
                debiased={{
                  left: result.debiased_left,
                  center: result.debiased_center,
                  right: result.debiased_right
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function LoaderSkeleton() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', padding: '20px' }}>
      <div style={{ height: '24px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', width: '40%', alignSelf: 'center', animation: 'pulse 1.5s infinite' }} />
      <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
        <div style={{ flex: 1, height: '140px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', animation: 'pulse 1.5s infinite' }} />
        <div style={{ flex: 1, height: '140px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', animation: 'pulse 1.5s infinite' }} />
      </div>
      <div style={{ height: '180px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', animation: 'pulse 1.5s infinite', marginTop: '10px' }} />
      <style>{`
        @keyframes pulse {
          0% { opacity: 0.6; }
          50% { opacity: 0.3; }
          100% { opacity: 0.6; }
        }
      `}</style>
    </div>
  );
}
