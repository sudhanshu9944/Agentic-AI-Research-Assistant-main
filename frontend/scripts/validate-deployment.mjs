/** Stop Vercel builds before shipping a frontend without a usable backend URL. */
export function validateDeployment(env) {
  if (!env.VERCEL) return;
  if (env.VITE_API_BASE_URL === '/api') return;
  let target;
  try {
    target = new URL(env.VITE_API_BASE_URL || '');
  } catch {
    throw new Error('Set VITE_API_BASE_URL to the public HTTPS backend URL before deploying.');
  }
  if (
    target.protocol !== 'https:' ||
    ['localhost', '127.0.0.1', '::1'].includes(target.hostname) ||
    target.username ||
    target.password
  ) {
    throw new Error('VITE_API_BASE_URL must be a public HTTPS backend URL without credentials.');
  }
}
validateDeployment(process.env);
