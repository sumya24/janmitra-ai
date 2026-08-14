# Deliverable 1 — Service Data Requirements

Defines what each of the 4 civic service categories covers, so every
state/city research pass (Maharashtra pilot and the 9-state fan-out)
searches for the same scope consistently.

---

## 1. Waste & Public Sanitation

**Service ID prefix:** `waste`

**Sub-services / problem types:**
- Garbage collection (routine door-to-door/community bin collection)
- Missed garbage collection
- Illegal dumping
- Street / public-area cleanliness
- Public toilet sanitation
- Waste / debris removal (construction debris, bulk waste)
- General sanitation-related complaints

**Typical responsible authority:** Municipal Corporation / Municipal
Council's Solid Waste Management (SWM) department, often under a state
Urban Development / Housing & Urban Development Department policy
umbrella (many states now operate this under Swachh Bharat
Mission–Urban guidelines, which is why this category tends to have the
best-published SLAs/citizen charters nationally).

**What to look for:** citizen charter or SWM bye-law sections, published
collection schedules/frequency, complaint-to-resolution SLA, e-waste and
bulk-waste rules, penalties for illegal dumping (if published), the
official grievance channel (app, portal, helpline).

---

## 2. Water & Drainage

**Service ID prefix:** `water`

**Sub-services / problem types:**
- Water leakage (pipeline/tap leakage)
- No / low water supply
- Contaminated water
- Water pipeline problems (breakage, illegal tapping)
- Drain blockage
- Drain overflow
- Sewage / drainage problems

**Typical responsible authority:** varies more than any other category —
sometimes the Municipal Corporation's Water Supply & Sewerage
department, sometimes a separate state-level Water Board / Jal Board
with its own jurisdiction and grievance system (e.g. a state's Water
Supply and Sewerage Board vs. the city corporation). **This split must be
captured explicitly per city** — don't assume the municipal corporation
handles this if a separate board actually does.

**What to look for:** which specific authority handles which sub-service
(supply vs. sewerage/drainage is often split), published SLA for
leak/blockage response, water-quality complaint procedure, contact
channel(s) — there may be two different ones for supply vs. drainage.

---

## 3. Roads & Potholes

**Service ID prefix:** `roads`

**Sub-services / problem types:**
- Potholes
- Damaged roads
- Road maintenance (general)
- Broken footpaths
- Road obstruction / damage (fallen trees, construction debris blocking a road)

**Typical responsible authority:** Municipal Corporation's Public
Works Department (PWD) for city roads; state PWD for state highways
running through city limits — jurisdiction can split by road
classification (municipal road vs. state highway vs. national highway),
which should be noted if the source specifies it.

**What to look for:** published pothole-repair SLA (several states now
publish this, e.g. "X days from report"), the reporting channel
(dedicated pothole-reporting app/portal is common), photo-upload
requirement if any, jurisdiction split between municipal and state/NH
roads.

---

## 4. Streetlights

**Service ID prefix:** `streetlight`

**Sub-services / problem types:**
- Streetlight not working
- Damaged streetlight
- Damaged pole
- General lighting problems (dim/flickering, missing light on a stretch)

**Typical responsible authority:** Municipal Corporation's Electrical /
Street Lighting department, in some cities now via a Smart City /
ICCC (Integrated Command & Control Centre) integrated system, or in
smaller ULBs the responsibility can sit with the state electricity
distribution company (DISCOM) rather than the municipality.

**What to look for:** this category most often has **no discrete
published SLA** — flag as `SLA NOT FOUND` rather than assuming a
default. Check whether the city has a dedicated streetlight-complaint
channel (common in Smart City ICCC-integrated cities) vs. it being
folded into a general public-works complaint line.

---

## Cross-cutting fields researched for every service × location

Per `00_README.md`'s per-record template:
- Service info (name, description, problem types, sub-services)
- Responsibility (department, authority, officer/designation if published)
- Jurisdiction (state, district, city, municipality, zone, ward, any
  published jurisdiction rules — e.g. population-based ULB categories)
- Procedure (how citizens report — online/offline, steps, required info/docs)
- SLA / response & resolution time
- Escalation (levels, appellate authority, timeline)
- Contact/channel (portal, app, phone, email)
- Citizen guidance (FAQs, do's and don'ts, citizen responsibilities)
- Full source metadata (title, URL, organization, dates, source type)

## Data NOT collected under this research

Per `00_README.md` rule 6: no citizen/worker/complaint IDs, no JanSarthi
internal workflow data, no private citizen information. This research is
strictly public, official, government-published information.
