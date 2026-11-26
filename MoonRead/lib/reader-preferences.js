export const READER_STORAGE_KEY = "moonread-state-v1";
export const LEGACY_READER_SETTINGS = ["moonread-reader-settings", "dse-reader-settings"];

// Apply only an allowlisted theme before the reader paints. The rest of the
// saved data still loads through the reader store after hydration.
export const initialReaderThemeScript = String.raw`(() => {
  if (!/^\/(?:books\/[^/]+\/)?read\//.test(location.pathname)) return;
  try {
    let preferences = JSON.parse(localStorage.getItem(${JSON.stringify(READER_STORAGE_KEY)}) || '{}')?.reader;
    if (!preferences) {
      for (const key of ${JSON.stringify(LEGACY_READER_SETTINGS)}) {
        const legacy = localStorage.getItem(key);
        if (legacy) { preferences = JSON.parse(legacy); break; }
      }
    }
    const theme = preferences?.theme;
    if (theme === 'night' || theme === 'sepia') document.documentElement.dataset.initialReaderTheme = theme;
  } catch {}
})();`;
