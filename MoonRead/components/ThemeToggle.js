"use client";

import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

const storageKey = "moonread-site-theme";

export default function ThemeToggle() {
  const [theme, setTheme] = useState(() => {
    if (typeof window === "undefined") return "light";
    return window.localStorage.getItem(storageKey) || "light";
  });

  useEffect(() => {
    document.documentElement.dataset.siteTheme = theme;
    window.localStorage.setItem(storageKey, theme);
  }, [theme]);

  const nextTheme = theme === "dark" ? "light" : "dark";
  const label = theme === "dark" ? "สลับเป็นโหมดสว่าง" : "สลับเป็นโหมดมืด";

  return (
    <button className="theme-toggle" type="button" onClick={() => setTheme(nextTheme)} aria-label={label} title={label}>
      {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
      <span>{theme === "dark" ? "สว่าง" : "มืด"}</span>
    </button>
  );
}
