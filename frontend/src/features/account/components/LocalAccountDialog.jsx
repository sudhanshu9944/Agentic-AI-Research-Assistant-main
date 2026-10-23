import { useEffect, useRef, useState } from 'react';
import { ArrowRight, Loader2, X } from 'lucide-react';
import { localAccounts, TOKEN_RULES } from '../services/localAccounts';

export default function LocalAccountDialog({ mode, onModeChange, onClose, onAuthenticated }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const dialog = useRef(null);
  const signup = mode === 'signup';
  useEffect(() => {
    const previous = document.activeElement;
    dialog.current?.querySelector('input')?.focus();
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    function handleKey(event) {
      if (event.key === 'Escape' && !busy) onClose();
      if (event.key !== 'Tab') return;
      const elements = [
        ...dialog.current.querySelectorAll('button:not(:disabled), input:not(:disabled)'),
      ];
      const first = elements[0],
        last = elements[elements.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      }
      if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    }
    document.addEventListener('keydown', handleKey);
    return () => {
      document.body.style.overflow = originalOverflow;
      document.removeEventListener('keydown', handleKey);
      previous?.focus();
    };
  }, [onClose, busy]);

  async function submit(event) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError('');
    try {
      const user = signup
        ? await localAccounts.signUp(name, email, password)
        : await localAccounts.signIn(email, password);
      setPassword('');
      onAuthenticated(user);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="dialog-overlay">
      <section
        className="account-dialog"
        ref={dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="account-title"
      >
        <button
          className="dialog-close icon-button"
          aria-label="Close account dialog"
          onClick={onClose}
          disabled={busy}
        >
          <X size={21} />
        </button>
        <span className="eyebrow">A SPACE FOR YOUR CURIOSITY</span>
        <h2 id="account-title">{signup ? 'Make yourself at home.' : 'Welcome back.'}</h2>
        <p className="account-intro">
          {signup
            ? `Start with ${TOKEN_RULES.welcome} free app tokens.`
            : 'Log in to your account on this browser.'}
        </p>
        <div className="account-tabs">
          <button
            className={!signup ? 'active' : ''}
            disabled={busy}
            onClick={() => {
              onModeChange('login');
              setError('');
            }}
          >
            Log in
          </button>
          <button
            className={signup ? 'active' : ''}
            disabled={busy}
            onClick={() => {
              onModeChange('signup');
              setError('');
            }}
          >
            Sign up
          </button>
        </div>
        <form onSubmit={submit}>
          {signup && (
            <label>
              Your name
              <input
                autoComplete="name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
                minLength={2}
                maxLength={70}
                disabled={busy}
              />
            </label>
          )}
          <label>
            Email address
            <input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              maxLength={160}
              disabled={busy}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete={signup ? 'new-password' : 'current-password'}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={signup ? 8 : 1}
              maxLength={128}
              disabled={busy}
            />
          </label>
          {signup && (
            <small className="password-hint">
              At least 8 characters. Your password is stored as a salted hash.
            </small>
          )}
          {error && (
            <p role="alert" className="account-error">
              {error}
            </p>
          )}
          <button className="button primary" disabled={busy}>
            {busy ? <Loader2 className="spin" size={17} /> : <ArrowRight size={17} />}
            {busy ? 'One moment…' : signup ? 'Create my account' : 'Log in'}
          </button>
        </form>
        <div className="token-explainer">
          <strong>YOUR APP TOKENS</strong>
          <span>
            Recommendations · {TOKEN_RULES.recommendations} &nbsp; Research · {TOKEN_RULES.research}{' '}
            &nbsp; Export · free
          </span>
          <p>
            Tokens are a local demo balance, separate from the AI provider's quota. Failed requests
            are refunded.
          </p>
        </div>
        <p className="local-account-note">
          This account stays in this browser. It isn't a server login; saved reports belong to this
          app installation.
        </p>
      </section>
    </div>
  );
}
