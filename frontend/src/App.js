import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState({ rating: '', comment: '' });
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  useEffect(() => {
    const starsContainer = document.querySelector('.stars');
    if (starsContainer) {
      for (let i = 0; i < 200; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.width = Math.random() * 3 + 'px';
        star.style.height = star.style.width;
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.animationDelay = Math.random() * 3 + 's';
        starsContainer.appendChild(star);
      }
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch(`http://localhost:8000/ask?q=${encodeURIComponent(query)}`);
      
      if (!res.ok) {
        throw new Error(`Error: ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch response');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    
    if (!feedback.rating) {
      alert('Please select a rating');
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: result?.query || 'General Feedback',
          rating: feedback.rating,
          comment: feedback.comment
        })
      });

      if (res.ok) {
        setFeedbackSubmitted(true);
        setTimeout(() => {
          setShowFeedback(false);
          setFeedbackSubmitted(false);
          setFeedback({ rating: '', comment: '' });
        }, 2000);
      }
    } catch (err) {
      alert('Failed to submit feedback');
    }
  };

  return (
    <div className="App">
      <div className="space-bg">
        <div className="stars"></div>
        <div className="planet earth"></div>
        <div className="planet mars"></div>
        <div className="planet jupiter"></div>
        <div className="planet saturn">
          <div className="ring"></div>
        </div>
      </div>

      {/* Floating Feedback Button */}
      <button className="floating-feedback-btn" onClick={() => setShowFeedback(true)}>
        💬 Feedback
      </button>

      <div className="container">
        <h1>🚀 AI Model Comparator</h1>
        <p className="subtitle">Compare responses from multiple AI models in space</p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask me anything..."
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? '⏳ Processing...' : '🚀 Compare'}
          </button>
        </form>

        {error && <div className="error">❌ {error}</div>}

        {loading && (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Querying AI models across the galaxy...</p>
          </div>
        )}

        {result && !loading && (
          <div className="results">
            <div className="comparison-header">
              <h3>📊 Comparison Analysis</h3>
              <div className="stats">
                <div className="stat-item">📈 Similarity: {result.comparison.similarity_score}%</div>
                <div className="stat-item">📝 Query: "{result.query}"</div>
              </div>
              <p className="analysis">{result.comparison.analysis}</p>
            </div>
            
            <div className="models-container">
              <div className="model-response">
                <h4>
                  {result.model1.name}
                  <span className="model-badge">Proprietary</span>
                </h4>
                <p>{result.model1.response}</p>
              </div>
              
              <div className="model-response">
                <h4>
                  {result.model2.name}
                  <span className="model-badge">Open Source</span>
                </h4>
                <p>{result.model2.response}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {showFeedback && (
        <div className="feedback-modal" onClick={() => setShowFeedback(false)}>
          <div className="feedback-content" onClick={(e) => e.stopPropagation()}>
            {feedbackSubmitted ? (
              <div className="feedback-success">
                <h2>✅ Thank You!</h2>
                <p>Your feedback has been sent successfully.</p>
              </div>
            ) : (
              <>
                <h2>💬 Feedback</h2>
                <p>Help us improve by sharing your thoughts</p>
                <form onSubmit={handleFeedbackSubmit}>
                  <div className="rating-section">
                    <label>Rating:</label>
                    <div className="rating-buttons">
                      {[1, 2, 3, 4, 5].map(num => (
                        <button
                          key={num}
                          type="button"
                          className={feedback.rating === num ? 'active' : ''}
                          onClick={() => setFeedback({...feedback, rating: num})}
                        >
                          {'⭐'.repeat(num)}
                        </button>
                      ))}
                    </div>
                  </div>
                  <textarea
                    placeholder="Your feedback (optional)..."
                    value={feedback.comment}
                    onChange={(e) => setFeedback({...feedback, comment: e.target.value})}
                    rows="4"
                  />
                  <div className="feedback-actions">
                    <button type="submit" className="submit-feedback">Submit</button>
                    <button type="button" onClick={() => setShowFeedback(false)}>Cancel</button>
                  </div>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
