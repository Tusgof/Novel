"use client";

import { useEffect, useReducer } from "react";

// MoonRead client store — reading progress, bookmarks, favorites, history,
// and reader settings. Persists to localStorage; simple pub/sub for React.
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

const empty = { progress: {}, bookmarks: {}, favorites: [], reader: { ...defaultReader } };

let state = empty;
let hydrated = false;
const listeners = new Set();

function read() {
  if (typeof window === "undefined") return empty;
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
    return { ...empty, reader: { ...defaultReader } };
  }
}

function ensure() {
  if (!hydrated && typeof window !== "undefined") { state = read(); hydrated = true; }
  return state;
}

function commit(next) {
  state = next;
  if (typeof window !== "undefined") {
    try { window.localStorage.setItem(KEY, JSON.stringify(state)); } catch {}
  }
  listeners.forEach((fn) => fn());
}

export const ReaderStore = {
  get: () => ensure(),
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },

  getProgress(slug) { return ensure().progress[slug] || null; },
  setProgress(slug, entry) {
    const s = ensure();
    commit({ ...s, progress: { ...s.progress, [slug]: { ...entry, updatedAt: Date.now() } } });
  },
  history() {
    const s = ensure();
    return Object.entries(s.progress)
      .map(([slug, p]) => ({ slug, ...p }))
      .sort((a, b) => b.updatedAt - a.updatedAt);
  },

  bookmarksFor(slug) { return ensure().bookmarks[slug] || []; },
  isBookmarked(slug, id) { return (ensure().bookmarks[slug] || []).some((b) => b.id === id); },
  toggleBookmark(slug, chapter) {
    const s = ensure();
    const list = s.bookmarks[slug] || [];
    const exists = list.some((b) => b.id === chapter.id);
    const next = exists
      ? list.filter((b) => b.id !== chapter.id)
      : [...list, { id: chapter.id, number: chapter.number, title: chapter.title, href: chapter.href }]
          .sort((a, b) => a.number - b.number);
    commit({ ...s, bookmarks: { ...s.bookmarks, [slug]: next } });
  },

  isFavorite(slug) { return ensure().favorites.includes(slug); },
  toggleFavorite(slug) {
    const s = ensure();
    const next = s.favorites.includes(slug) ? s.favorites.filter((x) => x !== slug) : [...s.favorites, slug];
    commit({ ...s, favorites: next });
  },

  getReader() { return ensure().reader; },
  setReader(patch) {
    const s = ensure();
    commit({ ...s, reader: { ...s.reader, ...patch } });
  },
};

export function useReaderStore() {
  const [, force] = useReducer((x) => x + 1, 0);
  useEffect(() => {
    if (!hydrated) { state = read(); hydrated = true; force(); }
    return ReaderStore.subscribe(force);
  }, []);
  return ReaderStore;
}

export { defaultReader };
