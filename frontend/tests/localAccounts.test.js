import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createLocalAccounts,
  TOKEN_RULES,
} from '../src/features/account/services/localAccounts.js';
function memory() {
  const store = new Map();
  return {
    getItem: (key) => store.get(key) ?? null,
    setItem: (key, value) => store.set(key, value),
    removeItem: (key) => store.delete(key),
    dump: () => [...store.values()].join(''),
  };
}
test('local signup hashes the password, persists login, and grants exactly 100 tokens', async () => {
  const storage = memory(),
    auth = createLocalAccounts(storage);
  const user = await auth.signUp('Demo Student', ' Student@example.test ', 'Test-only-password8');
  assert.equal(user.tokens, 100);
  assert.equal(user.email, 'student@example.test');
  assert.ok(!storage.dump().includes('Test-only-password8'));
  assert.ok(!('hash' in user));
  assert.deepEqual(createLocalAccounts(storage).currentUser(), user);
  auth.signOut();
  assert.equal(auth.currentUser(), null);
  await assert.rejects(auth.signIn('student@example.test', 'wrong-password'));
  assert.equal((await auth.signIn('STUDENT@example.test', 'Test-only-password8')).tokens, 100);
  await assert.rejects(auth.signUp('Demo', 'student@example.test', 'Another-password9'));
});
test('costs persist after reload; failed requests refund once and cannot inflate balance', async () => {
  const storage = memory(),
    auth = createLocalAccounts(storage);
  await auth.signUp('Student', 'student@example.test', 'Test-only-password8');
  auth.spendTokens(TOKEN_RULES.recommendations);
  const { receipt } = auth.spendTokens(TOKEN_RULES.research);
  assert.equal(createLocalAccounts(storage).currentUser().tokens, 88);
  assert.equal(auth.refundTokens(receipt).tokens, 98);
  assert.equal(auth.refundTokens(receipt).tokens, 98);
  assert.equal(auth.refundTokens({ ...receipt, id: 'invented' }).tokens, 98);
  assert.throws(() => auth.spendTokens(-10));
  assert.throws(() => auth.spendTokens(999));
  assert.equal(auth.currentUser().tokens, 98);
});
test('logout blocks charges and account balances remain separate', async () => {
  const storage = memory(),
    auth = createLocalAccounts(storage);
  await auth.signUp('First Student', 'one@example.test', 'Test-only-password8');
  auth.spendTokens(10);
  auth.signOut();
  assert.throws(() => auth.spendTokens(2));
  await auth.signUp('Second Student', 'two@example.test', 'Test-only-password8');
  assert.equal(auth.currentUser().tokens, 100);
  await auth.signIn('one@example.test', 'Test-only-password8');
  assert.equal(auth.currentUser().tokens, 90);
});
test('invalid signup and unavailable storage give actionable errors', async () => {
  const auth = createLocalAccounts(memory());
  await assert.rejects(auth.signUp('A', 'bad', 'short'));
  await assert.rejects(auth.signUp('Valid Name', 'bad', 'Valid-password8'));
  await assert.rejects(auth.signUp('Valid Name', 'valid@example.test', 'short'));
  assert.throws(() => createLocalAccounts({ getItem: () => '{broken' }).currentUser(), /storage/);
});
