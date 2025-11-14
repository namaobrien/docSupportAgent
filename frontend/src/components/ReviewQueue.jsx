import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getReviewQueue } from '../services/api';
import './ReviewQueue.css';

function ReviewQueue() {
  const [reviewItems, setReviewItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('needs_review');
  const [sortBy, setSortBy] = useState('date');
  const navigate = useNavigate();
  
  useEffect(() => {
    fetchReviewQueue();
  }, [statusFilter, sortBy]);
  
  const fetchReviewQueue = async () => {
    setLoading(true);
    try {
      const data = await getReviewQueue(statusFilter, sortBy);
      setReviewItems(data || []);
    } catch (error) {
      console.error('Failed to fetch review queue:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleViewAnalysis = (analysisId) => {
    navigate(`/analysis/${analysisId}`);
  };
  
  return (
    <div className="review-queue">
      <div className="queue-header">
        <div>
          <h2>Review Queue</h2>
          <p className="subtitle">Issues flagged for human review</p>
        </div>
      </div>
      
      <div className="queue-filters card">
        <div className="filter-group">
          <label htmlFor="status-filter">Status</label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="needs_review">Needs Review</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="sort-by">Sort By</label>
          <select
            id="sort-by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="date">Date</option>
            <option value="score_diff">Score Difference</option>
          </select>
        </div>
      </div>
      
      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading review queue...</p>
        </div>
      ) : reviewItems.length === 0 ? (
        <div className="empty-state card">
          <p>No items in review queue.</p>
        </div>
      ) : (
        <div className="review-items">
          {reviewItems.map(item => (
            <div key={item.id} className="review-item card">
              <div className="review-header">
                <div className="review-reason">
                  <span className="badge badge-warning">{item.reason.replace(/_/g, ' ')}</span>
                  <h3>{item.analysis.issue.title || 'Untitled Issue'}</h3>
                </div>
                <div className="review-meta">
                  <div className="meta-item">
                    <span className="meta-label">Iterations</span>
                    <span className="meta-value">{item.iterations_attempted || 0}</span>
                  </div>
                  {item.original_score !== null && (
                    <div className="meta-item">
                      <span className="meta-label">Original Score</span>
                      <span className="meta-value">{item.original_score.toFixed(2)}</span>
                    </div>
                  )}
                  {item.best_achieved_score !== null && (
                    <div className="meta-item">
                      <span className="meta-label">Best Score</span>
                      <span className="meta-value">{item.best_achieved_score.toFixed(2)}</span>
                    </div>
                  )}
                  {item.original_score !== null && item.best_achieved_score !== null && (
                    <div className="meta-item">
                      <span className="meta-label">Difference</span>
                      <span className={`meta-value ${item.best_achieved_score > item.original_score ? 'positive' : 'negative'}`}>
                        {(item.best_achieved_score - item.original_score).toFixed(2)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              {item.detailed_reason && (
                <div className="review-details">
                  <p>{item.detailed_reason}</p>
                </div>
              )}
              
              <div className="review-actions">
                <button
                  className="btn btn-primary"
                  onClick={() => handleViewAnalysis(item.analysis_id)}
                >
                  View Analysis
                </button>
                <a
                  href={item.analysis.issue?.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                >
                  View Issue
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ReviewQueue;

