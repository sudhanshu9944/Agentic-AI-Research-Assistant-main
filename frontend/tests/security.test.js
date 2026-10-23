import test from 'node:test';
import assert from 'node:assert/strict';
import { safeExternalUrl } from '../src/services/safeExternalUrl.js';

test('untrusted citations permit web links and reject executable/file/credential links', () => {
  assert.equal(
    safeExternalUrl('https://example.com/evidence?q=solar#source'),
    'https://example.com/evidence?q=solar#source',
  );
  for (const value of [
    'javascript:alert(1)',
    'data:text/html,test',
    'file:///private.txt',
    '//example.com',
    'https://user:pass@example.com',
    'https://example.com\n.evil.test',
    'https://example.com\\evil',
    null,
  ]) {
    assert.equal(safeExternalUrl(value), undefined);
  }
});
