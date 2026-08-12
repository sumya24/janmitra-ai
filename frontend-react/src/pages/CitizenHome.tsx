import { Link } from "react-router-dom";
import TopBar from "../components/TopBar";
import ServiceCard from "../components/ServiceCard";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { SERVICE_CATEGORY_DEFS } from "../lib/serviceCategories";

/** Citizen Home — the dashboard's landing screen (P0, Task 1 of the Phase 1 spec). Header is
 * the existing TopBar as-is (logo/profile/theme/language live there already — see TopBar.tsx);
 * this page adds the hero + the 4 service-category entry points + the Ask JanMitra CTA. */
export default function CitizenHome() {
  const { lang } = useUiLang();

  return (
    <div>
      <TopBar />
      <div className="page">
        <section className="home-hero enter">
          <h1 className="display">{t(lang, "home.hero.title")}</h1>
          <p>{t(lang, "home.hero.subtitle")}</p>
          <div className="home-hero-actions">
            <Link to="/citizen/report" className="btn btn-primary">
              {t(lang, "home.hero.reportCta")}
            </Link>
            <Link to="/citizen/ask" className="btn btn-ghost">
              {t(lang, "home.hero.askCta")}
            </Link>
          </div>
        </section>

        <div className="section-label">{t(lang, "home.servicesLabel")}</div>
        <div className="service-grid" style={{ marginBottom: 30 }}>
          {SERVICE_CATEGORY_DEFS.map((def, i) => (
            <div key={def.id} className="enter" style={{ "--stagger": i } as React.CSSProperties}>
              <ServiceCard
                icon={def.icon}
                title={t(lang, def.titleKey)}
                description={t(lang, def.descriptionKey)}
                actionLabel={t(lang, "home.serviceCard.action")}
                to={`/citizen/report?service=${def.id}`}
                color={def.color}
              />
            </div>
          ))}
        </div>

        <div className="surface-card" style={{ padding: 20, display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <div>
            <div style={{ fontWeight: 700, marginBottom: 4 }}>{t(lang, "home.trackPrompt.title")}</div>
            <div style={{ fontSize: 12.5, color: "var(--ink-2)" }}>{t(lang, "home.trackPrompt.body")}</div>
          </div>
          <Link to="/citizen/complaints" className="btn btn-ghost btn-sm">
            {t(lang, "nav.myComplaints")}
          </Link>
        </div>
      </div>
    </div>
  );
}
