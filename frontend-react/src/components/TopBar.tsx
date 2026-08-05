import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import SettingsModal from "./SettingsModal";
import ThemeToggle from "./ThemeToggle";
import "./TopBar.css";

const ROLE_LABEL: Record<string, string> = { citizen: "Citizen", worker: "Worker", admin: "Super Admin" };

export default function TopBar({ title = "JanMitra AI", subtitle = "Municipal Grievance Redressal" }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showSettings, setShowSettings] = useState(false);

  function handleLogout() {
    navigate("/welcome");
    logout();
  }

  if (!user) return null;

  return (
    <>
      <div className="topbar">
        <div className="brand">
          <div className="seal">JM</div>
          <div>
            <div className="brand-word display">{title}</div>
            <div className="brand-tag">{subtitle}</div>
          </div>
        </div>
        <div className="whoami">
          <div className="avatar">{user.full_name.charAt(0).toUpperCase()}</div>
          <div>
            <div>{user.full_name}</div>
            <span className="role-pill">{ROLE_LABEL[user.role]}</span>
          </div>
          <ThemeToggle className="icon-btn" />
          <button className="icon-btn" aria-label="Settings" onClick={() => setShowSettings(true)}>
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
              <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" stroke="currentColor" strokeWidth="1.8" />
              <path
                d="M19.4 13.5a7.6 7.6 0 0 0 0-3l2-1.5-2-3.5-2.4.8a7.6 7.6 0 0 0-2.6-1.5L14 2h-4l-.4 2.3a7.6 7.6 0 0 0-2.6 1.5l-2.4-.8-2 3.5 2 1.5a7.6 7.6 0 0 0 0 3l-2 1.5 2 3.5 2.4-.8a7.6 7.6 0 0 0 2.6 1.5L10 22h4l.4-2.3a7.6 7.6 0 0 0 2.6-1.5l2.4.8 2-3.5-2-1.5Z"
                stroke="currentColor"
                strokeWidth="1.4"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>
      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} onLogout={handleLogout} />}
    </>
  );
}
