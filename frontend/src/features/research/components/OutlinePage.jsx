import { ArrowRight, ArrowLeft, Loader2, Plus, Sparkles } from 'lucide-react';
import { TOKEN_RULES } from '../../account/services/localAccounts';

export default function OutlinePage({ workspace }) {
  const {
    recommendations,
    selected,
    locked,
    busy,
    customTopic,
    elapsed,
    setStage,
    setError,
    setSelected,
    toggleTopic,
    addTopic,
    setCustomTopic,
    research,
  } = workspace;
  return (
    <section className="outline-section content-width">
      <button
        className="back-link"
        disabled={locked}
        onClick={() => {
          setStage('topic');
          setError('');
        }}
      >
        <ArrowLeft size={15} /> Change topic
      </button>
      <span className="eyebrow">THE BIG PICTURE, CHOSEN BY YOU</span>
      <h1>
        What should we <mark>explore?</mark>
      </h1>
      <p className="section-intro">
        AI recommends these angles for <strong>{recommendations.query}</strong>. Keep what fits your
        research. Uncheck what doesn't.
      </p>
      <div className="outline-toolbar">
        <span>
          <Sparkles size={16} /> AI-suggested topics
        </span>
        <button
          className="text-button"
          disabled={locked}
          onClick={() =>
            setSelected(
              selected.length === recommendations.topics.length ? [] : recommendations.topics,
            )
          }
        >
          {selected.length === recommendations.topics.length ? 'Deselect all' : 'Select all'}
        </button>
      </div>
      <div className="topic-grid">
        {recommendations.topics.map((topic, index) => (
          <label
            className={`topic-option ${selected.includes(topic) ? 'selected' : ''}`}
            key={topic}
          >
            <input
              type="checkbox"
              checked={selected.includes(topic)}
              disabled={locked}
              onChange={() => toggleTopic(topic)}
            />
            <span className="option-number">{String(index + 1).padStart(2, '0')}</span>
            <span>{topic}</span>
          </label>
        ))}
      </div>
      <form className="custom-topic" onSubmit={addTopic}>
        <label htmlFor="custom-topic">Something missing? Add your own angle.</label>
        <div>
          <input
            id="custom-topic"
            value={customTopic}
            onChange={(event) => setCustomTopic(event.target.value)}
            maxLength={180}
            placeholder="e.g. Real-world examples in India"
            disabled={locked || recommendations.topics.length >= 12}
          />
          <button
            className="button secondary"
            disabled={
              locked || customTopic.trim().length < 2 || recommendations.topics.length >= 12
            }
          >
            <Plus size={16} /> Add topic
          </button>
        </div>
      </form>
      <div className="outline-footer">
        <div>
          <strong>
            {selected.length} of {recommendations.topics.length} topics selected
          </strong>
          <p>
            We'll research these angles, then show you a review. No PDF is generated yet. Research
            uses {TOKEN_RULES.research} app tokens.
          </p>
        </div>
        <button className="button primary" disabled={locked || !selected.length} onClick={research}>
          {busy === 'research' ? (
            <>
              <Loader2 size={18} className="spin" /> Researching…
            </>
          ) : (
            <>
              Research selected topics <ArrowRight size={18} />
            </>
          )}
        </button>
      </div>
      {busy === 'research' && (
        <div className="research-progress" role="status">
          <Loader2 size={22} className="spin" />
          <div>
            <strong>Following the evidence.</strong>
            <p>
              Searching sources, extracting findings and preparing your review. {elapsed}s elapsed.
            </p>
            <small>Free services may need a cooldown. Keep this page open.</small>
          </div>
        </div>
      )}
    </section>
  );
}
