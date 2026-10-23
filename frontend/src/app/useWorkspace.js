import { useEffect, useRef, useState } from 'react';
import { api } from '../services/researchApi';
import { localAccounts, TOKEN_RULES } from '../features/account/services/localAccounts';
import { MODELS } from '../features/research/config';
import { useTheme } from '../features/theme/useTheme';
import { downloadReport } from '../services/downloadReport';

/** Coordinates the topic → outline → review flow and refundable app-token charges. */
export function useWorkspace() {
  const [query, setQuery] = useState('');
  const [user, setUser] = useState(() => {
    try {
      return localAccounts.currentUser();
    } catch {
      return null;
    }
  });
  const [authMode, setAuthMode] = useState(null);
  const pendingAction = useRef(null);
  const [theme, setTheme] = useTheme();
  const [model, setModel] = useState(MODELS[0][0]);
  const [temperature, setTemperature] = useState(0.2);
  const [health, setHealth] = useState('checking');
  const [stage, setStage] = useState('topic');
  const [recommendations, setRecommendations] = useState(null);
  const [selected, setSelected] = useState([]);
  const [customTopic, setCustomTopic] = useState('');
  const [session, setSession] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [elapsed, setElapsed] = useState(0);
  const generation = useRef(0);
  const topicInput = useRef(null);
  const locked = Boolean(busy);

  useEffect(() => {
    const update = () => {
      try {
        setUser(localAccounts.currentUser());
      } catch {
        setUser(null);
      }
    };
    window.addEventListener('storage', update);
    return () => window.removeEventListener('storage', update);
  }, []);

  useEffect(() => {
    let active = true;
    api.healthCheck().then((result) => {
      if (active)
        setHealth(result.status === 'healthy' && result.research_ready ? 'ready' : 'offline');
    });
    api
      .getHistory()
      .then((result) => {
        if (active) setHistory(result);
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, [stage]);

  useEffect(() => {
    if (busy !== 'research') return;
    const timer = window.setInterval(() => setElapsed((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, [busy]);

  function reset() {
    if (locked) return;
    generation.current += 1;
    setStage('topic');
    setSession(null);
    setRecommendations(null);
    setSelected([]);
    setError('');
    setQuery('');
    setShowHistory(false);
    topicInput.current?.focus();
  }

  async function suggest(event) {
    event?.preventDefault();
    if (locked || query.trim().length < 3) return;
    if (!requireAccount('suggest')) return;
    const request = ++generation.current;
    let receipt;
    setBusy('recommend');
    setError('');
    setSession(null);
    try {
      const spent = localAccounts.spendTokens(TOKEN_RULES.recommendations);
      receipt = spent.receipt;
      setUser(spent.user);
      const result = await api.recommendTopics(query.trim(), model, temperature);
      if (request !== generation.current) return;
      setRecommendations(result);
      setSelected(result.topics);
      setStage('outline');
      setCustomTopic('');
    } catch (err) {
      refund(receipt);
      setError(err.message);
    } finally {
      setBusy('');
    }
  }

  function requireAccount(action) {
    try {
      const account = localAccounts.currentUser();
      if (account) return account;
      pendingAction.current = action;
      setAuthMode('login');
    } catch (err) {
      setError(err.message);
    }
    return null;
  }

  function refund(receipt) {
    if (!receipt) return;
    try {
      setUser(localAccounts.refundTokens(receipt));
    } catch {
      setError('The request failed and this browser could not save the token refund.');
    }
  }

  function closeAuth() {
    setAuthMode(null);
    pendingAction.current = null;
  }

  function authenticated(account) {
    setUser(account);
    setAuthMode(null);
    const action = pendingAction.current;
    pendingAction.current = null;
    if (action === 'suggest') suggest();
    if (action === 'research') research();
  }

  function signOut() {
    localAccounts.signOut();
    setUser(null);
    reset();
  }

  function toggleTopic(topic) {
    setSelected((items) =>
      items.includes(topic) ? items.filter((item) => item !== topic) : [...items, topic],
    );
  }

  function addTopic(event) {
    event.preventDefault();
    const topic = customTopic.trim();
    if (topic.length < 2 || recommendations.topics.length >= 12) return;
    if (!recommendations.topics.some((item) => item.toLowerCase() === topic.toLowerCase())) {
      setRecommendations((value) => ({ ...value, topics: [...value.topics, topic] }));
      setSelected((value) => [...value, topic]);
    }
    setCustomTopic('');
  }

  async function research() {
    if (locked || !selected.length) return;
    if (!requireAccount('research')) return;
    let receipt;
    setBusy('research');
    setError('');
    setElapsed(0);
    try {
      const spent = localAccounts.spendTokens(TOKEN_RULES.research);
      receipt = spent.receipt;
      setUser(spent.user);
      const result = await api.runResearch(
        recommendations.query,
        model,
        temperature,
        selected,
        recommendations.topics.filter((topic) => !selected.includes(topic)),
      );
      setSession(result);
      setStage('review');
      api
        .getHistory()
        .then(setHistory)
        .catch(() => {});
    } catch (err) {
      refund(receipt);
      setError(err.message);
    } finally {
      setBusy('');
    }
  }

  async function loadSession(id) {
    if (locked) return;
    generation.current += 1;
    setBusy('history');
    setError('');
    try {
      const result = await api.getReport(id);
      setSession(result);
      setStage('review');
      setShowHistory(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy('');
    }
  }

  async function download(format) {
    if (!session || locked) return;
    setBusy(format);
    setError('');
    try {
      await downloadReport(session, format);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy('');
    }
  }

  return {
    query,
    user,
    authMode,
    theme,
    model,
    temperature,
    health,
    stage,
    recommendations,
    selected,
    customTopic,
    session,
    history,
    showHistory,
    busy,
    error,
    elapsed,
    locked,
    topicInput,
    setQuery,
    setAuthMode,
    setTheme,
    setModel,
    setTemperature,
    setStage,
    setSelected,
    setCustomTopic,
    setShowHistory,
    setError,
    reset,
    suggest,
    closeAuth,
    authenticated,
    signOut,
    toggleTopic,
    addTopic,
    research,
    loadSession,
    download,
  };
}
