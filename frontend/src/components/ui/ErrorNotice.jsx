import { X } from 'lucide-react';

export default function ErrorNotice({ error, setError }) {
  return (
    <div className="error-notice" role="alert">
      <strong>Something needs a second look.</strong>
      <span>{error}</span>
      <button aria-label="Dismiss error" onClick={() => setError('')}>
        <X size={17} />
      </button>
    </div>
  );
}
