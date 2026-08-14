# Tamil Nadu — Official Source Inventory

**Cities researched:** Chennai (Greater Chennai Corporation, GCC),
Coimbatore (Coimbatore City Municipal Corporation, CCMC), Madurai
(Madurai City Municipal Corporation)
**Method:** WebSearch only — WebFetch (direct page-fetch/verification) is
unavailable in this environment for the entire duration of this research
pass. Every record below is marked `NOT INDEPENDENTLY FETCHED` in
`verification_status` as a result. `source_quality` reflects how
official/specific the *domain and search-result context* is, per the
`00_README.md` rubric — it is not a substitute for having actually opened
and read the page.

> **Environment note:** This entire pass relies on WebSearch result
> metadata (URL, title, and a search-engine-generated summary of
> snippets) rather than fetching and reading full page content. Anything
> presented here as an official-domain URL is genuinely real and
> currently indexed — but exact wording (SLA day-counts, escalation
> chains, officer titles) should be treated as **reported-by-search, not
> confirmed-by-direct-read**, until someone with working fetch access (or
> a person) opens the URL directly. This caveat applies to every record
> below. No `source_quality: A` is assigned anywhere a specific
> numeric SLA/day-count could only be traced to a non-government domain
> (news sites, complaint aggregators, consumer-complaint sites) — those
> figures are logged only in `notes`, clearly labeled as third-party/
> unverified, with `sla`/`escalation_procedure` left at their sentinel
> values.

---

## Summary table

