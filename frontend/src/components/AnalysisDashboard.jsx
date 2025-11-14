import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getAnalysis } from '../services/api';
import RubricScoreChart from './RubricScoreChart';
import IterationTimeline from './IterationTimeline';
import './AnalysisDashboard.css';

function AnalysisDashboard() {
  const { analysisId } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedIteration, setSelectedIteration] = useState(null);
  const [polling, setPolling] = useState(true);
  
  useEffect(() => {
    fetchAnalysis();
  }, [analysisId]);
  
  useEffect(() => {
    if (!polling) return;
    
    const interval = setInterval(() => {
      if (analysis?.analysis.status === 'processing') {
        fetchAnalysis(true);
      } else {
        setPolling(false);
      }
    }, 3000);
    
    return () => clearInterval(interval);
  }, [polling, analysis]);
  
  const fetchAnalysis = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const data = await getAnalysis(analysisId);
      
      // Check if response indicates still processing (202 response returns detail message)
      if (data.detail && data.detail.includes('processing')) {
        console.log('[AnalysisDashboard] Analysis still processing, will retry in 3s');
        setAnalysis({
          analysis: {
            status: 'processing',
            total_iterations: 0,
            is_doc_issue: true
          },
          issue: {
            issue_number: analysisId.split('-')[0] || '?',
            title: 'Loading issue details...'
          }
        });
        setLoading(false);
        setTimeout(() => fetchAnalysis(true), 3000);
        return;
      }
      
      // Normal analysis data received
      setAnalysis(data);
      setLoading(false);
      
      if (data.analysis.status !== 'processing') {
        setPolling(false);
      }
      
      // Select best iteration by default
      if (data.analysis.best_iteration_number && !selectedIteration) {
        const bestIter = data.analysis.iterations.find(
          it => it.iteration_number === data.analysis.best_iteration_number
        );
        setSelectedIteration(bestIter);
      }
    } catch (error) {
      console.error('Failed to fetch analysis:', error);
      setLoading(false);
      setPolling(false);
    }
  };
  
  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading analysis...</p>
      </div>
    );
  }
  
  if (!analysis) {
    return (
      <div className="error-container card">
        <h2>Analysis not found</h2>
        <p>The requested analysis could not be found.</p>
      </div>
    );
  }
  
  const { analysis: analysisData, issue, flagged_for_review, review_reason } = analysis;
  
  if (analysisData.status === 'processing') {
    return (
      <div className="processing-container">
        <div className="card">
          <div className="spinner"></div>
          <h2>🤖 Analysis in Progress</h2>
          <p className="processing-title">Issue #{issue.issue_number}: {issue.title}</p>
          <div className="processing-status">
            <p>✓ Issue classified as documentation-related</p>
            <p>✓ Found relevant documentation</p>
            <p>✓ Evaluated original documentation</p>
            <p className="current">⏳ Rewriting and improving documentation...</p>
            <p className="text-muted">
              Iteration {analysisData.total_iterations} of 1 • Should complete in ~10-15 seconds
            </p>
          </div>
          <div className="processing-tip">
            <strong>💡 Tip:</strong> The agent is running in the background. This page will auto-refresh!
          </div>
        </div>
      </div>
    );
  }
  
  if (!analysisData.is_doc_issue) {
    return (
      <div className="not-doc-issue card">
        <h2>Not a Documentation Issue</h2>
        <p>This issue was classified as not being documentation-related.</p>
        <div className="issue-link">
          <a href={issue.url} target="_blank" rel="noopener noreferrer">
            View issue on GitHub →
          </a>
        </div>
      </div>
    );
  }
  
  const iterations = analysisData.iterations || [];
  const bestIteration = iterations.find(
    it => it.iteration_number === analysisData.best_iteration_number
  );
  
  return (
    <div className="analysis-dashboard">
      <div className="dashboard-header">
        <div>
          <h2>Analysis Results</h2>
          <h3 className="issue-title">
            <a href={issue.url} target="_blank" rel="noopener noreferrer">
              #{issue.issue_number}: {issue.title}
            </a>
          </h3>
        </div>
        
        {flagged_for_review && (
          <div className="alert alert-warning">
            <strong>Flagged for Human Review</strong>
            <p>{review_reason}</p>
          </div>
        )}
      </div>
      
      <div className="info-cards">
        <div className="card info-card">
          <div className="info-label">Gap Type</div>
          <div className="info-value">{analysisData.gap_type || 'N/A'}</div>
        </div>
        
        <div className="card info-card">
          <div className="info-label">Total Iterations</div>
          <div className="info-value">{analysisData.total_iterations}</div>
        </div>
        
        <div className="card info-card">
          <div className="info-label">Best Iteration</div>
          <div className="info-value">#{analysisData.best_iteration_number || 'N/A'}</div>
        </div>
        
        <div className="card info-card">
          <div className="info-label">Verification</div>
          <div className="info-value">
            {(analysisData.verification_confidence * 100).toFixed(0)}%
          </div>
        </div>
      </div>
      
      {analysisData.doc_url && (
        <div className="card doc-link-card">
          <strong>Documentation:</strong>{' '}
          <a href={analysisData.doc_url} target="_blank" rel="noopener noreferrer">
            {analysisData.doc_url}
          </a>
        </div>
      )}
      
      {iterations.length > 0 && (
        <>
          <div className="card">
            <h3>Score Progression</h3>
            <RubricScoreChart iterations={iterations} bestIterationNumber={analysisData.best_iteration_number} />
          </div>
          
          <div className="card">
            <h3>Iterations Timeline</h3>
            <IterationTimeline
              iterations={iterations}
              selectedIteration={selectedIteration}
              onSelectIteration={setSelectedIteration}
              bestIterationNumber={analysisData.best_iteration_number}
            />
          </div>
          
          {selectedIteration && (
            <div className="iteration-details">
              <div className="card">
                <div className="iteration-header">
                  <h3>
                    Iteration #{selectedIteration.iteration_number}
                    {selectedIteration.iteration_number === analysisData.best_iteration_number && (
                      <span className="badge badge-success">Best</span>
                    )}
                  </h3>
                  {selectedIteration.rubric_score && (
                    <div className="total-score">
                      Score: {selectedIteration.rubric_score.total_score.toFixed(2)} / 10
                    </div>
                  )}
                </div>
                
                {selectedIteration.improvement_focus && (
                  <div className="improvement-focus">
                    <strong>Focus:</strong> {selectedIteration.improvement_focus}
                  </div>
                )}
                
                {selectedIteration.rubric_score && (
                  <div className="rubric-details">
                    <h4>Rubric Scores</h4>
                    <div className="score-grid">
                      <div className="score-item">
                        <span className="score-label">Accuracy</span>
                        <span className="score-value">
                          {selectedIteration.rubric_score.accuracy_score.toFixed(1)}
                        </span>
                      </div>
                      <div className="score-item">
                        <span className="score-label">Clarity</span>
                        <span className="score-value">
                          {selectedIteration.rubric_score.clarity_score.toFixed(1)}
                        </span>
                      </div>
                      <div className="score-item">
                        <span className="score-label">Completeness</span>
                        <span className="score-value">
                          {selectedIteration.rubric_score.completeness_score.toFixed(1)}
                        </span>
                      </div>
                      <div className="score-item">
                        <span className="score-label">Examples</span>
                        <span className="score-value">
                          {selectedIteration.rubric_score.examples_score.toFixed(1)}
                        </span>
                      </div>
                      <div className="score-item">
                        <span className="score-label">Structure</span>
                        <span className="score-value">
                          {selectedIteration.rubric_score.structure_score.toFixed(1)}
                        </span>
                      </div>
                      <div className="score-item">
                        <span className="score-label">Discoverability</span>
                        <span className="score-value">
                          {selectedIteration.rubric_score.discoverability_score.toFixed(1)}
                        </span>
                      </div>
                    </div>
                    
                    {selectedIteration.rubric_score.feedback && (
                      <div className="feedback-section">
                        <h4>Detailed Feedback</h4>
                        {Object.entries(selectedIteration.rubric_score.feedback).map(([key, value]) => (
                          <div key={key} className="feedback-item">
                            <strong>{key}:</strong> {value}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                
                <div className="rewritten-content">
                  <h4>Rewritten Documentation</h4>
                  <pre className="content-preview">{selectedIteration.rewritten_content}</pre>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default AnalysisDashboard;

