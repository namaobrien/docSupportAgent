import './IterationTimeline.css';

function IterationTimeline({ iterations, selectedIteration, onSelectIteration, bestIterationNumber }) {
  return (
    <div className="iteration-timeline">
      {iterations.map((iteration, index) => {
        const isSelected = selectedIteration?.iteration_number === iteration.iteration_number;
        const isBest = iteration.iteration_number === bestIterationNumber;
        const score = iteration.rubric_score?.total_score || 0;
        
        return (
          <div
            key={iteration.id}
            className={`timeline-item ${isSelected ? 'selected' : ''} ${isBest ? 'best' : ''}`}
            onClick={() => onSelectIteration(iteration)}
          >
            <div className="timeline-marker">
              <div className="marker-number">{iteration.iteration_number}</div>
            </div>
            
            <div className="timeline-content">
              <div className="timeline-header">
                <div className="timeline-title">
                  Iteration {iteration.iteration_number}
                  {isBest && <span className="badge badge-success">Best</span>}
                </div>
                <div className="timeline-score">{score.toFixed(2)}</div>
              </div>
              
              {iteration.improvement_focus && (
                <div className="timeline-description">
                  {iteration.improvement_focus}
                </div>
              )}
              
              {iteration.changes_made && iteration.changes_made.length > 0 && (
                <div className="timeline-changes">
                  {iteration.changes_made.slice(0, 2).map((change, idx) => (
                    <div key={idx} className="change-tag">{change}</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default IterationTimeline;

