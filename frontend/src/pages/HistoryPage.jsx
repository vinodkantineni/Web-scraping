import React, { useState, useEffect } from 'react';
import { Trash2, Calendar, ChevronDown, ChevronUp, Link2, AlertTriangle, ShieldCheck } from 'lucide-react';
import BiasChart from '../components/BiasChart';

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    setError('');
    const token = localStorage.getItem('token');

    try {
      const response = await fetch('/api/analysis/history', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load search history.');
      }

      const data = await response.json();
      setHistory(data);
    } catch (err) {
      setError(err.message || 'Error fetching search history.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation(); // Avoid expanding/collapsing card on delete click
    if (!window.confirm('Are you sure you want to delete this analysis record?')) return;

    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`/api/analysis/history/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete history item.');
      }

      // Remove from state
      setHistory(history.filter(item => item.id !== id));
      if (expandedId === id) setExpandedId(null);
    } catch (err) {
      alert(err.message);
    }
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const getDominantBiasText = (left, center, right) => {
    const maxVal = Math.max(left, center, right);
    if (maxVal === left) return 'Left-Leaning';
    if (maxVal === right) return 'Right-Leaning';
    return 'Balanced';
  };

  return (
    <div className="container animate-fade-in" style={{ paddingBottom: '80px', maxWidth: '900px' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h2 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>
          Your Analysis <span className="gradient-text">Search History</span>
        </h2>
        <p style={{ color: 'var(--text-muted)' }}>
          Review, compare, and manage your previously analyzed and debiased news articles.
        </p>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <span className="loading-spinner" style={{ width: '40px', height: '40px' }} />
        </div>
      ) : error ? (
        <div style={{
          padding: '16px',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.2)',
          color: '#ef4444',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          {error}
        </div>
      ) : history.length === 0 ? (
        <div className="glass-panel" style={{ padding: '48px', textAlign: 'center' }}>
          <ShieldCheck size={48} style={{ color: 'var(--accent-primary)', marginBottom: '16px', opacity: 0.7 }} />
          <h3 style={{ marginBottom: '8px' }}>No History Records Found</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
            You haven't run any article bias scans yet. Head over to the dashboard to begin!
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {history.map((item) => {
            const isExpanded = expandedId === item.id;
            return (
              <div 
                key={item.id} 
                className="glass-panel"
                onClick={() => setExpandedId(isExpanded ? null : item.id)}
                style={{ 
                  padding: '24px', 
                  cursor: 'pointer',
                  borderLeft: isExpanded ? '3px solid var(--accent-primary)' : '1px solid rgba(255,255,255,0.05)'
                }}
              >
                {/* Header Row */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '12px'
                }}>
                  <div style={{ flex: 1, minWidth: '280px' }}>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: '600', marginBottom: '6px' }}>{item.title}</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Calendar size={14} />
                        {formatDate(item.created_at)}
                      </span>
                      {item.url && (
                        <a 
                          href={item.url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          onClick={(e) => e.stopPropagation()} // Stop expansion
                          style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-primary)', textDecoration: 'none' }}
                        >
                          <Link2 size={14} />
                          Source Link
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Summary Badges and Controls */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <span style={{
                      padding: '4px 10px',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      fontWeight: '600',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.08)'
                    }}>
                      {getDominantBiasText(item.original_left, item.original_center, item.original_right)}
                    </span>
                    <span style={{
                      padding: '4px 10px',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      fontWeight: '700',
                      background: 'rgba(16, 185, 129, 0.1)',
                      color: '#10b981'
                    }}>
                      -{item.bias_reduction}% Bias
                    </span>
                    <button 
                      onClick={(e) => handleDelete(e, item.id)}
                      className="btn btn-danger"
                      style={{ padding: '8px', borderRadius: '6px' }}
                      title="Delete Record"
                    >
                      <Trash2 size={16} />
                    </button>
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div 
                    onClick={(e) => e.stopPropagation()} // Disable toggle on clicking details
                    style={{
                      marginTop: '24px',
                      paddingTop: '20px',
                      borderTop: '1px solid rgba(255,255,255,0.05)',
                      cursor: 'default'
                    }}
                  >
                    {/* Summary & Debiased Columns */}
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                      gap: '20px',
                      marginBottom: '24px'
                    }}>
                      <div className="glass-card" style={{ padding: '16px' }}>
                        <h4 style={{ color: 'var(--accent-cyan)', fontSize: '0.95rem', marginBottom: '8px', fontWeight: '600' }}>
                          Fact Summary
                        </h4>
                        <p style={{ fontSize: '0.9rem', lineHeight: '1.5', color: 'var(--text-main)' }}>{item.summary}</p>
                      </div>

                      <div className="glass-card" style={{ padding: '16px', borderLeft: '2px solid var(--accent-secondary)' }}>
                        <h4 style={{ color: 'var(--accent-secondary)', fontSize: '0.95rem', marginBottom: '8px', fontWeight: '600' }}>
                          Debiased Rewrite
                        </h4>
                        <p style={{ fontSize: '0.9rem', lineHeight: '1.5', color: 'var(--text-main)' }}>{item.debiased_text}</p>
                      </div>
                    </div>

                    {/* Chart Comparison */}
                    <div className="glass-card" style={{ padding: '20px' }}>
                      <h4 style={{ fontSize: '0.95rem', marginBottom: '16px', fontWeight: '600' }}>Bias Scores Detail</h4>
                      <BiasChart 
                        original={{
                          left: item.original_left,
                          center: item.original_center,
                          right: item.original_right
                        }}
                        debiased={{
                          left: item.debiased_left,
                          center: item.debiased_center,
                          right: item.debiased_right
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
