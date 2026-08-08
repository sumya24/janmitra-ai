# Authentication — Passwords, JWTs, and Roles, from the Ground Up

*Written for someone who wants to actually understand this, not just skim it — including "why did you build it this way" answers you could give in an interview.*

> Part of the JanMitra AI documentation set. See [`README.md`](../README.md) for the full index of every document.

---

## 1. The problem authentication solves

Two separate questions, easy to blur together but genuinely different:

- **Authentication** — "who are you?" (proving your identity, usually with a password)
- **Authorization** — "are you allowed to do this?" (once we know who you are, what can you actually access?)

JanMitra AI handles authentication via phone number + password, and authorization via a `role` (citizen/worker/admin) attached to your account. Both are implemented in [`backend/services/auth_service.py`](../backend/services/auth_service.py) and enforced in [`backend/deps.py`](../backend/deps.py).

---

## 2. Passwords: why you never store the real one

If you store a user's actual password in the database and that database ever leaks, every user's real password leaks with it — and because people reuse passwords, that's not just a problem for this app, it's a problem for every other account that person used the same password on.

The fix: **hash** the password before storing it. A hash function turns "correcthorsebatterystaple" into something like `$2b$12$KIXQ...` — a one-way transformation that's practically impossible to reverse. To check a login attempt, you hash the *attempt* and compare it to the *stored hash* — the real password is never stored anywhere, ever, not even briefly in the database.

```python
# backend/services/auth_service.py
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
```

**Why `bcrypt` specifically, not something like plain SHA-256?** This is a genuinely important interview-level distinction. A general-purpose hash function like SHA-256 is *fast* — which is exactly the wrong property for a password hash. Fast hashing means an attacker with a stolen database of hashes can try billions of password guesses per second against it. `bcrypt` is deliberately, tunably **slow** (it has a "cost factor" built in), which makes large-scale guessing attacks impractical even if the hashed data leaks. It also automatically generates and stores a random **salt** per password (`bcrypt.gensalt()`), so two users with the same password get completely different hashes — defeating precomputed "rainbow table" attacks.

---

## 3. What a JWT actually is

**JWT** stands for JSON Web Token. It's a compact, **signed** piece of text that encodes some claims (like "user 12, role citizen") in a way that can't be tampered with, without needing the server to remember anything about active sessions.

A JWT has three parts, separated by dots: `header.payload.signature` — for example:
```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMiIsInJvbGUiOiJjaXRpemVuIn0.4f3a...
└── header ──────────┘└── payload ─────────────────────────┘└ signature ┘
```

