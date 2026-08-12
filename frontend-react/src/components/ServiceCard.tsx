import type { ReactNode } from "react";
import { Link } from "react-router-dom";

/** One of the four civic-service cards on the citizen Home screen. Each service gets its own
 * accent, mirroring the logo's own 4 service-color segments exactly (waste=green, water=blue,
 * roads=orange, streetlight=purple) via the --service-<color>/-bg token pair — see
 * lib/serviceCategories.tsx and the brand token block in global.css. Services are still told
 * apart by icon + name + description first; color is a reinforcing accent, never the only
 * differentiator (a color-blind user relying on icon+text alone loses nothing). */
export default function ServiceCard({
  icon,
  title,
  description,
  actionLabel,
  to,
  color,
}: {
  icon: ReactNode;
  title: string;
  description: string;
  actionLabel: string;
  to: string;
  color: "waste" | "water" | "roads" | "streetlight";
}) {
  return (
    <Link
      to={to}
      className={`service-card service-card-${color} surface-card hoverable`}
      aria-label={`${actionLabel}: ${title}`}
    >
      <div className="service-card-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      <span className="service-card-action">
        {actionLabel}
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
    </Link>
  );
}
