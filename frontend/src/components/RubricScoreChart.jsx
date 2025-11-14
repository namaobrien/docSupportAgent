import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function RubricScoreChart({ iterations, bestIterationNumber }) {
  // Prepare data for chart
  const chartData = iterations.map(iteration => ({
    iteration: iteration.iteration_number,
    total: iteration.rubric_score?.total_score || 0,
    accuracy: iteration.rubric_score?.accuracy_score || 0,
    clarity: iteration.rubric_score?.clarity_score || 0,
    completeness: iteration.rubric_score?.completeness_score || 0,
    examples: iteration.rubric_score?.examples_score || 0,
    isBest: iteration.iteration_number === bestIterationNumber
  }));
  
  const CustomDot = (props) => {
    const { cx, cy, payload } = props;
    if (payload.isBest) {
      return (
        <circle
          cx={cx}
          cy={cy}
          r={6}
          fill="#d4a27f"
          stroke="#fff"
          strokeWidth={2}
        />
      );
    }
    return null;
  };
  
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
        <XAxis
          dataKey="iteration"
          label={{ value: 'Iteration', position: 'insideBottom', offset: -5 }}
        />
        <YAxis
          label={{ value: 'Score', angle: -90, position: 'insideLeft' }}
          domain={[0, 10]}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #ddd',
            borderRadius: '8px',
            padding: '10px'
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="total"
          stroke="#0e0e0e"
          strokeWidth={3}
          name="Total Score"
          dot={<CustomDot />}
        />
        <Line
          type="monotone"
          dataKey="accuracy"
          stroke="#ef4444"
          strokeWidth={2}
          name="Accuracy"
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="clarity"
          stroke="#3b82f6"
          strokeWidth={2}
          name="Clarity"
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="completeness"
          stroke="#22c55e"
          strokeWidth={2}
          name="Completeness"
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="examples"
          stroke="#eab308"
          strokeWidth={2}
          name="Examples"
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default RubricScoreChart;

