import React, { useEffect, useState } from 'react';
import axios from '../api';

interface PoemSummary {
  id: number;
  title: string;
  approval_status: string;
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get('/api/dashboard')
      .then(res => setData(res.data))
      .catch(err => {
        console.error(err);
        setError('Failed to load dashboard data');
      });
  }, []);

  if (error) return <div>{error}</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h2>Your Dashboard</h2>
      <p>Total poems: {data.total_poems}</p>
      <p>Pending: {data.pending_poems}</p>
      <p>Rejected: {data.rejected_poems}</p>
      <h3>Your poems</h3>
      {data.poems.map((p: PoemSummary) => (
        <div key={p.id}>
          <a href={`/poem/${p.id}`}>{p.title}</a> - {p.approval_status}
        </div>
      ))}
    </div>
  );
};

export default Dashboard;