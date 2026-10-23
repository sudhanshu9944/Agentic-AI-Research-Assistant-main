import { api } from './researchApi';
/** Fetches a saved report and starts a download only after an explicit user action. */
export async function downloadReport(session, format) {
  const content =
    format === 'pdf'
      ? await api.exportPDF(session.session_id)
      : await api.exportMarkdown(session.session_id);
  const blob =
    format === 'pdf' ? content : new Blob([content], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  const title = session.query.replace(/[^\p{L}\p{N}_-]+/gu, '_').slice(0, 60) || 'research';
  anchor.download = `${title}_report.${format === 'pdf' ? 'pdf' : 'md'}`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
