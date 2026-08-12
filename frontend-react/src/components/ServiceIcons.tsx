/** The four civic-service icons, drawn in the same hand-authored stroke language already used
 * throughout the app (rounded caps/joins, ~1.6-1.8px stroke, currentColor so they inherit
 * whatever color surrounds them in either theme) — deliberately not pulled from an icon
 * library, to stay visually consistent with the mic/translate/checkmark icons already in
 * Landing.tsx and elsewhere. Keep any future icon additions in this same stroke language. */

const commonProps = {
  width: 22,
  height: 22,
  viewBox: "0 0 24 24",
  fill: "none" as const,
};

export function WasteIcon() {
  return (
    <svg {...commonProps}>
      <path d="M9 3h6l.6 2H8.4L9 3Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
      <path d="M4.5 6.5h15" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path
        d="M6.5 6.5 7.3 20a1.6 1.6 0 0 0 1.6 1.5h6.2a1.6 1.6 0 0 0 1.6-1.5l.8-13.5"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path d="M10.3 10v7.5M13.7 10v7.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

export function WaterIcon() {
  return (
    <svg {...commonProps}>
      <path
        d="M12 2.5c2.4 3.4 5 6.9 5 10.2a5 5 0 0 1-10 0c0-3.3 2.6-6.8 5-10.2Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path d="M3.5 19.5h17M6 19.5v1.7M10 19.5v1.7M14 19.5v1.7M18 19.5v1.7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

export function RoadsIcon() {
  return (
    <svg {...commonProps}>
      <path d="M9 3 4 21M15 3l5 18" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M11.4 3h1.2l.4 4h-2l.4-4Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      <path d="M12.4 11.5v3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M12 17.5v3.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="9.6" cy="15.2" r="1.4" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  );
}

export function StreetlightIcon() {
  return (
    <svg {...commonProps}>
      <path d="M8.5 5.5a3.5 3.5 0 0 1 7 0c0 2-1.6 2.8-3.5 4-1.9-1.2-3.5-2-3.5-4Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
      <path d="M12 9.5v11.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M8.5 21h7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M9.3 3.6 8 2.3M14.7 3.6 16 2.3M8.3 6.3 6.8 6M15.7 6.3l1.5-.3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}
