/** Browser-local demo accounts and app-token ledger. This does not secure server APIs. */
export const TOKEN_RULES = Object.freeze({
  welcome: 100,
  recommendations: 2,
  research: 10,
  export: 0,
});
const ACCOUNTS = 'researchai.accounts.v1';
const SESSION = 'researchai.session.v1';
const encoder = new TextEncoder();
const toHex = (bytes) => Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
const fromHex = (text) => new Uint8Array(text.match(/.{2}/g).map((value) => parseInt(value, 16)));

export function createLocalAccounts(storage = globalThis.localStorage) {
  function accounts() {
    try {
      const value = JSON.parse(storage.getItem(ACCOUNTS) || '[]');
      if (!Array.isArray(value)) throw new Error('Invalid data');
      return value;
    } catch {
      throw new Error('Local account data is unavailable. Please check browser storage.');
    }
  }
  function save(value) {
    try {
      storage.setItem(ACCOUNTS, JSON.stringify(value));
    } catch {
      throw new Error(
        'This browser could not save the account. Allow local storage and try again.',
      );
    }
  }
  function publicUser(account) {
    return account
      ? { id: account.id, name: account.name, email: account.email, tokens: account.tokens }
      : null;
  }
  function currentUser() {
    const email = storage.getItem(SESSION);
    return publicUser(accounts().find((account) => account.email === email));
  }
  async function passwordHash(password, salt) {
    if (!globalThis.crypto?.subtle)
      throw new Error('Local sign-in needs HTTPS or localhost in a modern browser.');
    const key = await crypto.subtle.importKey('raw', encoder.encode(password), 'PBKDF2', false, [
      'deriveBits',
    ]);
    const result = await crypto.subtle.deriveBits(
      { name: 'PBKDF2', salt: fromHex(salt), iterations: 150000, hash: 'SHA-256' },
      key,
      256,
    );
    return toHex(new Uint8Array(result));
  }
  async function signUp(name, email, password) {
    name = name.trim();
    email = email.trim().toLowerCase();
    if (name.length < 2 || name.length > 70)
      throw new Error('Enter a name between 2 and 70 characters.');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 160)
      throw new Error('Enter a valid email address.');
    if (password.length < 8 || password.length > 128)
      throw new Error('Use a password with 8 to 128 characters.');
    if (accounts().some((account) => account.email === email))
      throw new Error('An account with this email already exists in this browser. Please log in.');
    const salt = toHex(crypto.getRandomValues(new Uint8Array(16)));
    const hash = await passwordHash(password, salt);
    const all = accounts();
    if (all.some((account) => account.email === email))
      throw new Error('This email already has a local account. Please log in.');
    const account = {
      id: crypto.randomUUID(),
      name,
      email,
      salt,
      hash,
      tokens: TOKEN_RULES.welcome,
      ledger: [],
    };
    save([...all, account]);
    storage.setItem(SESSION, email);
    return publicUser(account);
  }
  async function signIn(email, password) {
    email = email.trim().toLowerCase();
    const account = accounts().find((item) => item.email === email);
    if (!account || (await passwordHash(password, account.salt)) !== account.hash)
      throw new Error('Email or password is incorrect for this browser.');
    storage.setItem(SESSION, email);
    return publicUser(account);
  }
  function signOut() {
    storage.removeItem(SESSION);
  }
  function spendTokens(amount) {
    if (!Number.isInteger(amount) || amount < 1) throw new Error('Invalid token cost.');
    const all = accounts();
    const email = storage.getItem(SESSION);
    const account = all.find((item) => item.email === email);
    if (!account) throw new Error('Please log in to continue.');
    if (account.tokens < amount)
      throw new Error(
        `You need ${amount} app tokens for this action. Your balance is ${account.tokens}.`,
      );
    const receipt = { id: crypto.randomUUID(), email, amount };
    account.tokens -= amount;
    account.ledger.push({ id: receipt.id, amount, refunded: false });
    save(all);
    return { user: publicUser(account), receipt };
  }
  function refundTokens(receipt) {
    const all = accounts();
    const account = all.find((item) => item.email === receipt.email);
    const entry = account?.ledger.find((item) => item.id === receipt.id);
    if (entry && !entry.refunded) {
      account.tokens += entry.amount;
      entry.refunded = true;
      save(all);
    }
    return currentUser();
  }
  return { currentUser, signUp, signIn, signOut, spendTokens, refundTokens };
}

export const localAccounts = createLocalAccounts();
