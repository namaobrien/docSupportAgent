import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchIssues, analyzeIssue } from '../services/api';
import IssueTrigger from './IssueTrigger';
import './IssueBrowser.css';

// Cache configuration
const CACHE_KEY_PREFIX = 'issues_cache_';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

function IssueBrowser() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDays, setSelectedDays] = useState(1);
  const [analyzing, setAnalyzing] = useState({});
  const [cacheStatus, setCacheStatus] = useState('');
  const navigate = useNavigate();
  
  const dayOptions = [
    { label: 'Today', value: 1 },
    { label: 'Yesterday', value: 2 },
    { label: 'Last 7 days', value: 7 },
    { label: 'Last 30 days', value: 30 },
    { label: 'Last 90 days', value: 90 },
  ];
  
  useEffect(() => {
    fetchIssues();
  }, [selectedDays]);
  
  const getCacheKey = (days) => `${CACHE_KEY_PREFIX}${days}`;
  
  const getCachedIssues = (days) => {
    try {
      const cached = localStorage.getItem(getCacheKey(days));
      if (!cached) return null;
      
      const { data, timestamp } = JSON.parse(cached);
      const age = Date.now() - timestamp;
      
      if (age < CACHE_DURATION) {
        return data;
      }
      
      // Cache expired, remove it
      localStorage.removeItem(getCacheKey(days));
      return null;
    } catch (error) {
      console.error('Cache read error:', error);
      return null;
    }
  };
  
  const setCachedIssues = (days, data) => {
    try {
      const cacheData = {
        data,
        timestamp: Date.now()
      };
      localStorage.setItem(getCacheKey(days), JSON.stringify(cacheData));
    } catch (error) {
      console.error('Cache write error:', error);
    }
  };
  
  const fetchIssues = async () => {
    console.log('[IssueBrowser] fetchIssues called with selectedDays:', selectedDays);
    
    // Check cache first
    const cached = getCachedIssues(selectedDays);
    if (cached) {
      console.log('[IssueBrowser] Loading from cache:', cached.length, 'issues');
      setIssues(cached);
      setCacheStatus(`${cached.length} issues (cached)`);
      setTimeout(() => setCacheStatus(''), 2000);
      return;
    }
    
    console.log('[IssueBrowser] No cache found, fetching from API');
    setLoading(true);
    setIssues([]); // Clear existing issues
    setCacheStatus('Searching GitHub...');
    
    try {
      console.log('[IssueBrowser] Calling searchIssues API...');
      const data = await searchIssues(selectedDays);
      console.log('[IssueBrowser] API response:', data);
      const fetchedIssues = data.issues || [];
      console.log('[IssueBrowser] Fetched', fetchedIssues.length, 'issues');
      
      // Display issues progressively for better UX
      if (fetchedIssues.length > 0) {
        const chunkSize = 5;
        for (let i = 0; i < fetchedIssues.length; i += chunkSize) {
          const chunk = fetchedIssues.slice(0, i + chunkSize);
          setIssues(chunk);
          setCacheStatus(`Loading issues... ${chunk.length} of ${fetchedIssues.length}`);
          
          // Small delay to show progressive loading
          if (i + chunkSize < fetchedIssues.length) {
            await new Promise(resolve => setTimeout(resolve, 100));
          }
        }
        
        // Cache the results
        setCachedIssues(selectedDays, fetchedIssues);
        setCacheStatus(`✓ Loaded ${fetchedIssues.length} issues`);
        setTimeout(() => setCacheStatus(''), 3000);
      } else {
        console.log('[IssueBrowser] No issues found');
        setIssues([]);
        setCacheStatus('No issues found');
        setTimeout(() => setCacheStatus(''), 3000);
      }
    } catch (error) {
      console.error('[IssueBrowser] Failed to fetch issues:', error);
      setCacheStatus(`❌ Failed to load issues: ${error.message}`);
      setTimeout(() => setCacheStatus(''), 5000);
    } finally {
      setLoading(false);
      console.log('[IssueBrowser] fetchIssues complete');
    }
  };
  
  const handleAnalyze = async (issueNumber) => {
    console.log('[IssueBrowser] Starting FAST analysis for issue:', issueNumber);
    setAnalyzing(prev => ({ ...prev, [issueNumber]: true }));
    
    try {
      console.log('[IssueBrowser] Calling FAST analyzeIssue API...');
      const result = await analyzeIssue(issueNumber);
      console.log('[IssueBrowser] Analysis complete!', result);
      
      // Navigate to results page with the data
      navigate('/results', { state: { result } });
      
    } catch (error) {
      console.error('[IssueBrowser] Failed analysis:', error);
      alert(`❌ Failed: ${error.message}`);
      setAnalyzing(prev => ({ ...prev, [issueNumber]: false }));
    }
  };
  
  const handleRefresh = () => {
    // Clear cache for current selection and refetch
    localStorage.removeItem(getCacheKey(selectedDays));
    fetchIssues();
  };

  return (
    <div className="issue-browser">
      <div className="browser-header">
        <div>
          <h2>Documentation Issues</h2>
          <p className="subtitle">Search and analyze documentation-related issues</p>
          {cacheStatus && (
            <p className="cache-status">{cacheStatus}</p>
          )}
        </div>
      </div>
      
      <div className="filters-section card">
        <div className="filter-group">
          <label htmlFor="days-select">Time Range</label>
          <select
            id="days-select"
            value={selectedDays}
            onChange={(e) => setSelectedDays(Number(e.target.value))}
            className="days-select"
          >
            {dayOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        
        <button 
          className="btn btn-secondary refresh-btn" 
          onClick={handleRefresh}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : '↻ Refresh'}
        </button>
        
        <IssueTrigger onAnalyze={handleAnalyze} />
      </div>
      
      <div className="issues-grid">
        {issues.length === 0 && !loading ? (
          <div className="empty-state card">
            <p>No documentation issues found in the selected time range.</p>
          </div>
        ) : (
          <>
            {issues.map(issue => (
              <div key={issue.id} className="issue-card card">
                <div className="issue-header">
                  <h3 className="issue-title">
                    <a href={issue.url} target="_blank" rel="noopener noreferrer">
                      #{issue.issue_number}: {issue.title}
                    </a>
                  </h3>
                  <span className={`badge badge-${issue.status === 'open' ? 'success' : 'info'}`}>
                    {issue.status}
                  </span>
                </div>
                
                {issue.labels && issue.labels.length > 0 && (
                  <div className="issue-labels">
                    {issue.labels.map(label => (
                      <span key={label} className="label-tag">{label}</span>
                    ))}
                  </div>
                )}
                
                <div className="issue-actions">
                  <button
                    className="btn btn-primary"
                    onClick={() => handleAnalyze(issue.issue_number)}
                    disabled={analyzing[issue.issue_number]}
                  >
                    {analyzing[issue.issue_number] ? 'Analyzing...' : 'Analyze Issue'}
                  </button>
                </div>
              </div>
            ))}
            
            {loading && (
              <>
                {[...Array(3)].map((_, i) => (
                  <div key={`skeleton-${i}`} className="issue-card card skeleton-card">
                    <div className="skeleton-header">
                      <div className="skeleton-title"></div>
                      <div className="skeleton-badge"></div>
                    </div>
                    <div className="skeleton-labels">
                      <div className="skeleton-label"></div>
                      <div className="skeleton-label"></div>
                    </div>
                    <div className="skeleton-button"></div>
                  </div>
                ))}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default IssueBrowser;

