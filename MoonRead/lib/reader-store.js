"use client";

import { useMemo, useSyncExternalStore } from "react";

// MoonRead client store — reading progress, bookmarks, favorites, history,
// and reader settings. Persists to localStorage; simple pub/sub for React.
//
// Server render and the first client (hydration) render both use the frozen
// empty snapshot, so storage never leaks into SSR markup and hydration cannot
// diverge. The persisted client snapshot only becomes visible after hydration.
const KEY = "moonread-state-v1";
const LEGACY_SETTINGS = ["moonread-reader-settings", "dse-reader-settings"];

const defaultReader = {
  theme: "paper",
  fontSize: 20,
  lineHeight: 2.0,
  width: 760,
  paragraphSpacing: 1.25,
  fontFamily: "sarabun",
  autoAdvance: true,
};

const emptySnapshot = Object.freeze({
  progress: Object.freeze({}),
  bookmarks: Object.freeze({}),
  favorites: Object.freeze([]),
  reader: Object.freeze({ ...defaultReader }),
});

let clientSnapshot = null;
const listeners = new Set();

function read() {
  if (typeof window === "undefined") return emptySnapshot;
  try {
    const raw = JSON.parse(window.localStorage.getItem(KEY) || "{}");
    let reader = { ...defaultReader, ...(raw.reader || {}) };
    if (!raw.reader) {
      for (const k of LEGACY_SETTINGS) {
        const legacy = window.localStorage.getItem(k);
        if (legacy) { try { reader = { ...reader, ...JSON.parse(legacy) }; } catch {} break; }
      }
    }
    return {
      progress: raw.progress || {},
      bookmarks: raw.bookmarks || {},
      favorites: raw.favorites || [],
      reader,
    };
  } catch {
    return { ...emptySnapshot, reader: { ...defaultReader } };
  }
}

function getSnapshot() {
  if (typeof window === "undefined") return emptySnapshot;
  if (!clientSnapshot) clientSnapshot = read();
  return clientSnapshot;
}

function getServerSnapshot() {
  return emptySnapshot;
}

function subscribe(listener) {
  listeners.add(listener);
  return () => { listeners.delete(listener); };
}

function commit(next) {
  clientSnapshot = next;
  if (typeof window !== "undefined") {
    try { window.localStorage.setItem(KEY, JSON.stringify(next)); } catch {}
  }
  listeners.forEach((fn) => fn());
}

export const ReaderStore = {
  get: () => getSnapshot(),
  subscribe,

  getProgress(slug) { return getSnapshot().progress[slug] || null; },
  setProgress(slug, entry) {
    const s = getSnapshot();
    commit({ ...s, progress: { ...s.progress, [slug]: { ...entry, updatedAt: Date.now() } } });
  },
  history() {
    const s = getSnapshot();
    return Object.entries(s.progress)
      .map(([slug, p]) => ({ slug, ...p }))
      .sort((a, b) => b.updatedAt - a.updatedAt);
  },

  bookmarksFor(slug) { return getSnapshot().bookmarks[slug] || []; },
  isBookmarked(slug, id) { return (getSnapshot().bookmarks[slug] || []).some((b) => b.id === id); },
  toggleBookmark(slug, chapter) {
    const s = getSnapshot();
    const list = s.bookmarks[slug] || [];
    const exists = list.some((b) => b.id === chapter.id);
    const next = exists
      ? list.filter((b) => b.id !== chapter.id)
      : [...list, { id: chapter.id, number: chapter.number, title: chapter.title, href: chapter.href }]
          .sort((a, b) => a.number - b.number);
    commit({ ...s, bookmarks: { ...s.bookmarks, [slug]: next } });
  },

  isFavorite(slug) { return getSnapshot().favorites.includes(slug); },
  toggleFavorite(slug) {
    const s = getSnapshot();
    const next = s.favorites.includes(slug) ? s.favorites.filter((x) => x !== slug) : [...s.favorites, slug];
    commit({ ...s, favorites: next });
  },

  getReader() { return getSnapshot().reader; },
  setReader(patch) {
    const s = getSnapshot();
    commit({ ...s, reader: { ...s.reader, ...patch } });
  },
};

// Queries read only the snapshot that produced the current render; mutations
// stay on the shared imperative store so every subscriber sees one state.
function readerFacade(snapshot) {
  return {
    snapshot,
    get: () => snapshot,
    getProgress: (slug) => snapshot.progress[slug] || null,
    history: () => Object.entries(snapshot.progress)
      .map(([slug, p]) => ({ slug, ...p }))
      .sort((a, b) => b.updatedAt - a.updatedAt),
    bookmarksFor: (slug) => snapshot.bookmarks[slug] || [],
    isBookmarked: (slug, id) => (snapshot.bookmarks[slug] || []).some((b) => b.id === id),
    isFavorite: (slug) => snapshot.favorites.includes(slug),
    getReader: () => snapshot.reader,
    setProgress: ReaderStore.setProgress,
    toggleBookmark: ReaderStore.toggleBookmark,
    toggleFavorite: ReaderStore.toggleFavorite,
    setReader: ReaderStore.setReader,
  };
}

export function useReaderStore() {
  const snapshot = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  return useMemo(() => readerFacade(snapshot), [snapshot]);
}

export { defaultReader };
