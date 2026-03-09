import React, { useState } from 'react';
import axios from '../api';
import { useNavigate } from 'react-router-dom';

const AddPoem: React.FC = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('');
  const [thumbnail, setThumbnail] = useState<File | null>(null);
  const [video, setVideo] = useState<File | null>(null);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      setError('Title and content are required');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('content', content);
      formData.append('category', category);
      
      if (thumbnail) {
        formData.append('thumbnail', thumbnail);
      }
      
      if (video) {
        formData.append('video', video);
      }

      const response = await axios.post('/api/poem', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        navigate('/dashboard');
      } else {
        setError(response.data.message || 'Failed to submit poem');
      }
    } catch (err: any) {
      console.error('Submission error:', err);
      setError(err.response?.data?.message || 'Submission failed');
    } finally {
      setUploading(false);
    }
  };

  const handleThumbnailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }
      // Validate file size (5MB limit)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image file size must be less than 5MB');
        return;
      }
      setThumbnail(file);
      setError('');
    }
  };

  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('video/')) {
        setError('Please select a valid video file');
        return;
      }
      // Validate file size (50MB limit)
      if (file.size > 50 * 1024 * 1024) {
        setError('Video file size must be less than 50MB');
        return;
      }
      setVideo(file);
      setError('');
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
      <h2>Share New Poem</h2>
      {error && <p style={{ color: 'red', marginBottom: 20 }}>{error}</p>}
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 15 }}>
          <label>Title:</label>
          <input
            type="text"
            value={title}
            onChange={e => setTitle(e.target.value)}
            required
            style={{ width: '100%', padding: 8, marginTop: 5 }}
          />
        </div>
        
        <div style={{ marginBottom: 15 }}>
          <label>Content:</label>
          <textarea
            value={content}
            onChange={e => setContent(e.target.value)}
            required
            rows={10}
            style={{ width: '100%', padding: 8, marginTop: 5 }}
            placeholder="Write your poem here..."
          />
        </div>
        
        <div style={{ marginBottom: 15 }}>
          <label>Category:</label>
          <input
            type="text"
            value={category}
            onChange={e => setCategory(e.target.value)}
            placeholder="e.g., love, nature, life"
            style={{ width: '100%', padding: 8, marginTop: 5 }}
          />
        </div>
        
        <div style={{ marginBottom: 15 }}>
          <label>Thumbnail Image (optional):</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleThumbnailChange}
            style={{ marginTop: 5 }}
          />
          {thumbnail && (
            <p style={{ fontSize: '0.9em', color: '#666' }}>
              Selected: {thumbnail.name} ({(thumbnail.size / 1024 / 1024).toFixed(2)} MB)
            </p>
          )}
        </div>
        
        <div style={{ marginBottom: 20 }}>
          <label>Video (optional):</label>
          <input
            type="file"
            accept="video/*"
            onChange={handleVideoChange}
            style={{ marginTop: 5 }}
          />
          {video && (
            <p style={{ fontSize: '0.9em', color: '#666' }}>
              Selected: {video.name} ({(video.size / 1024 / 1024).toFixed(2)} MB)
            </p>
          )}
        </div>
        
        <button 
          type="submit" 
          disabled={uploading}
          style={{ 
            padding: '10px 20px', 
            backgroundColor: uploading ? '#ccc' : '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: 5,
            cursor: uploading ? 'not-allowed' : 'pointer'
          }}
        >
          {uploading ? 'Submitting...' : 'Submit Poem'}
        </button>
      </form>
    </div>
  );
};

export default AddPoem;