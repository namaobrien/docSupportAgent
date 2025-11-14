import { useState } from 'react';
import './IssueTrigger.css';

function IssueTrigger({ onAnalyze }) {
  const [issueNumber, setIssueNumber] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    const num = parseInt(issueNumber);
    if (isNaN(num) || num <= 0) {
      alert('Please enter a valid issue number');
      return;
    }
    
    setLoading(true);
    try {
      await onAnalyze(num);
    } finally {
      setLoading(false);
      setIssueNumber('');
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="issue-trigger">
      <div className="filter-group">
        <label htmlFor="issue-number">Or enter issue number</label>
        <div className="trigger-input-group">
          <input
            id="issue-number"
            type="number"
            value={issueNumber}
            onChange={(e) => setIssueNumber(e.target.value)}
            placeholder="e.g., 1234"
            min="1"
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !issueNumber}
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>
    </form>
  );
}

export default IssueTrigger;

