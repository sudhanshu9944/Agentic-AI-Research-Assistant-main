import { ArrowLeft, BookOpen, Check, ChevronDown, Download, FileText, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ReportViewer from './ReportViewer';

export default function ReviewPage({ session, locked, busy, reset, download }) {
  return (
    <section className="review-section content-width">
      <button className="back-link" onClick={reset} disabled={locked}>
        <ArrowLeft size={15} /> Start a new research
      </button>
      <span className="eyebrow">READ FIRST. DOWNLOAD WHEN READY.</span>
      <h1>
        Here's what <mark>we found.</mark>
      </h1>
      <p className="section-intro">{session.query}</p>
      <div className="review-stats">
        <span>
          <strong>{session.sources.length}</strong> sources
        </span>
        <span>
          <strong>{session.insights.length}</strong> insights
        </span>
        <span>
          <strong>{session.final_report.trim().split(/\s+/).length.toLocaleString()}</strong> words
        </span>
        <span className="review-ready">
          <Check size={16} /> Saved to your library
        </span>
      </div>
      <div className="review-summary">
        <span className="note-label">THE QUICK READ</span>
        <div className="markdown-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{session.summary}</ReactMarkdown>
        </div>
      </div>
      <div className="coverage-grid">
        <article className="coverage-card">
          <h3>
            <Check size={19} /> What you asked us to explore
          </h3>
          <ul>
            {(session.selected_topics?.length
              ? session.selected_topics
              : session.research_plan.sub_topics || []
            ).map((topic) => (
              <li key={topic}>{topic}</li>
            ))}
          </ul>
          <small>These are the requested angles. Evidence may be incomplete.</small>
        </article>
        <article className="coverage-card yellow">
          <h3>What wasn't included</h3>
          {session.excluded_topics?.length ? (
            <ul>
              {session.excluded_topics.map((topic) => (
                <li key={topic}>{topic}</li>
              ))}
            </ul>
          ) : (
            <p>No topics were explicitly deselected for this report.</p>
          )}
          <h4>Evidence gaps & limitations</h4>
          {session.evidence_gaps?.length ? (
            <ul>
              {session.evidence_gaps.map((gap) => (
                <li key={gap}>{gap}</li>
              ))}
            </ul>
          ) : (
            <p>
              {session.selected_topics?.length
                ? 'The AI identified no specific coverage gaps. This does not guarantee complete coverage; check the sources below.'
                : 'This older report has no separate gap assessment. Check its limitations and source excerpts.'}
            </p>
          )}
        </article>
      </div>
      <div className="method-note">
        <BookOpen size={20} />
        <p>
          <strong>How this came together.</strong> We searched the selected angles, ranked available
          source excerpts, extracted insights and wrote this report. Findings are based on search
          excerpts; linked pages have not been fully verified.
        </p>
      </div>
      <details className="full-research">
        <summary>
          Explore the full research <ChevronDown size={19} />
        </summary>
        <ReportViewer key={session.session_id} result={session} />
      </details>
      <div className="export-panel">
        <div>
          <span className="eyebrow">YOUR RESEARCH, READY TO GO</span>
          <h2>Happy with the picture?</h2>
          <p>Generate a PDF of the report you just reviewed, or keep an editable Markdown copy.</p>
        </div>
        <div className="export-actions">
          <button className="button primary" onClick={() => download('pdf')} disabled={locked}>
            {busy === 'pdf' ? <Loader2 size={18} className="spin" /> : <Download size={18} />}
            {busy === 'pdf' ? 'Generating PDF…' : 'Generate PDF'}
          </button>
          <button
            className="button secondary"
            onClick={() => download('markdown')}
            disabled={locked}
          >
            {busy === 'markdown' ? <Loader2 size={18} className="spin" /> : <FileText size={18} />}
            Markdown
          </button>
        </div>
      </div>
    </section>
  );
}
