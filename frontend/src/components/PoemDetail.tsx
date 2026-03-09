import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

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

const PoemDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [poem, setPoem] = useState<Poem | null>(null);

  useEffect(() => {
    if (id) {
      axios.get(`http://localhost:5000/api/poem/${id}`)
        .then(res => setPoem(res.data.poem))
        .catch(err => console.error(err));
    }
  }, [id]);

  if (!poem) return <div>Loading...</div>;

  return (
    <div>
      <h1>{poem.title}</h1>
      <p>By {poem.author}</p>
      <div dangerouslySetInnerHTML={{ __html: poem.content }} />
    </div>
  );
};

export default PoemDetail;