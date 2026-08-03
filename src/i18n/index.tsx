import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import en from "./en";
import zh from "./zh";
import type { I18nStrings } from "./en";

type Lang = "zh" | "en";

const strings: Record<Lang, I18nStrings> = { zh, en };

const STORAGE_KEY = "bioinformatics-workflows-lang";

function getInitialLang(): Lang {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "en" || stored === "zh") return stored;
  } catch {
    // localStorage unavailable
  }
  return "zh";
}

interface LangContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
}

const LangContext = createContext<LangContextValue>({
  lang: "zh",
  setLang: () => {},
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(getInitialLang);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    try {
      localStorage.setItem(STORAGE_KEY, l);
    } catch {
      // ignore
    }
  }, []);

  return (
    <LangContext.Provider value={{ lang, setLang }}>
      {children}
    </LangContext.Provider>
  );
}

export function useLanguage(): LangContextValue {
  return useContext(LangContext);
}

function getNestedValue(obj: Record<string, unknown>, path: string, params?: Record<string, string>): string {
  const keys = path.split(".");
  let current: unknown = obj;
  for (const key of keys) {
    if (current == null || typeof current !== "object") return path;
    current = (current as Record<string, unknown>)[key];
  }
  let result = typeof current === "string" ? current : path;
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      result = result.replace(`{${k}}`, v);
    }
  }
  return result;
}

export function useT(): (path: string, params?: Record<string, string>) => string {
  const { lang } = useContext(LangContext);
  const dict = strings[lang] as unknown as Record<string, unknown>;
  return useCallback(
    (path: string, params?: Record<string, string>) => getNestedValue(dict, path, params),
    [dict]
  );
}

export { strings };

export function useTagT(): (tag: string) => string {
  const { lang } = useContext(LangContext);
  const dict = strings[lang] as unknown as Record<string, unknown>;
  const translations = (dict.tagTranslations as Record<string, string>) || {};
  return useCallback(
    (tag: string) => translations[tag] || tag,
    [translations]
  );
}
