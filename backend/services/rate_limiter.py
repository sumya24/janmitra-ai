"""A small, in-process, stdlib-only sliding-window rate limiter.

Hand-rolled rather than a third-party package (slowapi/fastapi-limiter/etc.), matching this
codebase's existing preference for a small dependency surface -- see auth_service.py's own
docstring on why JWT is implemented directly against the stdlib for the same reason. This is
genuinely simple logic (count recent timestamps per identifier, evict old ones), and keeping it
in-house means no new supply-chain dependency and no new behavior to trust blindly.

**Storage: in-process memory, not shared/distributed.** Correct and sufficient for this project's
actual deployment -- `docker-compose.prod.yml` runs exactly one `uvicorn` process, no
`--workers`/gunicorn multi-process setup (confirmed directly against that file and
backend/Dockerfile's CMD) -- so there is only ever one counting process to begin with. If this
deployment ever moves to multiple backend processes/replicas, each would keep its own independent
counters and the *effective* limit would multiply by the process count -- documented here rather
than silently assumed away. A shared store (Redis, etc.) would be required at that point; adding
one now, for a single-process deployment, would be exactly the kind of unneeded infrastructure
this project's own constraints ask not to introduce.

**Sliding window, not fixed window**: a fixed window (e.g. "reset every :00 seconds") allows a
burst of up to 2x the limit right at the window boundary (limit requests just before the reset,
limit again just after). This implementation instead keeps each identifier's actual recent
request timestamps and only counts ones still within the trailing `window_seconds` -- correct at
every point in time, not just at window edges.

**Bounded memory, not unbounded**: every call opportunistically evicts THIS identifier's own
expired timestamps -- but an identifier that simply stops appearing (e.g. a one-time visitor)
would otherwise leave its now-stale entry sitting in the dict forever, since nothing ever revisits
a key nobody asks about again. A periodic full sweep (see `_SWEEP_INTERVAL_SECONDS`) also purges
any OTHER identifier's now-fully-expired entry, throttled so it doesn't turn every request into an
O(all identifiers) scan -- amortized cost stays cheap, and memory stays bounded by "identifiers
seen within roughly the last sweep interval", never "every identifier ever seen" over the
process's entire lifetime.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

# How often check() also sweeps the WHOLE dict for other identifiers' fully-expired entries (not
# just the one being checked right now) -- see module docstring. A handful of minutes keeps the
# dict from growing forever while staying cheap: this only runs a full-dict scan roughly once per
# interval, not on every single request.
_SWEEP_INTERVAL_SECONDS = 300.0


class RateLimiter:
    """A named sliding-window limiter (e.g. one instance for login attempts, a separate one for
    AI requests) -- separate instances never share state, so a citizen hitting the AI limit can't
    affect anyone's login attempts and vice versa. Thread-safe: FastAPI's sync routes run in a
    threadpool, so concurrent requests can genuinely call `check()` from different threads at
    once."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()
        self._last_sweep = time.monotonic()

    def check(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        """Records one attempt for `key` and reports whether it's allowed under `limit` per
        `window_seconds`.

        Returns:
            (allowed, retry_after_seconds). `retry_after_seconds` is 0 when allowed, otherwise a
            whole-second estimate of how long until the oldest counted hit ages out of the
            window (used for the 429 response's `Retry-After` header) -- an estimate, not a
            guarantee, since other requests can still be made in the meantime.
        """
        if limit <= 0:
            # A misconfigured (zero/negative) limit means "always block" -- honor that without
            # touching the timestamp deque at all, so there's no empty-deque edge case below.
            return False, window_seconds

        now = time.monotonic()
        cutoff = now - window_seconds

        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] <= cutoff:
                hits.popleft()

            if len(hits) >= limit:
                # hits is non-empty here: len(hits) >= limit >= 1.
                retry_after = max(1, int(hits[0] + window_seconds - now) + 1)
                self._sweep_if_due(now, window_seconds)
                return False, retry_after

            hits.append(now)
            self._sweep_if_due(now, window_seconds)
            return True, 0

    def _sweep_if_due(self, now: float, window_seconds: int) -> None:
        """Must be called while `self._lock` is already held. Purges every identifier whose
        entries are now fully expired -- not just the one `check()` was called for -- so a client
        that stops appearing entirely doesn't leave a permanent, never-revisited entry behind. A
        single `window_seconds` cutoff for the whole dict is an approximation (different callers
        may use different windows against the same limiter instance in theory, though this
        project's two limiters each only ever use their own fixed config value) -- fine for a
        purely memory-bounding sweep, not the authoritative per-key expiry check `check()` itself
        already does correctly above."""
        if now - self._last_sweep < _SWEEP_INTERVAL_SECONDS:
            return
        self._last_sweep = now
        cutoff = now - window_seconds
        stale_keys = [key for key, hits in self._hits.items() if not hits or hits[-1] <= cutoff]
        for key in stale_keys:
            del self._hits[key]

    def reset(self) -> None:
        """Clears all state -- test-only helper, so each test starts with a clean limiter instead
        of depending on execution order/timing to age old hits out."""
        with self._lock:
            self._hits.clear()
