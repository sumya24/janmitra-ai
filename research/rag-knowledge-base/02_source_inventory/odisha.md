# Odisha — Official Source Inventory

**Cities researched:** Bhubaneswar (Bhubaneswar Municipal Corporation,
BMC), Cuttack (Cuttack Municipal Corporation, CMC), Rourkela (Rourkela
Municipal Corporation, RMC)
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
| Odisha | Bhubaneswar | Waste & Sanitation | Sanitation Services — BMC | Bhubaneswar Municipal Corporation (BMC) | https://www.bmc.gov.in/services/sanitation-services | HTML | Service description, obligatory-function statement | RAG | B |
| Odisha | Bhubaneswar | Streetlights | Street Lighting — BMC | Bhubaneswar Municipal Corporation | https://www.bmc.gov.in/services/street-lighting | HTML | Service description (high-mast towers, obligatory function) | RAG | B |
| Odisha | Bhubaneswar | Water & Drainage | Water Supply Services — BMC | Bhubaneswar Municipal Corporation (references PHED as actual supplier) | https://www.bmc.gov.in/services/water-supply-services | HTML | Service description; jurisdiction note (state PHED supplies most of the city) | RAG | B |
| Odisha | Bhubaneswar | Water & Drainage | Public Health Engineering Organization (PHEO), Odisha — Services | PHED/PHEO Odisha — state department, NOT BMC | https://pheoodisha.gov.in/view-portal-services/2 | HTML | Jurisdiction, complaint/service info | RAG | B |
| Odisha | Bhubaneswar | Water & Drainage | Contact Us — PHEO Odisha | PHED/PHEO Odisha | https://pheoodisha.gov.in/portal-contact-us/8 | HTML | Contact channels | RAG | B |
| Odisha | Bhubaneswar | All services (unified grievance) | State e-Services Portal — Bhubaneswar Me (grievance) | Bhubaneswar Municipal Corporation, Bhubaneswar Smart City Ltd (BSCL), Bhubaneswar Development Authority (BDA), Capital Region Urban Transport (CRUT) — unified helpline | https://citizenservices.bhubaneswar.me/grievance/complaint-registration/grievance | Web app | Procedure, category list (SWM, streetlight, public/community toilets, etc.) | RAG | B |
| Odisha | Bhubaneswar / state-wide | All services (Housing & Urban Development Dept. citizen charter) | CITIZEN'S CHARTER (Draft) — Housing & Urban Development Department | Government of Odisha — Housing & Urban Development (H&UD) Department, via SUJOG | https://sujog.odisha.gov.in/Deshboard/images/Citizen%20Charter_HUD_Final.pdf | PDF | Department-wide service charter (draft status) | RAG | A |
| Odisha | (state-wide) | All services (SUJOG e-governance platform) | SUJOG — Sustainable Urban Services in a Jiffy | Government of Odisha, H&UD Department | https://sujog.odisha.gov.in/ | Web app | Channel (property tax, water & sewerage, trade licence, building plan approval, marriage registration, FSSM) | RAG | B |
| Odisha | (state-wide) | Water & Drainage (SUJOG module) | Services / Water & Sewerage — SUJOG | Government of Odisha, H&UD Department | https://sujog.odisha.gov.in/wns | Web app | Channel (connection application, bill payment) | RAG | B |
| Odisha | (state-wide) | All services (public grievance escalation) | Public Grievance Redressal — SUJOG | Government of Odisha, H&UD Department | https://sujog.odisha.gov.in/pgr | Web app | Channel, escalation | RAG | B |
| Odisha | (state-wide, general grievance system, not urban-specific) | All services (escalation levels) | Notification — formal platform for grievance redressal | Government of Odisha — General Administration & Public Grievance Department | https://health.odisha.gov.in/sites/default/files/2024-08/23017%2006082024%20Notification%20formal%20platform%20for%20grievance%20%28E%29.pdf | PDF | Escalation-level structure (L1–L4, 30-day auto-escalation) | RAG | B |
| Odisha | Cuttack | All services (grievance) | Public Grievance Redressal — Cuttack Municipal Corporation | Cuttack Municipal Corporation (CMC), via SUJOG | https://sujogportal.odisha.gov.in/cuttack/service/complaints/ | Web app | Channel, tracking | RAG | B |
| Odisha | Cuttack | All services (grievance, CMC own site) | Grievance — Cuttack Municipal Corporation | Cuttack Municipal Corporation | https://cmccuttack.odisha.gov.in/index.php/2559-2/ | HTML | Procedure, contact | RAG | B |
| Odisha | Cuttack | Water & Drainage | Water & Sewerage — Cuttack, SUJOG | Cuttack Municipal Corporation, via SUJOG | https://sujogportal.odisha.gov.in/cuttack/service/water-tax/ | Web app | Channel (connection, billing) | RAG | B |
| Odisha | Rourkela | All services (grievance) | Public Grievance Redressal — Rourkela Municipal Corporation | Rourkela Municipal Corporation (RMC), via SUJOG | https://sujogportal.odisha.gov.in/rourkela/service/complaints/ | Web app | Channel, tracking | RAG | B |
| Odisha | Rourkela | All services (RMC own site) | e-Services — Rourkela Municipal Corporation | Rourkela Municipal Corporation | https://rmc.nic.in/eservices.html | HTML | Channel listing | RAG | B |
| Odisha | Cuttack | (reference only, not verified fact source) | Cuttack Municipal Corporation call center — complaint category codes | Non-.gov.in domain (appears to be CMC's outsourced call-center vendor, not confirmed as an official CMC-operated domain) | https://cmccallcenter.in/register-complain | Web form | Complaint category granularity (garbage lifting, road sweeping, debris removal, dead animal removal, etc.) — useful context, not independently confirmed as official | reference only | D |
| Odisha | Bhubaneswar | (reference only, not verified fact source) | Praja/IJAMTES-style academic PDF — Solid Waste Management in Bhubaneswar | Academic paper (ijamtes.org), not government | https://www.ijamtes.org/gallery/94-jan19.pdf | PDF | Contextual analysis of BMC's SWM system challenges (manpower, vehicle shortages) | reference only | D |

---

## Full records

### Record: Odisha-Bhubaneswar-Waste-Sanitation
```
service_id: od-bhubaneswar-waste-sanitation
service_name: Waste & Public Sanitation
sub_service: Solid waste management (general), cleanliness
problem_type: garbage_collection

state: Odisha
district: Khordha
city: Bhubaneswar
municipality: Bhubaneswar Municipal Corporation (BMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: BMC operates 60 wards; sanitation/cleaning service has been privatized in 40 of the 60 wards per search summary (source for the ward count/privatization detail was a search-engine summary referencing a BMC tender/DPR document, not independently opened)

department: NOT FOUND IN OFFICIAL SOURCE (Sanitation/Solid Waste Management wing of BMC, exact department name not confirmed on an official page)
authority: Bhubaneswar Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: BMC's sanitation-services page describes solid waste management as one of its core civic functions; the city generates approximately 500 tonnes/day of solid waste within the BMC area (per search-summarized context, not independently confirmed on BMC's own page). BMC has run the "Swachh Bhubaneswar Abhiyaan" cleanliness program.
procedure: File via BMC/BSCL/BDA/CRUT's unified grievance channel (toll-free 1929 or 1800 345 0061, email grievance@bmc.gov.in) or the citizenservices.bhubaneswar.me online grievance portal.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Toll-free 1929, unified helpline 1800 345 0061, landline 0674-2548295, email grievance@bmc.gov.in, online portal (citizenservices.bhubaneswar.me), social media
contact_information: 1929 / 1800 345 0061 / grievance@bmc.gov.in

escalation_procedure: ESCALATION INFORMATION NOT FOUND (BMC-specific escalation chain not surfaced; see the state-level H&UD Citizen Charter and General Administration & Public Grievance Dept. records for the general Odisha escalation structure)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Sanitation Services — Bhubaneswar Municipal Corporation
source_url: https://www.bmc.gov.in/services/sanitation-services
source_type: govt_portal
source_organization: Bhubaneswar Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: The 500 tonnes/day figure and the 40/60-ward privatization detail were surfaced via search summaries referencing BMC-adjacent documents (a tender PDF, an academic paper) rather than confirmed as text on bmc.gov.in's own sanitation-services page directly — treat these two figures as needing re-confirmation even though they plausibly originate from BMC-related sources.
```

### Record: Odisha-Bhubaneswar-Streetlight
```
service_id: od-bhubaneswar-streetlight
service_name: Streetlights
sub_service: Streetlight provision and maintenance, high-mast lighting
problem_type: streetlight_not_working

state: Odisha
district: Khordha
city: Bhubaneswar
municipality: Bhubaneswar Municipal Corporation (BMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (Electrical/Street Lighting wing, exact name not confirmed)
authority: Bhubaneswar Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: BMC's own street-lighting services page states that "the provision and maintenance of streetlights is an obligatory function of Bhubaneswar Municipal Corporation," and that high-mast towers are erected at markets, institutions, and dense traffic junctions for uniform lighting. A World Bank PPP case-study document on Bhubaneswar street lighting was also located, suggesting a public-private partnership model has been used historically for at least part of the streetlight infrastructure — not independently confirmed as still current.
procedure: File via the BMC/BSCL/BDA/CRUT unified grievance channel; the citizenservices.bhubaneswar.me grievance portal explicitly lists "street light" as one of its grievance categories.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Toll-free 1929 / 1800 345 0061, citizenservices.bhubaneswar.me grievance portal (streetlight is an explicit category), email grievance@bmc.gov.in
contact_information: 1929 / 1800 345 0061

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Street Lighting — Bhubaneswar Municipal Corporation
source_url: https://www.bmc.gov.in/services/street-lighting
source_type: govt_portal
source_organization: Bhubaneswar Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Unlike most other cities researched across all 3 states in this pass, Bhubaneswar has a genuinely dedicated, named "Street Lighting" service page on the municipal corporation's own domain — a small positive outlier against the general pattern (seen in Maharashtra, Karnataka, Tamil Nadu) that streetlights are usually the thinnest-documented category. Still, no SLA or escalation detail was found.
```

### Record: Odisha-Bhubaneswar-Water-PHED
```
service_id: od-bhubaneswar-water-phed
service_name: Water & Drainage
sub_service: Piped water supply (leakage, no/low supply), drainage
problem_type: no_low_water_supply

state: Odisha
district: Khordha
city: Bhubaneswar
municipality: Bhubaneswar Municipal Corporation (BMC) — but water supply is NOT primarily handled by BMC; see notes
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Public Health Engineering Organization (PHEO), also referred to as PHED — a state department, not a BMC department
authority: Public Health Engineering Organization, Government of Odisha
officer_designation: NOT FOUND IN OFFICIAL SOURCE (Engineer-in-Chief, PHED referenced generically as the department head in search results, not tied to a specific complaint-escalation role)

description: Water supply to most parts of Bhubaneswar is maintained by the state PHED, not BMC directly — approximately 220 ML/day is supplied through the piped water supply system (per search summary attributed to BMC's own water-supply-services page, which itself references PHED as the operating agency). This is a jurisdiction split consistent with the pattern flagged in 01_service_data_requirements.md.
procedure: Log in to PHED's online complaint portal using consumer number plus registered mobile/telephone and email, or call the toll-free number.
required_information: Consumer number, registered mobile number or telephone number, email ID (for online complaint login)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Toll-free 1800 345 6783 (leakage/water supply), PHED main contact numbers 0674-2575309 / 0674-2393909 / 9437089388, email eicphodisha@gmail.com, online complaint portal (consumer-number login)
contact_information: Toll-free 1800 345 6783; email eicphodisha@gmail.com

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Public Health Engineering Organization, Odisha — Services
source_url: https://pheoodisha.gov.in/view-portal-services/2
source_type: govt_portal
source_organization: Public Health Engineering Organization (PHEO), Government of Odisha

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: **Important jurisdiction-split finding**: Bhubaneswar's piped water supply is predominantly run by the state PHED (Public Health Engineering Organization), not BMC — matching the pattern found for Bengaluru/BWSSB (Karnataka) and Chennai/CMWSSB (Tamil Nadu). Any JanSarthi routing logic for Bhubaneswar water complaints should point to PHED channels rather than BMC's general grievance line, though BMC's own citizenservices.bhubaneswar.me portal also lists water as a grievance category — the exact division of labor between the two channels (state PHED infrastructure vs. BMC-forwarded citizen complaints) was not fully resolved in this pass and needs direct-fetch follow-up. Drainage/sewerage specifically (as opposed to water supply) was not clearly attributed to either PHED or BMC in the search results found — flag as a further open question.
```

### Record: Odisha-Bhubaneswar-AllServices-UnifiedHelpline
```
service_id: od-bhubaneswar-all-unified-helpline
service_name: (cross-cutting — unified helpline covers all 4 categories plus non-civic services)
sub_service: General civic grievance registration across 4 city agencies
problem_type: multiple

state: Odisha
district: Khordha
city: Bhubaneswar
municipality: Bhubaneswar Municipal Corporation (BMC), jointly with Bhubaneswar Smart City Limited (BSCL), Bhubaneswar Development Authority (BDA), and Capital Region Urban Transport (CRUT)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Bhubaneswar Municipal Corporation (lead agency for the unified helpline), jointly with BSCL, BDA, CRUT
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: A single unified toll-free helpline and online grievance portal covers all 4 city agencies (BMC, BSCL, BDA, CRUT), accepting grievances across categories including bus ticket/fare issues, community and public toilets, solid waste management, streetlight, stray animals, and other municipal services. Since the Citizen Charter's release on 6 December 2006, a reported 13,473 of 14,779 grievances received had been disposed (a historical, not current, figure per search summary — needs re-confirmation of currency).
procedure: Call the toll-free number, use social media, email the dedicated grievance address, or use the online Complaint Form on citizenservices.bhubaneswar.me.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Toll-free 1929 and 1800 345 0061, landline 0674-2548295, email grievance@bmc.gov.in, social media, online portal (citizenservices.bhubaneswar.me/grievance/complaint-registration/grievance)
contact_information: 1929 / 1800 345 0061 / grievance@bmc.gov.in

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: State e-Services Portal — Bhubaneswar Me (Grievance)
source_url: https://citizenservices.bhubaneswar.me/grievance/complaint-registration/grievance
source_type: grievance_portal
source_organization: Bhubaneswar Municipal Corporation, Bhubaneswar Smart City Limited, Bhubaneswar Development Authority, Capital Region Urban Transport

publication_date: 2006-12-06 (Citizen Charter release date, referenced within this source's own historical figures)
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: The 4-agency unification (BMC + BSCL + BDA + CRUT under one helpline) is a distinctive structural feature not seen in the other 2 states researched — worth capturing in any future JanSarthi Odisha-specific routing design, since it means a single Bhubaneswar helpline number may route to a Smart City company or transit authority rather than the municipal corporation for some categories. The 2006 Citizen Charter reference (13,473/14,779 disposed) is old and should be treated as historical context only, not current performance — flagged per the OUTDATED sentinel guidance if ever cited as a live statistic.
```

### Record: Odisha-HUD-CitizenCharterDraft
```
service_id: od-statewide-hud-citizen-charter-draft
service_name: (cross-cutting — department-wide charter spanning housing, water/sewerage, solid waste, storm water drainage, roads, public transport)
sub_service: Departmental citizen charter
problem_type: multiple

state: Odisha
district: NOT FOUND IN OFFICIAL SOURCE (state department, applies to all Odisha ULBs)
city: NOT FOUND IN OFFICIAL SOURCE (applies state-wide)
municipality: N/A (state department, not a single ULB)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Housing & Urban Development (H&UD) Department
authority: Government of Odisha — Housing & Urban Development Department
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: The H&UD Department's Citizen's Charter (explicitly marked "Draft" in its own title) states the department's measures for civic-service management and delivery, covering affordable housing, safe drinking water, sanitation (including solid waste management), storm water drainage, sewerage, roads, public transport, and livelihood opportunities. The department separately reports (per an unrelated May-2026 news item, not part of this PDF) 94% timeline adherence across 30 ORTPS-notified citizen services, with 21 of 30 services fully operational online via SUJOG.
procedure: NOT FOUND IN OFFICIAL SOURCE (charter content beyond the general scope statement was not extracted from the PDF in this pass)
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — the charter is a departmental-scope document; specific per-service SLA day-counts were not extracted from the PDF text in this pass (only the general framing was surfaced via search summary).
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: SUJOG platform (sujog.odisha.gov.in), SWACHHATA platform, dedicated grievance management systems referenced generically
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: ESCALATION INFORMATION NOT FOUND (this document); see the separate General Administration & Public Grievance Department notification record below for the general Odisha state escalation-level structure, which is NOT confirmed to be the same mechanism this H&UD charter refers to.
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: CITIZEN'S CHARTER (Draft) — Housing & Urban Development Department
source_url: https://sujog.odisha.gov.in/Deshboard/images/Citizen%20Charter_HUD_Final.pdf
source_type: citizen_charter
source_organization: Housing & Urban Development Department, Government of Odisha

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: state
notes: Rated A because this is the state department's own official citizen charter PDF, hosted on its own e-governance domain (sujog.odisha.gov.in), directly naming the civic-service categories this research covers. HOWEVER: the document's own title includes the word "(Draft)" — per 00_README.md's sentinel-value table, this is exactly the situation for `OUTDATED / VERIFY BEFORE PRODUCTION USE`, so despite the A source-quality rating, this record's content should be treated as provisional/unadopted until a person confirms whether a finalized (non-draft) version exists and supersedes it. This is the single most promising document for a future direct-fetch pass across all 3 states researched.
```

### Record: Odisha-Statewide-GAPGD-EscalationLevels
```
service_id: od-statewide-gapgd-escalation
service_name: (cross-cutting — general state grievance escalation, not urban-specific)
sub_service: Public grievance escalation levels
problem_type: multiple

state: Odisha
district: NOT FOUND IN OFFICIAL SOURCE (state-wide)
city: NOT FOUND IN OFFICIAL SOURCE (state-wide, not urban-service-specific)
municipality: N/A
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: General Administration & Public Grievance Department
authority: Government of Odisha
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: A formal notification from Odisha's General Administration & Public Grievance Department establishes a "formal platform for grievance redressal" with a defined 4-level escalation structure. This is a general state-government mechanism (via the Jana Sunani / PGRS portal), not specific to urban civic services or any one municipal corporation — logged here as the most concrete official escalation-timeline detail found across all 3 states in this pass, but its applicability to municipal-corporation-specific complaints (vs. general state department grievances) needs direct confirmation.
procedure: Register a grievance through the Jana Sunani/PGRS system; if undisposed after 30 days at the district level, it automatically escalates to the next higher authority.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: 30 days (district-level auto-escalation trigger) — this is the one specific, numbered day-count in this entire Odisha research pass that traces to what appears to be an official state government notification PDF (health.odisha.gov.in, hosted under a state department subdomain).
response_time: NOT FOUND IN OFFICIAL SOURCE
resolution_time: NOT FOUND IN OFFICIAL SOURCE

complaint_channel: Jana Sunani / PGRS portal (odisha.gov.in ecosystem), also referenced via igrodisha.gov.in
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: 4-level structure — Level 1 (local office/department) → Level 2 (District/Department Grievance Cell) → Level 3 (State Grievance Redressal Authority) → Level 4 (Chief Minister's Grievance Cell). Auto-escalation from district level occurs after 30 days without disposal.
escalation_authority: Level 1 (local office) → Level 2 (District/Dept. Grievance Cell) → Level 3 (State Grievance Redressal Authority) → Level 4 (CM's Grievance Cell)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Notification — formal platform for grievance redressal
source_url: https://health.odisha.gov.in/sites/default/files/2024-08/23017%2006082024%20Notification%20formal%20platform%20for%20grievance%20%28E%29.pdf
source_type: dept_notification
source_organization: General Administration & Public Grievance Department, Government of Odisha

publication_date: 2024-08-06 (per the filename/notification-date convention observed in the URL)
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: state
notes: This is a *general* Odisha state government grievance escalation structure (applicable to all departments, discovered via a health-department-hosted copy of the notification), not something confirmed to be specific to Housing & Urban Development / municipal-corporation civic complaints. It should not be assumed to automatically govern e.g. a BMC garbage complaint's escalation path without direct confirmation — logged here because it is the most concrete, numbered escalation detail (30-day auto-trigger, 4 levels) found anywhere across the 3-state, 9-city research pass, and is worth a targeted follow-up to confirm whether it applies to SUJOG/municipal-corporation grievances specifically.
```

### Record: Odisha-Cuttack-AllServices-Grievance
```
service_id: od-cuttack-all-grievance
service_name: (cross-cutting — grievance system covers all 4 categories)
sub_service: General civic grievance registration
problem_type: multiple (sanitation/public health categories explicitly named: garbage lifting, road sweeping, debris removal, garbage bin replacement, dead animal removal, anti-malaria operations)

state: Odisha
district: Cuttack
city: Cuttack
municipality: Cuttack Municipal Corporation (CMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (routed internally by category)
authority: Cuttack Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: CMC operates a Public Grievance Redressal (PGR) system, both via CMC's own domain (cmccuttack.odisha.gov.in) and via the state's SUJOG portal, allowing citizens to lodge complaints online and track resolution progress until closure. Categories accepted include sanitation and public-health issues with specific sub-codes (garbage lifting, road sweeping, debris removal, garbage bin replacement, dead animal removal, anti-malaria operations) — this granular category list was found via a third-party-hosted CMC call-center vendor site (cmccallcenter.in), not CMC's own .gov.in domain, and is logged with that caveat.
procedure: Register complaint via CMC's Control Room (0671-2310472), the toll-free number, email, or the SUJOG portal for Cuttack.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Control Room 0671-2310472, toll-free 1800 3456728, email mccmc@nic.in, online portal (sujogportal.odisha.gov.in/cuttack, cmccuttack.odisha.gov.in)
contact_information: Control Room 0671-2310472; toll-free 1800 3456728; email mccmc@nic.in

escalation_procedure: ESCALATION INFORMATION NOT FOUND (CMC-specific escalation chain not surfaced)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Grievance — Cuttack Municipal Corporation
source_url: https://cmccuttack.odisha.gov.in/index.php/2559-2/
source_type: govt_portal
source_organization: Cuttack Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: CMC's own domain is an official odisha.gov.in subdomain (cmccuttack.odisha.gov.in), which is a good sign of genuine official presence. The detailed sanitation sub-category list (garbage lifting/road sweeping/debris removal/etc.) is plausible and specific-sounding but was only found on cmccallcenter.in, a non-.gov.in domain that appears to be an outsourced call-center vendor front-end for CMC — per this file's rule, that detail is NOT treated as independently verified and is logged only descriptively here, not promoted to a quality-A fact.
```

### Record: Odisha-Rourkela-AllServices-Grievance
```
service_id: od-rourkela-all-grievance
service_name: (cross-cutting — grievance/helpline explicitly covers streetlights, water, roads, sanitation)
sub_service: General civic grievance and information helpline
problem_type: multiple (streetlights, drinking water, roads & infrastructure, sanitation explicitly named)

state: Odisha
district: Sundargarh
city: Rourkela
municipality: Rourkela Municipal Corporation (RMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Rourkela Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: RMC operates a 24x7 free helpline explicitly covering "Information, Grievance & Feedback on street lights, drinking water, roads & infra, sanitation, marriage, birth & death certificates, various taxes and permits" — this specific category list was found on RMC's own official X/Twitter account (@RourkelaMC), a government-agency-operated social account rather than a formal document; also confirmed generally via the SUJOG portal's Rourkela section and RMC's own domain (rmc.nic.in).
procedure: Call the 24x7 helpline, or register online via the SUJOG portal's Rourkela grievance section.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: 24x7 helpline 1800 345 7468, online portal (sujogportal.odisha.gov.in/rourkela/service/complaints/), RMC's own site (rmc.nic.in)
contact_information: 1800 345 7468

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Rourkela Municipal Corporation (X/Twitter post announcing 24x7 helpline)
source_url: https://x.com/RourkelaMC/status/1431276264191528973
source_type: govt_portal
source_organization: Rourkela Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE (tweet-based; exact post date not extracted beyond the status ID)
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Source is RMC's own verified-appearing official social media account rather than a formal webpage/PDF — genuinely useful for confirming the helpline number and explicit category list (streetlights/water/roads/sanitation are all named together, unusually complete for a single source in this pass), but social-media posts are less durable/re-verifiable than a hosted document; a corroborating RMC-domain or SUJOG page confirming the same helpline number would upgrade confidence. Cross-referenced against rmc.nic.in/eservices.html and sujogportal.odisha.gov.in/rourkela/, both of which are genuine official domains, for partial corroboration of RMC's general online-services presence.
```

---

## Coverage notes for Odisha

- **Best-covered service:** No single civic-service category had richer
  coverage than the others across Odisha's 3 cities — instead, the
  standout finding was structural: Odisha runs a single state-wide
  e-governance platform (SUJOG) that every researched city (Bhubaneswar,
  Cuttack, Rourkela) uses for online services and grievance redressal,
  giving Odisha the most *consistent* cross-city infrastructure pattern
  of the 3 states researched in this entire assignment (Maharashtra,
  Karnataka, Tamil Nadu, Odisha). Streetlights was, if anything,
  marginally better documented for Bhubaneswar than elsewhere (a
  dedicated bmc.gov.in "Street Lighting" service page exists), bucking
  the pattern seen in the other states.
- **Weakest-covered service:** Roads & Potholes — no dedicated official
  page, department name, or SLA was found for road/pothole complaints in
  any of the 3 Odisha cities in this pass (RMC's helpline mentions
  "roads & infra" as a general category, but nothing pothole-specific
  surfaced). This is the one clear service-category gap for Odisha.
- **Jurisdiction-split finding:** Bhubaneswar's water supply is
  predominantly run by the state Public Health Engineering Organization
  (PHED/PHEO), not BMC directly — the same structural pattern found for
  Bengaluru/BWSSB (Karnataka) and Chennai/CMWSSB (Tamil Nadu). Odisha
  additionally has a distinctive **4-agency unified helpline** for
  Bhubaneswar (BMC + Bhubaneswar Smart City Ltd + Bhubaneswar Development
  Authority + Capital Region Urban Transport under one number), not seen
  in any other city researched across the 3-state assignment.
- **Third-city choice:** Rourkela was used per the assignment's suggested
  list; its official-domain presence (rmc.nic.in, SUJOG's rourkela
  section) is real but the richest single piece of category-specific
  detail found for it (streetlights/water/roads/sanitation named
  together under one helpline) came from the corporation's own social
  media account rather than a webpage — flagged as B rather than
  upgraded, and worth a direct-fetch follow-up to find the same list on
  a hosted RMC page.
- **Notable finding — draft citizen charter:** Odisha's Housing & Urban
  Development Department has published a state-wide Citizen's Charter
  PDF explicitly marked "(Draft)" in its own title. This is flagged per
  `00_README.md`'s `OUTDATED / VERIFY BEFORE PRODUCTION USE` sentinel
  guidance — its content should not be treated as final/adopted policy
  without independent confirmation that a non-draft version exists.
- **Notable finding — general vs. urban-specific escalation:** The most
  concrete, numbered escalation detail found for Odisha in this entire
  pass (a 4-level structure with 30-day district-level auto-escalation)
  comes from a General Administration & Public Grievance Department
  notification that governs state government grievances broadly, not
  something confirmed to be specific to municipal-corporation civic
  complaints — this should not be assumed to automatically apply to a
  BMC/CMC/RMC-routed garbage or streetlight complaint without direct
  verification.
- As with the other 2 states in this batch, no specific numeric SLA
  day-count for complaint-to-resolution was confirmed on any Odisha
  municipal corporation's own official page in this pass — the one
  numbered figure captured with reasonable confidence (the 30-day
  auto-escalation trigger) is a *general* state grievance-system
  parameter, not a per-service civic SLA, and is flagged as such above.
