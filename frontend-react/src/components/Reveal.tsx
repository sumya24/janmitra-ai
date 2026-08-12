import { useEffect, useRef, useState, type ReactNode } from "react";

/** Wraps content that should fade/rise into place the first time it scrolls into view, then
 * leaves it alone -- a one-shot reveal, not a repeated trigger on every scroll up/down, which
 * reads as gimmicky rather than purposeful. `stagger` offsets a group's entrances slightly
 * (see the --stagger custom property consumed by .enter in global.css) so a row of cards
 * settles in left-to-right/top-to-bottom instead of all at once. */
export default function Reveal({
  children,
  stagger = 0,
  as: Tag = "div",
  className = "",
  style,
}: {
  children: ReactNode;
  stagger?: number;
  as?: keyof React.JSX.IntrinsicElements;
  className?: string;
  style?: React.CSSProperties;
}) {
  const ref = useRef<HTMLElement | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    // Respect a browser without IntersectionObserver (very old) by just showing content.
    if (typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const tagStyle = {
    ...style,
    opacity: visible ? undefined : 0,
    transform: visible ? undefined : "translateY(8px)",
    "--stagger": stagger,
  } as React.CSSProperties;

  return (
    // @ts-expect-error -- ref typing across the union of intrinsic elements isn't worth narrowing here
    <Tag ref={ref} className={`${className} ${visible ? "enter" : ""}`.trim()} style={tagStyle}>
      {children}
    </Tag>
  );
}
