import { ArrowRight, Check, ChevronDown, Loader2, Plus, Search, Sparkles } from 'lucide-react';
import { MODELS, EXAMPLES } from '../config';
import { TOKEN_RULES } from '../../account/services/localAccounts';

export default function TopicPage({ workspace }) {
  const {
    query,
    model,
    temperature,
    busy,
    locked,
    user,
    topicInput,
    setQuery,
    setModel,
    setTemperature,
    suggest,
  } = workspace;
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">A LITTLE QUESTION. A BIGGER PICTURE.</span>
          <h1>
            Good research.
            <br />
            <mark>Your way.</mark>
          </h1>
          <p className="hero-description">
            Go from a curious thought to a clear, source-backed report. You choose what matters. AI
            connects the dots.
          </p>
          <ul className="hero-checks">
            <li>
              <Check size={16} /> Pick the angles you want to explore
            </li>
            <li>
              <Check size={16} /> Understand the findings before you download
            </li>
            <li>
              <Check size={16} /> Keep the sources, see the gaps
            </li>
          </ul>
          <a href="#workspace" className="button primary hero-cta">
            Start exploring <ArrowRight size={17} />
          </a>
        </div>
        <div className="hero-notes" aria-label="How it works">
          <div className="note-card pink">
            <span className="note-label">01 / YOUR IDEA</span>
            <Sparkles size={27} />
            <h2>
              Start with
              <br />a “what if?”
            </h2>
            <p>A topic is all you need. We'll help you find the right questions.</p>
          </div>
          <div className="note-card blue">
            <span className="note-label">02 / YOUR CALL</span>
            <Check size={27} />
            <h2>You set the scope.</h2>
            <p>Choose AI recommendations. Add your own. Leave the rest out.</p>
          </div>
          <span className="hand-note">Curiosity looks good on you ↗</span>
        </div>
      </section>
      <section className="topic-section" id="workspace">
        <div className="section-heading">
          <div>
            <span className="eyebrow">LET'S GET INTO IT</span>
            <h2>What's on your mind?</h2>
          </div>
          <span className="small-stamp">Built for curious minds ✳</span>
        </div>
        <form className="topic-form" onSubmit={suggest}>
          <label htmlFor="research-topic">Your research topic</label>
          <div className="topic-input-row">
            <Search size={23} />
            <input
              id="research-topic"
              ref={topicInput}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              maxLength={500}
              minLength={3}
              required
              disabled={locked}
              placeholder="e.g. How is AI changing education?"
            />
            <button
              type="submit"
              className="button primary"
              disabled={locked || query.trim().length < 3}
            >
              {busy === 'recommend' ? (
                <>
                  <Loader2 className="spin" size={17} /> Thinking…
                </>
              ) : (
                <>
                  Explore this topic <ArrowRight size={18} />
                </>
              )}
            </button>
          </div>
          <p className="token-cost-note">
            Recommendations: {TOKEN_RULES.recommendations} app tokens ·{' '}
            {user ? `${user.tokens} remaining` : `${TOKEN_RULES.welcome} free when you sign up`}
          </p>
        </form>
        <div className="example-row">
          <span>NEED A SPARK?</span>
          {EXAMPLES.map((example) => (
            <button
              key={example}
              disabled={locked}
              onClick={() => {
                setQuery(example);
                topicInput.current?.focus();
              }}
            >
              {example} <Plus size={12} />
            </button>
          ))}
        </div>
        <details className="settings">
          <summary>
            Research preferences <ChevronDown size={15} />
          </summary>
          <div>
            <label>
              AI model
              <select
                value={model}
                disabled={locked}
                onChange={(event) => setModel(event.target.value)}
              >
                {MODELS.map(([id, name]) => (
                  <option value={id} key={id}>
                    {name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Writing creativity · {temperature.toFixed(1)}
              <input
                aria-label="Writing creativity"
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={temperature}
                disabled={locked}
                onChange={(event) => setTemperature(Number(event.target.value))}
              />
            </label>
            <p>
              Lower creativity keeps the writing focused. Free API availability and limits apply.
            </p>
          </div>
        </details>
      </section>
      <section className="how-section">
        <span className="eyebrow">FROM QUESTION TO CLARITY</span>
        <h2>
          A report you understand.
          <br />
          <span>Before you download.</span>
        </h2>
        <div className="how-grid">
          {[
            [
              '01',
              'Find your direction',
              'AI suggests relevant angles. Check the ones you want and add anything it missed.',
            ],
            [
              '02',
              'Look a little deeper',
              'We search the web, compare source excerpts and bring the key findings together.',
            ],
            [
              '03',
              'Make it yours',
              'Read the summary, see what is missing, then generate your PDF when you are ready.',
            ],
          ].map(([n, title, body]) => (
            <article key={n}>
              <span>{n}</span>
              <h3>{title}</h3>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}
