import { useLocation, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import './FastResults.css';

function FastResults() {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result;
  
  if (!result) {
    return (
      <div className="error-container card">
        <h2>No Results</h2>
        <p>No analysis results found.</p>
        <button className="btn btn-primary" onClick={() => navigate('/')}>
          Back to Issues
        </button>
      </div>
    );
  }
  
  const { 
    issue_title, 
    issue_url, 
    doc_url,
    original_docs, 
    improved_docs, 
    rubric_scores, 
    total_score,
    explanation,
    time_taken 
  } = result;
  
  return (
    <div className="fast-results">
      <div className="results-header">
        <div>
          <h1>📝 Analysis Results</h1>
          <h2 className="issue-title">
            <a href={issue_url} target="_blank" rel="noopener noreferrer">
              {issue_title}
            </a>
          </h2>
          <div className="doc-link">
            <a href={result.doc_url} target="_blank" rel="noopener noreferrer">
              🔗 View Original Documentation
            </a>
          </div>
        </div>
        <div className="header-stats">
          <div className="stat">
            <div className="stat-value">{total_score}/10</div>
            <div className="stat-label">Total Score</div>
          </div>
          <div className="stat">
            <div className="stat-value">{time_taken}s</div>
            <div className="stat-label">Time Taken</div>
          </div>
        </div>
      </div>
      
      {/* Rubric Scores */}
      <div className="card rubric-section">
        <h3>📊 Quality Rubric</h3>
        <div className="rubric-grid">
          {Object.entries(rubric_scores).map(([key, value]) => (
            <div key={key} className="rubric-item">
              <div className="rubric-label">{key.charAt(0).toUpperCase() + key.slice(1)}</div>
              <div className="rubric-score">{value}/10</div>
              <div className="rubric-bar">
                <div 
                  className="rubric-bar-fill" 
                  style={{ width: `${(value / 10) * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
        {explanation && (
          <div className="explanation">
            <strong>Explanation:</strong> {explanation}
          </div>
        )}
      </div>
      
      {/* Side-by-side comparison */}
      <div className="comparison-section">
        <div className="card comparison-col">
          <h3>📄 Original Documentation</h3>
          <div className="doc-content markdown-content original">
            <ReactMarkdown>{original_docs}</ReactMarkdown>
          </div>
        </div>
        
        <div className="card comparison-col improved">
          <h3>💡 Targeted Recommendation</h3>
          <div className="doc-content markdown-content">
            <ReactMarkdown>{improved_docs}</ReactMarkdown>
          </div>
        </div>
      </div>
      
      <div className="results-footer">
        <button className="btn btn-secondary" onClick={() => navigate('/')}>
          ← Back to Issues
        </button>
      </div>
    </div>
  );
}

export default FastResults;

