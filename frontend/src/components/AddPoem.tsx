import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const AddPoem: React.FC = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    axios.post('http://localhost:5000/api/poem', { title, content, category }, { withCredentials: true })
      .then(res => {
        if (res.data.success) {
          navigate('/dashboard');
        } else {
          setError(res.data.message || 'Failed to submit poem');
        }
      })
      .catch(err => {
        console.error(err);
        setError('Submission failed');
      });
  };

  return (
    <div>
      <h2>Share New Poem</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title:</label>
          <input value={title} onChange={e => setTitle(e.target.value)} />
        </div>
        <div>
          <label>Content:</label>
          <textarea value={content} onChange={e => setContent(e.target.value)} />
        </div>
        <div>
          <label>Category:</label>
          <input value={category} onChange={e => setCategory(e.target.value)} />
        </div>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default AddPoem;