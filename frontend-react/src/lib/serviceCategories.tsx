import type { ReactNode } from "react";
import { WasteIcon, WaterIcon, RoadsIcon, StreetlightIcon } from "../components/ServiceIcons";
import type { ServiceCategory } from "./ragTypes";
import { t, type LangCode } from "./i18n";

/**
 * Single source of truth for the 4 civic-service categories, shared by the citizen Home
 * service cards, the Report an Issue wizard (service selection + the mock AI-understanding
 * step's keyword match), and My Area. `id` is the real `ServiceCategory` enum value from the
 * RAG backend schema (see lib/ragTypes.ts) — the only thing that's ever client-only here is
 * which keywords hint at which category; the category id itself is backend-ready.
 */
export interface ServiceCategoryDef {
  id: ServiceCategory;
  icon: ReactNode;
  titleKey: string;
  descriptionKey: string;
  keywords: string[];
  /** CSS custom-property suffix for this service's color pair (--service-<color>/-bg),
   * mirroring the logo's own 4 service-color segments exactly (waste=green, water=blue,
   * roads=orange, streetlight=purple) — see the token block in global.css. */
  color: "waste" | "water" | "roads" | "streetlight";
}

export const SERVICE_CATEGORY_DEFS: ServiceCategoryDef[] = [
  {
    id: "WASTE_SANITATION",
    icon: <WasteIcon />,
    titleKey: "service.waste.title",
    descriptionKey: "service.waste.description",
    keywords: ["garbage", "waste", "trash", "sanitation", "dump", "litter"],
    color: "waste",
  },
  {
    id: "WATER_DRAINAGE",
    icon: <WaterIcon />,
    titleKey: "service.water.title",
    descriptionKey: "service.water.description",
    keywords: ["water", "leak", "drain", "sewage", "pipe", "flood"],
    color: "water",
  },
  {
    id: "ROADS_POTHOLES",
    icon: <RoadsIcon />,
    titleKey: "service.roads.title",
    descriptionKey: "service.roads.description",
    keywords: ["road", "pothole", "footpath", "pavement", "traffic"],
    color: "roads",
  },
  {
    id: "STREETLIGHTS",
    icon: <StreetlightIcon />,
    titleKey: "service.streetlight.title",
    descriptionKey: "service.streetlight.description",
    keywords: ["streetlight", "street light", "lamp", "pole", "electric"],
    color: "streetlight",
  },
];

/** Best-effort, client-side-only keyword match used solely to pre-fill the wizard's mock
 * "AI Understanding" step — never presented as a real backend classification. Returns null
 * when nothing matches rather than guessing, matching the same "don't fabricate" rule the
 * mock Ask JanMitra answers follow. */
export function guessServiceCategory(text: string): ServiceCategoryDef | null {
  const q = text.toLowerCase();
  return SERVICE_CATEGORY_DEFS.find((def) => def.keywords.some((k) => q.includes(k))) ?? null;
}

export function serviceCategoryLabel(lang: LangCode, id: ServiceCategory): string {
  const def = SERVICE_CATEGORY_DEFS.find((d) => d.id === id);
  return def ? t(lang, def.titleKey) : id;
}
