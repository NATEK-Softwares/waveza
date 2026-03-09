import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

interface Poem {
  id: number;
  title: string;
  content: string;
  timestamp: string;
  category: string;
  excerpt: string;
  thumbnail: string;
  video_url: string;
  slug: string;
  approval_status: string;
  author: string;
  likes_count: number;
  comments_count: number;
}

const Home: React.FC = () => {
  const [poems, setPoems] = useState<Poem[]>([]);
  const [categories, setCategories] = useState<Array<[string, number]>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:5000/api/')
      .then(response => {
        setPoems(response.data.poems);
        setCategories(response.data.categories || []);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching poems:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>WaveZA - Poems</h1>
      <h3>Categories</h3>
      <ul>
        {categories.map(([name, count]) => (
          <li key={name}><Link to={`/category/${name}`}>{name} ({count})</Link></li>
        ))}
      </ul>
      {poems.map(poem => (
        <div key={poem.id}>
          <h2><Link to={`/poem/${poem.id}`}>{poem.title}</Link></h2>
          <p>{poem.excerpt}</p>
          <p>By {poem.author}</p>
        </div>
      ))}
    </div>
  );
};

export default Home;