import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const Profile: React.FC = () => {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    axios.get('http://localhost:5000/api/dashboard', { withCredentials: true })
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h2>Your Profile</h2>
      <p>Bio: {data.user?.bio || 'none'}</p>
      <h3>Your Poems</h3>
      {data.poems.map((p: any) => (
        <div key={p.id}>
          <Link to={`/poem/${p.id}`}>{p.title}</Link> - {p.approval_status}
        </div>
      ))}
    </div>
  );
};

export default Profile;