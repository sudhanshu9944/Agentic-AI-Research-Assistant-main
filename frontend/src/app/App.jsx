import { useWorkspace } from './useWorkspace';
import SiteHeader from '../components/layout/SiteHeader';
import SiteFooter from '../components/layout/SiteFooter';
import ErrorNotice from '../components/ui/ErrorNotice';
import LocalAccountDialog from '../features/account/components/LocalAccountDialog';
import ResearchHistory from '../features/research/components/ResearchHistory';
import ResearchJourney from '../features/research/components/ResearchJourney';
import TopicPage from '../features/research/components/TopicPage';
import OutlinePage from '../features/research/components/OutlinePage';
import ReviewPage from '../features/research/components/ReviewPage';

export default function App() {
  const workspace = useWorkspace();
  const { showHistory, authMode, stage, session, error } = workspace;
  return (
    <div className="site-shell">
      <div className="utility-bar">
        <span>YOUR CURIOSITY. YOUR DIRECTION.</span>
        <span>AI-assisted research, thoughtfully put together.</span>
      </div>
      <SiteHeader workspace={workspace} />
      {showHistory && (
        <ResearchHistory
          history={workspace.history}
          locked={workspace.locked}
          loadSession={workspace.loadSession}
          setShowHistory={workspace.setShowHistory}
        />
      )}
      {authMode && (
        <LocalAccountDialog
          mode={authMode}
          onModeChange={workspace.setAuthMode}
          onClose={workspace.closeAuth}
          onAuthenticated={workspace.authenticated}
        />
      )}
      <main>
        <ResearchJourney stage={stage} />
        {error && <ErrorNotice error={error} setError={workspace.setError} />}
        {stage === 'topic' && <TopicPage workspace={workspace} />}
        {stage === 'outline' && workspace.recommendations && <OutlinePage workspace={workspace} />}
        {stage === 'review' && session && (
          <ReviewPage
            session={session}
            locked={workspace.locked}
            busy={workspace.busy}
            reset={workspace.reset}
            download={workspace.download}
          />
        )}
      </main>
      <SiteFooter reset={workspace.reset} locked={workspace.locked} />
    </div>
  );
}