| State | City | Service | Source | Authority | URL | Format | Data Available | RAG or SQL | Quality |
|---|---|---|---|---|---|---|---|---|---|
| Tamil Nadu | Chennai | All services (complaint portal) | Public Grievance and Redressal System (PGR) | Greater Chennai Corporation (GCC) | https://chennaicorporation.gov.in/gcc/complaints/ | HTML | Procedure, channels | RAG | B |
| Tamil Nadu | Chennai | All services (PGR web app) | GCC Public Grievance Redressal — citizen registration | Greater Chennai Corporation | https://erp.chennaicorporation.gov.in/pgr/citizen/BeforeReg.do | Web form | Procedure, tracking | RAG | B |
| Tamil Nadu | Chennai | Roads & Potholes / Drainage | Integrated Storm Water Drain — GCC department page | Greater Chennai Corporation | https://chennaicorporation.gov.in/gcc/department/storm-water/ | HTML | Department info, jurisdiction | RAG | B |
| Tamil Nadu | Chennai | Water & Drainage | Complaints and Grievance — CMWSSB | Chennai Metropolitan Water Supply and Sewerage Board (CMWSSB), NOT GCC | https://cmwssb.tn.gov.in/complaints-grievance | HTML | Procedure, channels | RAG | B |
| Tamil Nadu | Chennai | Water & Drainage | Citizen's Charter — CMWSSB | Chennai Metropolitan Water Supply and Sewerage Board | https://cmwssb.tn.gov.in/citizencharter | HTML | Charter existence confirmed; specific SLA text not extracted | RAG | B |
| Tamil Nadu | Chennai | Water & Drainage | Complaint Redressal — CMWSSB | Chennai Metropolitan Water Supply and Sewerage Board | https://cmwssb.tn.gov.in/complaint-redressal | HTML | Procedure (SMS notification to Depot Engineer within 3 min) | RAG | B |
| Tamil Nadu | Chennai | Waste & Sanitation | Solid Waste Management : Chennai (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via tn.data.gov.in | https://tn.data.gov.in/catalog/solid-waste-management-chennai-6 | Dataset (catalog) | Source segregation, D2D efficiency, bin placement, vehicle capacity | Structured/SQL | C |
| Tamil Nadu | (state-wide, applies to all ULBs) | Waste & Sanitation | Vehicles and Land used for Solid Waste Management | data.gov.in OGD Platform India | https://www.data.gov.in/catalog/vehicles-and-land-used-solid-waste-management | Dataset | Vehicle counts, compost-yard land area, per-ULB (Tamil Nadu-wide) | Structured/SQL | C |
| Tamil Nadu | (state-wide) | All services (Directorate of Municipal Administration) | tnurbantree.tn.gov.in — Urban e-Governance / Government Orders | Directorate of Municipal Administration, Tamil Nadu (covers all municipalities/corporations except Chennai) | https://www.tnurbantree.tn.gov.in/ | HTML | Portal hosting per-ULB citizen charters | RAG | B |
| Tamil Nadu | Coimbatore | All services (citizen charter) | Coimbatore City Municipal Corporation Citizen's Charter (PDF) | Coimbatore City Municipal Corporation (CCMC) | https://ccmc.gov.in/img/upload/CitizensCharterEnglish1.pdf | PDF | Service descriptions, published SLA schedule referenced, 3-step complaint redressal system | RAG | A |
| Tamil Nadu | Coimbatore | All services (citizen charter, HTML) | Citizen Charter — Coimbatore City Municipal Corporation | CCMC | https://ccmc.gov.in/index.php/administration/citizen-charter | HTML | Charter existence, links to PDF | RAG | A |
| Tamil Nadu | Coimbatore | All services (grievance registration) | Grievance Registration — CCMC | CCMC | https://payment.ccmc.gov.in/frmGrievancesRegistration.asp | Web form | Channel, tracking (repGrievances.asp) | RAG | B |
| Tamil Nadu | Coimbatore | Waste & Sanitation | Solid Waste Management : Coimbatore (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in | https://www.data.gov.in/catalog/solid-waste-management-coimbatore | Dataset (catalog) | Source segregation, D2D efficiency, bin placement, vehicle capacity | Structured/SQL | C |
| Tamil Nadu | Madurai | All services (citizen charter) | Citizen Charter — Madurai Corporation | Madurai City Municipal Corporation, hosted via tnurbantree.tn.gov.in (Directorate of Municipal Administration) | https://www.tnurbantree.tn.gov.in/madurai/citizen-charter/ | HTML | Charter existence confirmed; lists Mayor/Deputy Mayor/councillor contacts and key-official designations | RAG | B |
| Tamil Nadu | Madurai | All services (grievance channel, district) | How to lodge your Grievance — Madurai District | District Administration, Madurai (Government of Tamil Nadu, NIC) | https://madurai.nic.in/service/how-to-lodge-a-grievance/ | HTML | Procedure, escalation reference | RAG | B |
| Tamil Nadu | Madurai | Waste & Sanitation | Solid Waste Management : Madurai (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in | https://www.data.gov.in/catalog/solid-waste-management-madurai | Dataset (catalog) | Source segregation, D2D efficiency, bin placement, vehicle capacity | Structured/SQL | C |
| Tamil Nadu | (state-wide) | All services (state escalation) | Tamil Nadu e-Sevai Portal (TNeGA) | Tamil Nadu e-Governance Agency | https://tnega.tn.gov.in/projects/e-sevai | HTML | Channel (Common Service Centre delivery) | RAG | B |
| Tamil Nadu | Chennai | (reference only, not verified fact source) | complainthub.org — GCC complaint guide | Third-party (not government) | https://complainthub.org/gcc-chennai/ | HTML | Aggregated complaint-channel info, unverifiable claims | reference only | D |
| Tamil Nadu | Madurai | (reference only, not verified fact source) | complainthub.org — Madurai Municipal Corporation complaint guide | Third-party (not government) | https://complainthub.org/madurai-municipal-corporation/ | HTML | Aggregated complaint-channel info, unverifiable claims | reference only | D |
| Tamil Nadu | Madurai | (reference only, not verified fact source) | mducorpicts.com — Madurai Corporation new-complaint web form | Private ICT vendor domain (non-.gov.in; functions as MCC's outsourced e-gov front-end) | https://www.mducorpicts.com/Public/Newgrievance.aspx | Web form | Channel — functionally used by the corporation, but domain is not an official government domain | reference only | D |

---

## Full records

### Record: TamilNadu-Chennai-Waste-GCCComplaints
```
service_id: tn-chennai-waste-gcc-complaints
service_name: Waste & Public Sanitation
sub_service: Garbage collection, solid waste management complaints
problem_type: garbage_collection

state: Tamil Nadu
district: Chennai
city: Chennai
municipality: Greater Chennai Corporation (GCC)
zone: NOT FOUND IN OFFICIAL SOURCE (GCC operates multiple zones; not tied to a specific zone document in this pass)
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (Solid Waste Management wing of GCC, inferred; exact department name not confirmed on an official page)
authority: Greater Chennai Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GCC's Public Grievance Redressal (PGR) system and the "Namma Chennai" mobile app (jointly developed with Chennai Smart City Limited) accept solid-waste-management complaints alongside potholes, streetlights, storm-water drains, and stray-dog issues, with photo upload and complaint-number tracking.
procedure: Take a photo of the issue and submit via the Namma Chennai app, or register online at GCC's PGR portal; receive a Complaint Number for tracking.
required_information: Photo of the issue, location
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Citizen Helpline 1913, online portal (erp.chennaicorporation.gov.in/pgr/citizen/BeforeReg.do), Namma Chennai mobile app, postal mail to The Commissioner, GCC, Ripon Building, EVR Salai, Chennai–600003
contact_information: 1913 (citizen helpline); +91-44-25619206 / +91-44-25303511 (general help)

escalation_procedure: ESCALATION INFORMATION NOT FOUND (GCC-specific escalation chain not surfaced in this pass)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Welcome to Greater Chennai Corporation — Complaints
source_url: https://chennaicorporation.gov.in/gcc/complaints/
source_type: govt_portal
source_organization: Greater Chennai Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Multiple complaint channels confirmed as genuinely official (chennaicorporation.gov.in and erp.chennaicorporation.gov.in domains); exact per-category SLA and escalation chain were not surfaced and need direct-fetch confirmation.
```

### Record: TamilNadu-Chennai-Roads-StormWaterDrain
```
service_id: tn-chennai-roads-storm-water
service_name: Roads & Potholes
sub_service: Road maintenance, pothole repair, storm-water drainage (jurisdiction overlaps Water & Drainage category)
problem_type: potholes

state: Tamil Nadu
district: Chennai
city: Chennai
municipality: Greater Chennai Corporation (GCC)
zone: NOT FOUND IN OFFICIAL SOURCE (Chennai is divided into 4 watershed basins with 12 major watersheds for storm-water planning purposes, per this department page — not the same as GCC's administrative zones)
ward: NOT FOUND IN OFFICIAL SOURCE

department: GCC Roads department (maintenance of roads, pothole repair, new road construction) and a separate Integrated Storm Water Drain department/scheme
authority: Greater Chennai Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GCC's Roads department handles road maintenance and pothole repair; a related but organizationally distinct Storm Water Drain program has completed approximately 345 km of drains under JnNURM funding (core city) to reduce monsoon flooding/water stagnation, given the city's low average elevation (~2.0m above mean sea level).
procedure: Report via GCC's PGR portal or Namma Chennai app (photo + location), same general channel as other GCC civic complaints.
required_information: Photo of the issue, location
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Namma Chennai app, GCC PGR portal, Citizen Helpline 1913
contact_information: 1913

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Integrated Storm Water Drain — Greater Chennai Corporation
source_url: https://chennaicorporation.gov.in/gcc/department/storm-water/
source_type: govt_portal
source_organization: Greater Chennai Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Roads (potholes) and storm-water drainage are handled as organizationally distinct functions within GCC in Chennai, unlike the simpler single-department pattern seen for some other cities — worth flagging for schema design (this record spans both "Roads & Potholes" and "Water & Drainage" categories). A news source (citizenmatters.in, third-party — not used as a fact source here) separately reported that newly-laid Chennai roads are frequently re-dug by other agencies shortly after completion, delaying pothole fixes; this is contextual only, not a verified official claim.
```

### Record: TamilNadu-Chennai-Water-CMWSSB
```
service_id: tn-chennai-water-cmwssb
service_name: Water & Drainage
sub_service: Water supply, sewerage/drainage complaints
problem_type: no_low_water_supply

state: Tamil Nadu
district: Chennai
city: Chennai
municipality: Greater Chennai Corporation (GCC) — but water supply & sewerage is NOT handled by GCC; see notes
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Chennai Metropolitan Water Supply and Sewerage Board (CMWSSB / "Chennai Metro Water") — a separate statutory board, not a GCC department
authority: Chennai Metropolitan Water Supply and Sewerage Board
officer_designation: Depot Engineer / Senior Accounts Officer (named as the staff notified via SMS when a complaint is registered, per CMWSSB's own complaint-redressal page); specific individual NOT FOUND IN OFFICIAL SOURCE

description: CMWSSB is the dedicated statutory board for Chennai's water supply and sewerage — a clear jurisdiction split from GCC (the municipal corporation), consistent with the pattern flagged in 01_service_data_requirements.md. CMWSSB published its own Citizen's Charter in 1998 (approved by Govt. of Tamil Nadu Order No. 58, MAWS Department, dated 16 April 1998), covering water supply and sewerage services, citizen rights, and citizen responsibilities.
procedure: Register complaint via the CMWSSB website; a Complaint Registration Number is sent by SMS; the complaint is simultaneously communicated to the Depot Engineer/Senior Accounts Officer by SMS within a maximum of 3 minutes, per CMWSSB's own complaint-redressal page.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — CMWSSB's own complaint-redressal page states that its complaint-monitoring system is "linked with the maximum time limit for redressal given in the Citizen Charter," but the specific day-count figures were not surfaced by search in this pass (the Citizen Charter document itself was not directly read).
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: CMWSSB website (cmwssb.tn.gov.in), national helpline 14420 (24x7), toll-free 1916, social media (monitored by a dedicated team per the complaint-redressal page)
contact_information: 14420 (24x7 national helpline); 1916 (toll-free)

escalation_procedure: ESCALATION INFORMATION NOT FOUND — a claim that unresolved complaints can be escalated to a "Consumer Grievances Redressal Forum (CGRF)" within 90 days appeared in search results, but could not be confidently attributed to a cmwssb.tn.gov.in page as opposed to a third-party summary in this pass; treat as unverified until directly confirmed.
escalation_authority: NOT FOUND IN OFFICIAL SOURCE (see CGRF caveat above)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Complaints and Grievance | CMWSSB
source_url: https://cmwssb.tn.gov.in/complaints-grievance
source_type: govt_portal
source_organization: Chennai Metropolitan Water Supply and Sewerage Board

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: **Important jurisdiction-split finding**: for Chennai, water supply and sewerage is run by CMWSSB, a separate state statutory board — **not** GCC. Any JanSarthi routing logic for Chennai water/drainage complaints must point to CMWSSB channels (14420 / 1916 / cmwssb.tn.gov.in), not GCC's Namma Chennai/PGR system. CMWSSB's own Citizen's Charter (in force since 1998, per a government order) is a strong candidate for a future quality-A record once its content can be directly fetched and read — this pass only confirmed the charter's existence and 1998 origin, not its specific SLA text, so it is kept at B rather than A here.
```

### Record: TamilNadu-Chennai-AllServices-GCCandStateEscalation
```
service_id: tn-chennai-all-escalation
service_name: (cross-cutting — escalation applies to all 4 categories)
sub_service: Public grievance escalation
problem_type: multiple

state: Tamil Nadu
district: Chennai
city: Chennai
municipality: Greater Chennai Corporation (GCC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Greater Chennai Corporation (city level); Tamil Nadu CM Helpline / IIPGCMS (state level, fallback)
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GCC's own PGR system issues a trackable complaint number per submission (confirmed via GCC's own X/Twitter account replying with complaint numbers to citizens, e.g. format "2025-364GDI"). At the state level, Tamil Nadu's Integrated and Inclusive Public Grievance CM Helpline Management System (IIPGCMS / "CM Helpline") accepts complaints about civic issues and local urban bodies including municipal corporations, usable as a fallback escalation channel if GCC's own process is unsatisfactory.
procedure: File with GCC's PGR system first; if unresolved or unsatisfactory, approach the Chief Minister's Office (CMO) or relevant regulatory/statutory authority via the state CM Helpline system.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: GCC PGR (erp.chennaicorporation.gov.in/pgr), Citizen Helpline 1913; state-level TN CM Helpline / IIPGCMS
contact_information: 1913 (GCC); TN CM Helpline (specific phone number NOT FOUND IN OFFICIAL SOURCE in this pass)

escalation_procedure: If a GCC PGR complaint is not resolved to the citizen's satisfaction, the citizen may approach the Chief Minister's Office (CMO) or the relevant regulatory/statutory authority via Tamil Nadu's state grievance system.
escalation_authority: Greater Chennai Corporation (PGR) → Chief Minister's Office / relevant statutory authority (state level, via IIPGCMS)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Public Grievance and Redressal System (GCC PGR) / Tamil Nadu CM Helpline reference
source_url: https://gccservices.chennaicorporation.gov.in/pgr
source_type: grievance_portal
source_organization: Greater Chennai Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: GCC's PGR complaint-number format was directly observed in the corporation's own public replies on X (chennaicorp account), which is a reasonably strong confirmation that the numbered-tracking mechanism is real and active — but escalation timeline/day-counts remain unfound for both the city and state levels.
```

### Record: TamilNadu-Coimbatore-AllServices-CitizenCharter
```
service_id: tn-coimbatore-all-citizen-charter
service_name: (cross-cutting — citizen charter covers water supply, sewerage, health/sanitation, roads, drainage, street lighting)
sub_service: General civic service commitments and grievance redressal
problem_type: multiple

state: Tamil Nadu
district: Coimbatore
city: Coimbatore
municipality: Coimbatore City Municipal Corporation (CCMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Multiple — Public Health Branch (sanitation/sweeping), Water Supply, Sewerage, Roads/Drainage, Street Lighting, Town Planning, Revenue (per the Citizen's Charter's own table of contents)
authority: Coimbatore City Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE (charter is stated to list key officials' names/designations/contacts per search summary, but specific names not extracted in this pass)

description: CCMC's own Citizens' Charter (published on the corporation's own domain, ccmc.gov.in) commits to transparency, responsibility, and user-friendliness in service delivery. It documents water supply, sewerage, health & sanitation, birth/death registration, trade licensing, immunization, town planning, and revenue-collection services, and specifies operational timings for some services directly — e.g. the Public Health Branch's routine road/public-place sweeping runs 6:00am–11:00am and 2:30pm–4:30pm daily. The charter also describes a "3-step normal complaint redressal system" for services outside the online-tracked subset.
procedure: File grievances via helpline, web portal, mobile app, email, Twitter, Facebook, post, or in person at the grievance call center; a dedicated internal telephone line at CCMC's Main Office is also provided for public grievances. WhatsApp grievances can be sent to 8190000200.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — the charter is confirmed (via search summary) to specify time schedules for services including Public Health, Water Supply, Roads, Drainage, and Street Lights, but exact day-count figures for complaint-to-resolution were not extracted from the PDF in this pass (only the sweeping-schedule times were surfaced as concrete text).
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Helpline, web portal, mobile app, email, Twitter, Facebook, postal mail, in-person grievance call center, WhatsApp 8190000200
contact_information: WhatsApp 8190000200

escalation_procedure: A "three step normal complaint redressal system for all other services" is referenced in search summary, alongside a separate "online complaint system" for certain services — but the specific 3 steps/levels and their timelines were not extracted from the PDF in this pass.
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Coimbatore City Municipal Corporation Citizen's Charter
source_url: https://ccmc.gov.in/img/upload/CitizensCharterEnglish1.pdf
source_type: citizen_charter
source_organization: Coimbatore City Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A because this is the corporation's own official Citizen's Charter PDF, hosted on its own ccmc.gov.in domain, and search summaries surfaced concrete, location-specific operational detail (the twice-daily sweeping schedule) directly attributable to this document — the strongest single source found for Tamil Nadu in this pass. However, the exact SLA day-counts for complaint-to-resolution (as opposed to routine service schedules) were not confirmed by search and remain SLA NOT FOUND — re-verify by direct fetch before treating any specific day-count as final. This is the best candidate in the entire 3-state pass for upgrading to a fully-populated record once direct fetch is available.
```

### Record: TamilNadu-Madurai-AllServices-CitizenCharter
```
service_id: tn-madurai-all-citizen-charter
service_name: (cross-cutting — citizen charter covers general municipal services)
sub_service: General civic service commitments and grievance redressal
problem_type: multiple

state: Tamil Nadu
district: Madurai
city: Madurai
municipality: Madurai City Municipal Corporation
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (charter is described as listing key officials by designation, but the department-by-department breakdown was not extracted from this pass)
authority: Madurai City Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE — the charter reportedly lists the Mayor, Deputy Mayor, and councillors with contact numbers, plus the names/designations/contacts of officials handling major issues, per search summary; specific names not extracted here.

description: The Citizens' Charter of Madurai Corporation is described (per its own hosting page on tnurbantree.tn.gov.in, the state Directorate of Municipal Administration's portal) as a commitment to publish service-delivery information and operate a time-bound public-grievance redressal system.
procedure: Register complaint via helpline, or write a complaint letter and submit it to the grievance cell at Corporation headquarters (Arignar Anna Maligai, Thallakulam, Madurai–625002).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Citizen Helpline +91-7871661787; dedicated line 14420 for sewage/septic-tank issues; postal/in-person grievance cell at Corporation HQ
contact_information: +91-7871661787; 14420 (sewage/septic tank)

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen Charter – Madurai Corporation
source_url: https://www.tnurbantree.tn.gov.in/madurai/citizen-charter/
source_type: citizen_charter
source_organization: Madurai City Municipal Corporation, via Directorate of Municipal Administration (Tamil Nadu)

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Note the "14420" number appears both here (Madurai, sewage-specific) and for CMWSSB in Chennai (general water helpline) — this is Tamil Nadu's shared/common statewide helpline pattern for water-utility complaints (14420 is used as a national common water/power-utility helpline number across multiple TN boards), not a coincidence, but this was not independently confirmed as a single unified state number in this pass — flag for follow-up. Kept at quality B (not A) because, unlike Coimbatore's charter, no concrete operational-schedule or SLA text was surfaced from this specific page in search summaries.
```

### Record: TamilNadu-DMA-CitizenCharterPortal
```
service_id: tn-statewide-dma-citizen-charter-portal
service_name: (cross-cutting — hosts individual citizen charters for most Tamil Nadu ULBs)
sub_service: Directory/portal of per-municipality citizen charters
problem_type: multiple

state: Tamil Nadu
district: NOT FOUND IN OFFICIAL SOURCE (state-wide portal)
city: NOT FOUND IN OFFICIAL SOURCE (indexes multiple cities/municipalities)
municipality: N/A (state department portal, not a single ULB)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Directorate of Municipal Administration, Tamil Nadu
authority: Government of Tamil Nadu — Directorate of Municipal Administration (nodal department coordinating all Municipalities and Municipal Corporations in the state EXCEPT the Corporation of Chennai, which is administered separately as GCC)
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: tnurbantree.tn.gov.in hosts individual Citizen Charter documents for many Tamil Nadu municipalities and municipal corporations (confirmed for Coimbatore, Madurai, Tiruchirappalli/Trichy, Tiruppur, Karaikudi, Idappadi, Pollachi in search results), each detailing services including Water Supply, Sewerage, Waste Management, Roads, Drains, Street Lights, Public Conveniences, and Sanitation, with published time schedules for "Public Health, Water supply, Roads, drainages and Street Lights."
procedure: N/A (this record documents the portal itself as a source, not a citizen procedure)
required_information: N/A
required_documents: N/A

sla: SLA NOT FOUND — search summary confirms that individual per-municipality charters DO specify time schedules for these service categories, but did not surface the specific numeric day-counts for any single municipality beyond Coimbatore's sweeping-schedule times (see Coimbatore record).
response_time: N/A
resolution_time: N/A

complaint_channel: N/A (varies per municipality; see individual city records)
contact_information: N/A

escalation_procedure: N/A
escalation_authority: N/A

faq: N/A
citizen_guidance: N/A

source_title: tnurbantree.tn.gov.in — Urban e-Governance / Government Orders portal
source_url: https://www.tnurbantree.tn.gov.in/
source_type: govt_portal
source_organization: Directorate of Municipal Administration, Government of Tamil Nadu

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: state
notes: Logged as a state-level index/portal because it is the single most valuable follow-up target for future Tamil Nadu research passes — every non-Chennai municipality's Citizen Charter appears to live at a predictable URL pattern (tnurbantree.tn.gov.in/<city>/citizen-charter/), meaning a direct-fetch pass over this portal could yield many quality-A records efficiently. A specific example found (Karaikudi) has a dated, signed 2025-26 PDF charter at https://www.tnurbantree.tn.gov.in/karaikudi/wp-content/uploads/sites/33/2025/06/Citizen-Charter-2025-26-singed-copy.pdf, suggesting these are actively maintained, current documents — a strong signal for data quality once fetched.
```

---

## Coverage notes for Tamil Nadu

- **Best-covered service:** No single service category dominated as
  clearly as in Maharashtra/Karnataka — the strongest single record found
  was Coimbatore's own Citizen's Charter PDF (quality A, the only A-rated
  record in this file), which cuts across all 4 service categories rather
  than being specific to one. Water & Drainage is well-covered for
  Chennai specifically, thanks to CMWSSB's dedicated citizen-facing
  complaint-redressal infrastructure (SMS-based Depot Engineer
  notification, national 14420 helpline).
- **Weakest-covered service:** Streetlights — no dedicated department,
  SLA, or streetlight-specific official page was found for Chennai,
  Coimbatore, or Madurai in this pass (Chennai's Namma Chennai app
  accepts streetlight photos as one of several categories, but nothing
  streetlight-specific beyond that), matching the pattern seen in
  Maharashtra and Karnataka.
- **Jurisdiction-split finding (important):** Chennai's water supply and
  sewerage is run by CMWSSB, a separate statutory board — **not** GCC.
  This mirrors the Bengaluru/BWSSB split found in Karnataka. Coimbatore
  and Madurai, by contrast, appear (per their own Citizen Charters
  covering "water supply, sewerage" directly) to have water/sewerage
  handled within the municipal corporation itself rather than split to a
  separate board — this should be treated as a tentative finding pending
  direct-fetch confirmation, not a settled fact.
- **Third-city choice:** Madurai was used per the assignment's suggested
  list; its official-domain coverage (tnurbantree.tn.gov.in citizen
  charter, madurai.nic.in district grievance page) was real but thinner
  in extracted detail than Coimbatore's own-domain (ccmc.gov.in) charter.
- **Notable structural finding:** Tamil Nadu's Directorate of Municipal
  Administration publishes individual Citizen Charters for most
  municipalities/corporations at a predictable URL pattern under
  tnurbantree.tn.gov.in — this portal is flagged above as the strongest
  candidate for a productive follow-up research pass, since (unlike
  Maharashtra and Karnataka, where per-city charters had to be inferred
  from general grievance pages) Tamil Nadu appears to have dated,
  regularly-updated PDF charters (e.g. Karaikudi's "2025-26" signed copy)
  publicly indexed for many cities at once.
- Nothing in this file should be read as confirming exact SLA numbers —
  the one genuinely concrete, location-specific operational detail found
  (Coimbatore's twice-daily street-sweeping schedule) is a *schedule*,
  not a complaint-response SLA; every complaint-response day-count claim
  found in this pass (e.g. the CMWSSB CGRF "90 days" figure) could not be
  confidently traced to an official government domain and is logged only
  in `notes`, not in the `sla`/`escalation_procedure` fields.
