import { Github } from 'lucide-react';
import { PROJECT } from '../../config/project';

export default function SiteFooter({ reset, locked }) {
  return (
    <footer className="site-footer">
      <div className="footer-top">
        <button className="wordmark" onClick={reset} disabled={locked}>
          Research<span className="brand-ai">.AI</span>
        </button>
        <p>A little curiosity goes a long way.</p>
        <a href={PROJECT.repositoryUrl} target="_blank" rel="noopener noreferrer">
          <Github size={15} /> Explore the source
        </a>
      </div>
      <div className="footer-credits">
        <p>
          Made with ❤️ by <strong>{PROJECT.contributors.join(', ')}</strong>
        </p>
        <p>
          <em>Built with ❤️ using</em> {PROJECT.stack.join(' · ')}
        </p>
      </div>
    </footer>
  );
}
