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
      {/* Road edges receding into the distance, closed at the top with a short horizon so the
          shape doesn't read as two disconnected lines -- widened/heightened to match the visual
          weight of WasteIcon/WaterIcon (verified via rendered bounding-box measurement, not
          just eyeballed: previously 16x18 with a lot of empty interior, now ~17x19 with the
          centerline filling that interior). */}
      <path d="M8 3 3.5 21M16 3l4.5 18" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M10.6 3h2.8" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M12 7.5v2.8M12 13.5v2.8M12 19.3v1" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path
        d="M7.6 16.6c-.5-1 .1-2.1 1.2-2.3 1-.2 2 .3 2.3 1.2.3.9-.3 1.9-1.3 2.2-.9.3-1.8-.1-2.2-1.1Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function StreetlightIcon() {
  return (
    <svg {...commonProps}>
      {/* Widened lantern head + a wider base plate + longer light rays, same "lamp on a pole"
          concept as before but rebalanced to match the other three icons' visual weight
          (previously a 10.4-wide bounding box vs ~15-17 for the others -- confirmed via rendered
          bounding-box measurement -- now ~15 wide). */}
      <path
        d="M7 6a5 5 0 0 1 10 0c0 2.6-2.1 3.6-5 5.2C9.1 9.6 7 8.6 7 6Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path d="M12 11.2V20" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M7.5 20.5h9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path
        d="M8.5 3 7 1.5M15.5 3 17 1.5M6.3 6.8 4.5 6.3M17.7 6.8l1.8-.5"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinecap="round"
      />
    </svg>
  );
}