- **Header** — which algorithm was used to sign it (`HS256` here).
- **Payload** — the actual claims: who this token is for, their role, when it expires. **This part is only encoded, not encrypted** — anyone can decode and read it (it's just base64). Never put a secret *inside* a JWT's payload; the security comes from the signature, not from the payload being hidden.
- **Signature** — a cryptographic proof, computed from the header+payload plus a **secret key only the server knows**, that the token wasn't tampered with. Change even one character of the payload, and the signature no longer matches — the server rejects it immediately.

**Why JWTs instead of traditional server-side sessions?** This is one of the most common "explain your architecture" interview questions. With traditional sessions, the server stores a session ID in memory or a database, and the browser just holds that ID in a cookie — the server has to look up "what does session ID X mean" on every request. With JWTs, **all the information is in the token itself** — the server can verify it's genuine (via the signature) without storing anything or querying a database, just by checking the signature and reading the payload. This makes JWTs a natural fit for APIs that might eventually run across multiple server instances (no shared session store needed) — though the honest trade-off is that a JWT can't be instantly revoked before it expires, unlike a server-side session you can just delete.

---

## 4. How this codebase implements JWTs — and a real interview talking point

Most projects reach for a library like `PyJWT`. This one **doesn't** — `auth_service.py` implements JWT creation and verification directly against Python's standard library (`hmac`, `hashlib`, `json`, `base64`), and says exactly why in its own docstring:

> "JWTs are implemented directly against the standard library (HS256 only) rather than a third-party JWT package, since this project only ever needs to verify tokens it issued itself with one shared secret — no external issuers, no key rotation, no asymmetric signing. This keeps the dependency surface small."

This is worth understanding well because it's a genuinely good, defensible engineering decision to be able to explain, not just a curiosity:

- A full JWT library supports many algorithms, external token issuers, key rotation, asymmetric (public/private key) signing — real complexity that exists to solve problems this app doesn't have. This app only ever issues its own tokens and verifies them with the one secret it already holds.
- Implementing the (much smaller) actual need directly means **one fewer third-party dependency** to keep updated and trust, for a well-understood, ~100-line piece of code that can be read and audited in full.
- The trade-off, worth stating honestly: hand-rolling security-adjacent code is *usually* a bad idea — you're one bug away from creating a real vulnerability. This is only defensible because (a) it's simple enough to actually reason about completely, (b) it uses `hmac.compare_digest()` for the signature check specifically to avoid **timing attacks** (see below), and (c) it's thoroughly tested (see [`docs/TESTING.md`](TESTING.md), including property-based tests). A more complex auth scheme should absolutely use a battle-tested library instead.

### The signature check, and why `hmac.compare_digest` matters

```python
if not hmac.compare_digest(expected_signature, actual_signature):
    raise InvalidTokenError("Invalid token signature.")
```

A naive `expected_signature == actual_signature` in Python compares byte-by-byte and **returns as soon as it finds a mismatch** — which means comparing a totally-wrong signature is measurably faster than comparing an almost-right one. An attacker who can measure response times precisely could, in theory, exploit that timing difference to guess the correct signature one byte at a time — a **timing attack**. `hmac.compare_digest` always takes the same amount of time regardless of how much of the two values matches, closing that hole. This is exactly the kind of small, specific detail that separates "I copied JWT code from a tutorial" from "I understand what I built" in an interview.

---

## 5. The request lifecycle: from header to authorized action

1. Login succeeds → `create_access_token(user)` builds a JWT containing `sub` (the user's ID), `role`, `iat` (issued-at), and `exp` (expiry, `JWT_EXPIRE_MINUTES` from now — 24 hours by default).
2. The frontend stores this token (`localStorage`, see [`docs/FRONTEND.md`](FRONTEND.md)) and sends it back as `Authorization: Bearer <token>` on every request from then on.
3. `deps.get_current_user` reads that header, calls `decode_access_token`, which verifies the signature and checks `exp` hasn't passed, then looks up the real `User` row by the `sub` claim.
4. `deps.require_role("admin")` (or any role) wraps `get_current_user` and additionally checks the resolved user's `role` is in the allowed list, rejecting with `403 Forbidden` otherwise.

This is FastAPI's **dependency injection** at work — a route just declares `admin: User = Depends(require_role("admin"))` as a parameter, and all of the above happens automatically before the route's own code runs at all. See [`docs/BACKEND.md`](BACKEND.md) for more on this pattern.

---

## 6. Authorization: three roles, enforced two ways

- **Route-level** — `require_role(...)` blocks an entire endpoint from the wrong role before any of its logic runs (e.g., only `admin` can reach `POST /admin/workers`).
- **Row-level** — inside a route, an explicit ownership check (e.g., `_get_owned_complaint` in `routes/complaints.py`) confirms a specific *record* belongs to the caller, not just that their role is generally allowed — a worker being allowed to accept complaints in general doesn't mean they should be able to accept *any* complaint's ID they happen to guess.

**Why there's no way to self-register as a worker or admin, at all, anywhere:** this isn't an oversight — `routes/auth.py`'s sign-up endpoint has no `role` field in its request model whatsoever, so there is no code path, no matter what a malicious client sends, that can result in anything but a citizen account. The very first admin account is planted directly into the database by a script (`scripts/seed_admin.py`), run by whoever is setting the system up — never through the running application itself. This is a strong, simple security property: "can an attacker escalate their own privileges through the API" has a provably-no answer, because the capability doesn't exist in the API surface at all.

---

## Likely interview questions about this part of the project

**"Why JWTs instead of sessions?"** — stateless verification (no server-side session store needed), a natural fit for an API consumed by a separate frontend. Trade-off: can't be instantly revoked before expiry, unlike deleting a server-side session. See [§3](#3-what-a-jwt-actually-is).

**"How do you store passwords?"** — bcrypt, never the plaintext, with bcrypt chosen specifically for being deliberately slow (resists brute-force) and self-salting (resists rainbow tables), unlike a fast general-purpose hash. See [§2](#2-passwords-why-you-never-store-the-real-one).

**"Why didn't you use a JWT library?"** — the app's actual need (self-issued tokens, one shared secret, no key rotation) is a small subset of what a full library solves for; implementing it directly against the standard library keeps the dependency surface small and the whole implementation auditable. Trade-off acknowledged: this is only defensible because it's simple, uses `hmac.compare_digest` to avoid timing attacks, and is well-tested. See [§4](#4-how-this-codebase-implements-jwts--and-a-real-interview-talking-point).

**"How do you prevent privilege escalation?"** — there is no code path anywhere in the API that can create a worker or admin account; sign-up's request model has no `role` field at all. The first admin is seeded directly into the database, outside the running application. See [§6](#6-authorization-three-roles-enforced-two-ways).

**"What's a timing attack, and where does it matter in your code?"** — see the `hmac.compare_digest` explanation in [§4](#4-how-this-codebase-implements-jwts--and-a-real-interview-talking-point). A genuinely great detail to bring up unprompted.

---

*Related reading: [`docs/BACKEND.md`](BACKEND.md), [`docs/DATABASE.md`](DATABASE.md), [`docs/TESTING.md`](TESTING.md).*
