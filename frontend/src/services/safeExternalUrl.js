/** Citations may open web pages, never scripts, local files or embedded credentials. */
export function safeExternalUrl(value) {
  if (
    typeof value !== 'string' ||
    [...value].some((character) => character.charCodeAt(0) <= 32 || character === '\\')
  )
    return undefined;
  try {
    const url = new URL(value);
    if (['http:', 'https:'].includes(url.protocol) && !url.username && !url.password)
      return url.href;
  } catch {
    // Invalid or relative source links stay inert.
  }
  return undefined;
}
