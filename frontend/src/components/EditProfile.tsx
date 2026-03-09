import React, { useEffect, useState } from 'react';
import axios from '../api';
import { useNavigate } from 'react-router-dom';

const EditProfile: React.FC = () => {
  const [bio, setBio] = useState('');
  const [categories, setCategories] = useState<string[]>([]);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // fetch current profile data
    axios.get('/api/dashboard')
      .then(res => {
        // using dashboard endpoint as an example; ideally create /api/user
        // we only care about bio here
        // no bio returned currently; skip
      })
      .catch(err => console.error(err));
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    axios.post('/api/edit_profile', { bio, categories })
      .then(res => {
        if (res.data.success) {
          navigate('/profile');
        } else {
          setMessage(res.data.message || 'Update failed');
        }
      })
      .catch(err => {
        console.error(err);
        setMessage('Update failed');
      });
  };

  return (
    <div>
      <h2>Edit Profile</h2>
      {message && <p>{message}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Bio:</label>
          <textarea value={bio} onChange={e => setBio(e.target.value)} />
        </div>
        <div>
          <label>Categories (comma-separated):</label>
          <input value={categories.join(',')} onChange={e => setCategories(e.target.value.split(','))} />
        </div>
        <button type="submit">Save</button>
      </form>
    </div>
  );
};

export default EditProfile;