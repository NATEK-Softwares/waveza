import React, { useEffect, useState } from 'react';
import axios from '../api';
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

interface Comment {
  id: number;
  content: string;
  timestamp: string;
  user_id: number;
  username: string;
  parent_id: number | null;
  replies: Comment[];
}

interface LikeStatus {
  liked: boolean;
  likes_count: number;
}

const PoemDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [poem, setPoem] = useState<Poem | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [likeStatus, setLikeStatus] = useState<LikeStatus>({ liked: false, likes_count: 0 });
  const [newComment, setNewComment] = useState('');
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [replyContent, setReplyContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadPoemData();
    }
  }, [id]);

  const loadPoemData = async () => {
    try {
      const [poemRes, commentsRes, likesRes] = await Promise.all([
        axios.get(`/api/poem/${id}`),
        axios.get(`/api/poem/${id}/comments`),
        axios.get(`/api/poem/${id}/likes`)
      ]);

      setPoem(poemRes.data.poem);
      setComments(commentsRes.data.comments);
      setLikeStatus(likesRes.data);
    } catch (err) {
      console.error('Error loading poem data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    try {
      const res = await axios.post(`/api/poem/${id}/like`);
      setLikeStatus(res.data);
    } catch (err) {
      console.error('Error toggling like:', err);
    }
  };

  const handleCommentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await axios.post(`/api/poem/${id}/comment`, 
        { content: newComment }
      );
      setNewComment('');
      loadPoemData(); // Reload comments
    } catch (err) {
      console.error('Error adding comment:', err);
    }
  };

  const handleReplySubmit = async (commentId: number) => {
    if (!replyContent.trim()) return;

    try {
      await axios.post(`/api/poem/${id}/comment`, 
        { content: replyContent, parent_id: commentId }
      );
      setReplyTo(null);
      setReplyContent('');
      loadPoemData(); // Reload comments
    } catch (err) {
      console.error('Error adding reply:', err);
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    try {
      await axios.delete(`/api/comment/${commentId}`);
      loadPoemData(); // Reload comments
    } catch (err) {
      console.error('Error deleting comment:', err);
    }
  };

  const renderComments = (comments: Comment[], level = 0): JSX.Element[] => {
    return comments.map(comment => (
      <div key={comment.id} style={{ marginLeft: level * 20, marginBottom: 10 }}>
        <div style={{ border: '1px solid #ddd', padding: 10, borderRadius: 5 }}>
          <strong>{comment.username}</strong> 
          <span style={{ fontSize: '0.8em', color: '#666', marginLeft: 10 }}>
            {new Date(comment.timestamp).toLocaleString()}
          </span>
          <p>{comment.content}</p>
          <div>
            <button onClick={() => setReplyTo(replyTo === comment.id ? null : comment.id)}>
              Reply
            </button>
            {/* Add delete button for comment author - would need user context */}
          </div>
          
          {replyTo === comment.id && (
            <form onSubmit={(e) => { e.preventDefault(); handleReplySubmit(comment.id); }}>
              <textarea
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                placeholder="Write a reply..."
                rows={3}
              />
              <button type="submit">Reply</button>
              <button type="button" onClick={() => setReplyTo(null)}>Cancel</button>
            </form>
          )}
          
          {comment.replies && comment.replies.length > 0 && (
            <div>{renderComments(comment.replies, level + 1)}</div>
          )}
        </div>
      </div>
    ));
  };

  if (loading) return <div>Loading...</div>;
  if (!poem) return <div>Poem not found</div>;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 20 }}>
      <h1>{poem.title}</h1>
      <p>By {poem.author} | Category: {poem.category}</p>
      
      {poem.thumbnail && (
        <img src={`${axios.defaults.baseURL}/${poem.thumbnail}`} alt="Poem thumbnail" style={{ maxWidth: '100%' }} />
      )}
      
      <div dangerouslySetInnerHTML={{ __html: poem.content }} />
      
      {poem.video_url && (
        <video controls style={{ maxWidth: '100%', marginTop: 20 }}>
          <source src={`${axios.defaults.baseURL}/${poem.video_url}`} />
        </video>
      )}
      
      <div style={{ marginTop: 20, padding: 20, border: '1px solid #ddd', borderRadius: 5 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 20 }}>
          <button onClick={handleLike} style={{ fontSize: '1.2em' }}>
            {likeStatus.liked ? '❤️' : '🤍'} {likeStatus.likes_count} Likes
          </button>
          <span>{comments.length} Comments</span>
        </div>
        
        <form onSubmit={handleCommentSubmit}>
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Write a comment..."
            rows={4}
            style={{ width: '100%', marginBottom: 10 }}
          />
          <button type="submit">Post Comment</button>
        </form>
        
        <div style={{ marginTop: 20 }}>
          <h3>Comments</h3>
          {comments.length === 0 ? (
            <p>No comments yet. Be the first to comment!</p>
          ) : (
            renderComments(comments.filter(c => !c.parent_id))
          )}
        </div>
      </div>
    </div>
  );
};

export default PoemDetail;