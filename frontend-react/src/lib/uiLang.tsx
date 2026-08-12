import { createContext, useContext, useState, type ReactNode } from "react";
import type { LangCode } from "./i18n";

const LANG_KEY = "janmitra.uiLang";

interface UiLangState {
  lang: LangCode;
  setLang: (lang: LangCode) => void;
}

const UiLangContext = createContext<UiLangState | null>(null);

export function UiLangProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<LangCode>(
    () => (localStorage.getItem(LANG_KEY) as LangCode) || "en"
  );

  function setLang(newLang: LangCode) {
    localStorage.setItem(LANG_KEY, newLang);
    setLangState(newLang);
  }

  return <UiLangContext.Provider value={{ lang, setLang }}>{children}</UiLangContext.Provider>;
}

export function useUiLang(): UiLangState {
  const ctx = useContext(UiLangContext);
  if (!ctx) throw new Error("useUiLang must be used within UiLangProvider");
  return ctx;
}
