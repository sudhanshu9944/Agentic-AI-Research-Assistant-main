import { ArrowRight, FileText, X } from 'lucide-react';

export default function ResearchHistory({ history, locked, loadSession, setShowHistory }) {
  const handleLoadSession = loadSession;
  return (
    <section className="history-panel" aria-label="Saved research">
      <div className="section-heading">
        <div>
          <span className="eyebrow">YOUR LIBRARY</span>
          <h2>Pick up where you left off.</h2>
        </div>
        <button
          className="icon-button"
          aria-label="Close history"
          onClick={() => setShowHistory(false)}
        >
          <X size={20} />
        </button>
      </div>
      {history.length ? (
        <div className="history-grid">
          {history.map((item) => (
            <button
              key={item.session_id}
              className="history-item"
              disabled={locked}
              onClick={() => handleLoadSession(item.session_id)}
            >
              <FileText size={20} />
              <span>
                <strong>{item.query}</strong>
                <small>{new Date(item.created_at).toLocaleDateString()}</small>
              </span>
              <ArrowRight size={18} />
            </button>
          ))}
        </div>
      ) : (
        <p>No saved research yet. Your first report will appear here.</p>
      )}
    </section>
  );
}
