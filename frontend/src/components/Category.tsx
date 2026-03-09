import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';

interface Poem {
  id: number;
  title: string;
  excerpt: string;
  author: string;
}

const Category: React.FC = () => {
  const { name } = useParams<{ name: string }>();
  const [poems, setPoems] = useState<Poem[]>([]);

  useEffect(() => {
    if (name) {
      axios.get(`http://localhost:5000/api/category/${name}`)
        .then(res => setPoems(res.data.poems))
        .catch(err => console.error(err));
    }
  }, [name]);

  return (
    <div>
      <h2>Category: {name}</h2>
      {poems.map(p => (
        <div key={p.id}>
          <Link to={`/poem/${p.id}`}>{p.title}</Link>
          <p>{p.excerpt}</p>
          <p>By {p.author}</p>
        </div>
      ))}
    </div>
  );
};

export default Category;