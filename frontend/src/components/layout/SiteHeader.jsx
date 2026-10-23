import { ArrowRight, BookOpen, Github, History, Moon, Sun, User } from 'lucide-react';
import { PROJECT } from '../../config/project';

export default function SiteHeader({ workspace }) {
  const {
    reset,
    locked,
    stage,
    setShowHistory,
    showHistory,
    history,
    health,
    theme,
    setTheme,
    user,
    signOut,
    setAuthMode,
  } = workspace;
  return (
    <header className="site-header">
      <button className="wordmark" onClick={reset} disabled={locked} aria-label="Research.AI home">
        <span className="brand-icon">
          <BookOpen size={23} />
        </span>
        Research<span className="brand-ai">.AI</span>
      </button>
      <nav aria-label="Main navigation">
        <button
          className={stage !== 'review' ? 'nav-active' : ''}
          onClick={reset}
          disabled={locked}
        >
          WORKSPACE
        </button>
        <button onClick={() => setShowHistory((value) => !value)} aria-expanded={showHistory}>
          <History size={15} /> MY RESEARCH <span className="history-count">{history.length}</span>
        </button>
      </nav>
      <div className="header-tools">
        <span className={`service-status ${health}`}>
          <span />
          {health === 'ready' ? 'Ready' : health === 'checking' ? 'Connecting…' : 'Offline'}
        </span>
        <a
          className="icon-button github-link"
          href={PROJECT.repositoryUrl}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="View project on GitHub"
          title="View project on GitHub"
        >
          <Github size={19} />
        </a>
        <button
          className="icon-button theme-toggle"
          onClick={() => setTheme((value) => (value === 'light' ? 'dark' : 'light'))}
          aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
          title={theme === 'light' ? 'Dark mode' : 'Light mode'}
        >
          {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
        </button>
        {user ? (
          <details className="profile-menu">
            <summary>
              <span className="token-pill">✳ {user.tokens} tokens</span>
              <span className="profile-avatar" aria-label={`Account for ${user.name}`}>
                <User size={16} />
              </span>
            </summary>
            <div className="profile-popover">
              <strong>{user.name}</strong>
              <span>{user.email}</span>
              <p>
                <b>{user.tokens}</b> app tokens left
              </p>
              <small>
                100 on signup · 2 per recommendation · 10 per research · free exports. Local demo
                balance, separate from Groq quota.
              </small>
              <button disabled={locked} onClick={signOut}>
                Log out
              </button>
            </div>
          </details>
        ) : (
          <>
            <button className="welcome-tokens" onClick={() => setAuthMode('signup')}>
              100 welcome tokens
            </button>
            <button className="login-button" onClick={() => setAuthMode('login')}>
              Log in / Sign up <ArrowRight size={14} />
            </button>
          </>
        )}
      </div>
    </header>
  );
}
