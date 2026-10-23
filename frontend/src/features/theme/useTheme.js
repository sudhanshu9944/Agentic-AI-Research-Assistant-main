import { useEffect, useState } from 'react';
const THEME_KEY = 'researchai.theme.v1';
export function useTheme() {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem(THEME_KEY) === 'dark' ? 'dark' : 'light';
    } catch {
      return 'light';
    }
  });
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch {
      /* Storage restrictions should not prevent changing the current theme. */
    }
  }, [theme]);
  return [theme, setTheme];
}
