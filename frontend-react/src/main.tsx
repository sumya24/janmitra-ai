import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./styles/global.css";
import App from "./App.tsx";
import { AuthProvider } from "./lib/auth";
import { UiLangProvider } from "./lib/uiLang";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <UiLangProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </UiLangProvider>
    </BrowserRouter>
  </StrictMode>
);
