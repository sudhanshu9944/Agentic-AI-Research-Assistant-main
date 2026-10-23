import test from 'node:test';
import assert from 'node:assert/strict';
import { validateDeployment } from '../scripts/validate-deployment.mjs';

test('Vercel builds require an HTTPS backend without embedded credentials', () => {
  validateDeployment({});
  validateDeployment({ VERCEL: '1', VITE_API_BASE_URL: '/api' });
  validateDeployment({ VERCEL: '1', VITE_API_BASE_URL: 'https://research.example.com' });
  for (const url of [
    '',
    'http://research.example.com',
    'https://localhost',
    'https://127.0.0.1',
    'https://user:secret@research.example.com',
  ]) {
    assert.throws(() => validateDeployment({ VERCEL: '1', VITE_API_BASE_URL: url }));
  }
});
