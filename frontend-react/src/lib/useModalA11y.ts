import { useEffect, useRef } from "react";

/** Minimal shared accessibility behavior for the app's overlay/.modal dialogs -- ConfirmModal.tsx
 * and the ~10 other workflow modals built on the same .overlay/.modal CSS pair (TopBar.css),
 * none of which had any of this before (confirmed by grepping the whole components/ directory).
 * Rather than duplicate this in every modal, or build a full shared <Modal> wrapper component
 * (a bigger change than this pass calls for -- each modal's body/actions still vary), this is the
 * one small hook every modal calls, attaching the returned ref to its own outer ".modal" div.
 *
 * Provides the three things a modal dialog needs that a plain div doesn't get for free:
 * 1. Moves focus into the modal on open, and returns it to whatever had focus before (the
 *    trigger button) on close -- without this, focus silently stays on/near a now-hidden
 *    trigger, or resets to <body>, disorienting for keyboard/screen-reader users.
 * 2. Traps Tab/Shift+Tab within the modal's own focusable elements while open, so tabbing
 *    doesn't silently leave the dialog into page content sitting behind the dimmed backdrop.
 * 3. Closes on Escape, the standard dialog-dismissal key.
 *
 * Pair with role="dialog" aria-modal="true" on the same element (a static attribute the caller
 * already controls directly, not worth threading through this hook).
 */
export function useModalA11y(onClose: () => void) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    const container = ref.current;

    function focusableElements(): HTMLElement[] {
      if (!container) return [];
      return Array.from(
        container.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ),
      ).filter((el) => el.offsetParent !== null);
    }

    // Move focus into the dialog -- the first focusable element if there is one, otherwise the
    // container itself (it has tabIndex=-1 from the caller so it can still take focus).
    const initial = focusableElements();
    (initial[0] ?? container)?.focus();

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
        return;
      }
      if (e.key !== "Tab") return;
      const items = focusableElements();
      if (items.length === 0) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      previouslyFocused?.focus?.();
    };
    // Deliberately empty deps: this should run exactly once for this modal's lifetime (mount to
    // unmount), matching how every caller already mounts/unmounts the whole component on
    // open/close rather than toggling a visibility prop -- re-running mid-life on an onClose
    // identity change would re-grab focus/re-capture "previously focused" mid-interaction.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return ref;
}
