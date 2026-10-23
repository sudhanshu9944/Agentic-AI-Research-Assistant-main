import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { safeExternalUrl } from '../../services/safeExternalUrl';

const components = {
  a: ({ href, children }) => (
    <a href={safeExternalUrl(href)} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  ),
  // AI/search content must not load third-party tracking images automatically.
  img: ({ alt }) => <span>{alt || 'Image omitted'}</span>,
};

export default function ResearchMarkdown({ children, className }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={components}
      urlTransform={(url) => safeExternalUrl(url) || ''}
      skipHtml
      className={className}
    >
      {children}
    </ReactMarkdown>
  );
}
