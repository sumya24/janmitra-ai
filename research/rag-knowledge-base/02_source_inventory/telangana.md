# Telangana — Official Source Inventory

**Cities researched:** Hyderabad (GHMC), Warangal (GWMC)
**Method:** WebSearch only. WebFetch (direct page-fetch/verification) was
completely unavailable in this environment for this entire pass (tested
against multiple domains including government sites — all
`EGRESS_BLOCKED`). Every record below is marked `NOT INDEPENDENTLY
FETCHED — confirm before production use` in `verification_status`.

> **Environment note (same caveat as `maharashtra.md` / `andhra_pradesh.md`):**
> Everything here relies on WebSearch result metadata (URL, title,
> search-engine-generated summary), not a direct fetch-and-read of page
> content. `source_quality` reflects how official/specific the *domain*
> is (never upgraded because a summary sounded detailed). **Critically
> for this state:** several specific numeric SLA figures for GHMC's
> Citizen's Charter (e.g. "24 hours for potholes," "same-day for MSW
> collection," "48 hours for stormwater drains") were found repeatedly
> across the search results — but every instance of those exact
> day-counts in this pass was attributed to **news-site summaries**
> (thehansindia.com, telanganatribune.com, newsmeter.in), not to
> body text read directly from the official `ghmc.gov.in` PDF, even
> though that PDF's own URL was independently located. Per the
> environment constraint, those figures are therefore **NOT** entered
> into the `sla` field below — they are recorded only in `notes`,
> clearly labeled as unverified/third-party, pending someone with
> working fetch access opening the PDF directly.

---

## Summary table

| State | City | Service | Source | Authority | URL | Format | Data Available | RAG or SQL | Quality |
|---|---|---|---|---|---|---|---|---|---|
| Telangana | Hyderabad | All services (Citizen's Charter) | Citizen's Charter — Hyderabad | Greater Hyderabad Municipal Corporation (GHMC) | https://www.ghmc.gov.in/CitizenCharter/CitizenCharter-19.06.pdf | PDF | Service list (17 civic services), Ward Level Office structure | RAG | A |
| Telangana | Hyderabad | All services (grievance system) | Grievances — Integrated Grievance System (IGS) | GHMC | https://igs.ghmc.gov.in/ | Web app | Channel, complaint tracking (re-open by complainant) | RAG | A |
| Telangana | Hyderabad | All services (grievance system, alt.) | GHMC Online Grievance | GHMC, hosted via Centre for Good Governance (cgg.gov.in) | https://ghmconlinegrievance.cgg.gov.in/ | Web app | Channel | RAG | B |
| Telangana | Hyderabad | Water & Drainage | Citizen's Charter of HMWSSB | Hyderabad Metropolitan Water Supply & Sewerage Board (HMWSSB) — separate statutory board, NOT GHMC | https://www.hyderabadwater.gov.in/application/files/7417/3185/0800/updated_citizen_charter.pdf | PDF | Complaint types, escalation description, contact channels | RAG | A |
| Telangana | Hyderabad | Water & Drainage | Contact Us — HMWSSB | HMWSSB | https://www.hyderabadwater.gov.in/en/index.php/contact-us | HTML | Channel, contact info | RAG | A |
| Telangana | Warangal | All services (grievance mechanism) | Grievance Registration — GWMC | Greater Warangal Municipal Corporation (GWMC) | https://gwmc.gov.in/grievance_registration.aspx | Web form | Procedure, channel | RAG | A |
| Telangana | Warangal | All services (contact) | Contact Us — GWMC | GWMC | https://gwmc.gov.in/ContactUs_New.aspx | HTML | Contact info | RAG | A |
| Telangana | (state-wide) | All services | Grievance Redressal — CDMA / MA&UD | Commissioner and Director of Municipal Administration (CDMA), MA&UD Dept., Govt. of Telangana | https://emunicipal.telangana.gov.in/Grievance_Redressal | HTML | Procedure (post/phone/fax/email intake, ULB routing) | RAG | B |
| Telangana | (state-wide) | All services | Municipal Administration & Urban Development | Telangana State Portal | https://www.telangana.gov.in/departments/municipal-administration-urban-development/ | HTML | Department overview | RAG | B |
| Telangana | Warangal | Waste & Sanitation | Solid Waste Disposal : Warangal (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | https://www.data.gov.in/catalog/solid-waste-disposal-warangal | Dataset (catalog) | Source segregation, D2D efficiency, bin placement, collection vehicles | Structured/SQL | C |
| Telangana | Warangal | Waste & Sanitation | Solid Waste Collection Vehicle : Warangal 2019 | MoHUA Smart Cities Mission, via Smart Cities Mission Data Portal | https://smartcities.data.gov.in/resources/solid-waste-collection-vehicle-warangal-2019 | Dataset | Collection vehicle fleet data | Structured/SQL | C |
| Telangana | Hyderabad (reference only) | (reference only, not verified fact source) | Citizen's Charter: GHMC promises to fill potholes within 24 hrs | newsmeter.in (news, third-party) | https://newsmeter.in/hyderabad/citizens-charter-ghmc-promises-fill-potholes-within-24-hrs-of-complaint-17-civic-services-listed-713559 | HTML | Reported SLA figures (unverified against the official PDF in this pass) | reference only | D |
| Telangana | Hyderabad (reference only) | (reference only, not verified fact source) | GHMC rolls out Citizen's Charter for speedy redressal | thehansindia.com (news, third-party) | https://www.thehansindia.com/news/cities/hyderabad/hyderabad-ghmc-rolls-out-citizens-charter-for-speedy-redressal-of-civic-woes-802923 | HTML | Reported SLA figures, compensation clause (unverified against official PDF) | reference only | D |
| Telangana | Warangal (reference only) | (reference only, not verified fact source) | COMPASSIONATE CITIZENSHIP PROGRAM — Public Services Warangal | covanetwork.org (NGO/training material, third-party) | https://www.covanetwork.org/wp-content/uploads/CC-PPT-Public-Service-Warangal-Final-29-12-2022.pdf | PDF | Claims about which GWMC section handles which service; not independently confirmed | reference only | D |

---

## Full records

### Record: Telangana-Hyderabad-Waste-SolidWasteManagement
```
service_id: ts-hyderabad-waste-solid-waste-management
service_name: Waste & Public Sanitation
sub_service: Municipal solid waste (MSW) collection — door-to-door and bulk waste generators
problem_type: garbage_collection

state: Telangana
district: Hyderabad
city: Hyderabad
municipality: Greater Hyderabad Municipal Corporation (GHMC)
zone: GHMC is organized into 6 Zones and 30 Circles (per GHMC's own organizational structure, corroborated across multiple search summaries)
ward: GHMC has 150 Wards; the Citizen's Charter's 17 civic services (including sanitation-adjacent ones) are stated to be delivered at Ward Level Offices

department: Sanitation / Solid Waste Management wing of GHMC (exact formal department name and officer NOT FOUND IN OFFICIAL SOURCE in this pass — GHMC's Entomology wing, a related but distinct public-health unit, was separately named)
authority: Greater Hyderabad Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GHMC's Citizen's Charter (an official document confirmed to exist at the ghmc.gov.in domain — see source below) lists 17 civic services to be delivered at Ward Level Offices, including municipal solid waste (MSW) collection from door-to-door and from bulk waste generators/commercial establishments. Complaints (including open garbage dumping) can also be filed via the MyGHMC app.
procedure: Report via the MyGHMC mobile app (which also handles open manholes, potholes, and dysfunctional streetlights), the GHMC website's online services, the GHMC call centre, or the Integrated Grievance System (IGS) at igs.ghmc.gov.in — citizens can track status and, under IGS, only the complainant (not GHMC staff) can close the ticket.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — a "same day" resolution commitment for MSW door-to-door/bulk-waste collection was reported repeatedly across news coverage (thehansindia.com, telanganatribune.com, newsmeter.in) of GHMC's Citizen's Charter, and an official Citizen's Charter PDF was independently located at ghmc.gov.in (see source_url below) — but the exact wording/day-count was not read directly from that PDF in this pass, only reported via secondary news sources. Do not treat as verified until the PDF itself is opened.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: MyGHMC mobile app, ghmc.gov.in online services, GHMC call centre 040-2111 1111, Integrated Grievance System (igs.ghmc.gov.in), GHMC's Twitter/X account, Ward Level Offices, Commissioner's Office, Prajavani
contact_information: GHMC call centre 040-2111 1111

escalation_procedure: If a registered complaint is not redressed within the Citizen's Charter timeline, or the citizen is not satisfied with the response, they may lodge a grievance with GHMC's Public Grievance Cell, or email/write to the Commissioner (head office) or the Joint Commissioners of the concerned department.
escalation_authority: Public Grievance Cell, GHMC → Commissioner / Joint Commissioners (concerned department), GHMC

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen's Charter — Hyderabad
source_url: https://www.ghmc.gov.in/CitizenCharter/CitizenCharter-19.06.pdf
source_type: citizen_charter
source_organization: Greater Hyderabad Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE (news coverage places the Charter's launch around June 2023; the PDF filename "19.06" is consistent with a 19 June date, but this is inferential, not confirmed)
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A because ghmc.gov.in is unambiguously GHMC's own official domain and the URL (CitizenCharter-19.06.pdf) is a location-and-topic-specific document, whose existence and exact URL were independently confirmed via search — but the PDF's body text (the actual SLA table, the Rs.50/Rs.100-per-day-of-delay compensation clause reportedly described in news coverage) was NOT read directly in this pass. This is the single highest-value direct-fetch target found across all 3 states in this research pass: if confirmed, it would upgrade multiple SLA fields across all 4 Hyderabad service categories from NOT FOUND to a real, citable figure.
```

### Record: Telangana-Hyderabad-Water-Drainage
```
service_id: ts-hyderabad-water-drainage
service_name: Water & Drainage
sub_service: Water supply, sewerage maintenance, water-quality/contamination complaints
problem_type: no_low_water_supply

state: Telangana
district: Hyderabad
city: Hyderabad
municipality: Hyderabad Metropolitan Water Supply & Sewerage Board (HMWSSB) — a SEPARATE statutory board, distinct from GHMC
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Hyderabad Metropolitan Water Supply & Sewerage Board (HMWSSB) — the board itself is the responsible authority, not a GHMC sub-department
authority: HMWSSB
officer_designation: NOT FOUND IN OFFICIAL SOURCE (Managing Director's office is referenced via the general contact email mdhmwssb@hyderabadwater.gov.in, but no named individual was surfaced)

description: HMWSSB is a statutory board — separate from GHMC — responsible for water supply and sewerage across the Hyderabad Metropolitan Area, serving Hyderabad and Secunderabad. It operates a round-the-clock call centre ("Metro Customer Care," MCC) and publishes its own Citizen's Charter. This is a clear, confirmed jurisdiction split from GHMC (which handles roads, sanitation collection, and streetlights — see other Hyderabad records) — exactly the kind of split `01_service_data_requirements.md` warns must be captured explicitly per city rather than assumed.
procedure: File via HMWSSB's 24-hour customer care (155313 / 040-23300114 / 23433933), the sewerage helpline (14420), email (customer-support@hyderabadwater.gov.in), or online under "Register Grievances" in the "Customer" section of hyderabadwater.gov.in. HMWSSB offices are open 10:30am-5:00pm for in-person matters, though the call centre operates 24x7.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — no numeric hour/day figure for a specific complaint type (leak, no-supply, sewage) was found attributed to an official hyderabadwater.gov.in page body in this pass, despite the official Citizen's Charter PDF's existence and URL being confirmed (see source below).
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: 24-hour customer care 155313 / 040-23300114 / 23433933, sewerage helpline 14420, email customer-support@hyderabadwater.gov.in, online "Register Grievances" (Customer section, hyderabadwater.gov.in), HMWSSB Citizen Services mobile app
contact_information: Water complaint 155313 / Sewerage helpline 14420 / email customer-support@hyderabadwater.gov.in

escalation_procedure: HMWSSB's Citizen's Charter is described as having "a well laid down mechanism for efficient and effective resolution of grievances," with an unresolved complaint escalated to the next-level officer — but the specific level names/titles were not confirmed on an official page body in this pass.
escalation_authority: NOT FOUND IN OFFICIAL SOURCE (generic "next level officer" only, per search summary of the Charter)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen's Charter of HMWSSB
source_url: https://www.hyderabadwater.gov.in/application/files/7417/3185/0800/updated_citizen_charter.pdf
source_type: citizen_charter
source_organization: Hyderabad Metropolitan Water Supply & Sewerage Board

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE ("updated_citizen_charter" in the filename suggests at least one revision, but the date of that revision was not surfaced)
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: This is the clearest water-supply-vs-municipal-corporation jurisdiction split found across all 3 states researched in this pass — HMWSSB is a genuinely separate statutory entity from GHMC with its own domain, own Citizen's Charter, and own call centre, unlike Visakhapatnam/Vijayawada (see andhra_pradesh.md) where GVMC/VMC appear to handle water directly. A second official PDF URL for the same Charter was also found (hyderabadwater.gov.in/en/files/4216/8681/9494/Citizen_charter.pdf) — worth checking both in a future direct-fetch pass in case they differ (e.g. an update). A third-party source (consumercomplaints.in / complainthub.org) cited "~250 complaints/day on water pollution" at HMWSSB's call centre — NOT used above as it is not an official-domain claim; noted here only for context.
```

### Record: Telangana-Hyderabad-Roads-Potholes
```
service_id: ts-hyderabad-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting, damaged/missing catch pits, roadside silt removal
problem_type: potholes

state: Telangana
district: Hyderabad
city: Hyderabad
municipality: Greater Hyderabad Municipal Corporation (GHMC)
zone: GHMC's road/pothole responsibility covers its ~626 sq km jurisdiction; regional roads beyond city limits (expressways, Outer Ring Road/ORR alignment) fall under the Hyderabad Metropolitan Development Authority (HMDA) instead — a jurisdiction split confirmed via multiple search summaries, though not read directly from a single official comparison document.
ward: Citizen's Charter services (including pothole filling) are stated to be delivered at Ward Level Offices, GHMC's 150 wards

department: NOT FOUND IN OFFICIAL SOURCE (GHMC's Engineering/Public Works function handles roads per general descriptions, but no specific department name/officer was confirmed on an official page)
authority: Greater Hyderabad Municipal Corporation (municipal roads); Hyderabad Metropolitan Development Authority (HMDA) for regional infrastructure/ORR — jurisdiction split, do not conflate the two bodies
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GHMC's Citizen's Charter lists pothole-filling, replacement of damaged/missing catch pits, and removal of accumulated roadside silt among the 17 civic services delivered at Ward Level Offices. The MyGHMC app separately allows citizens to submit pothole complaints alongside open manholes and streetlight issues.
procedure: Report via the MyGHMC app, at the nearest Ward Level Office, via ghmc.gov.in online services, or via igs.ghmc.gov.in (Integrated Grievance System). Complaint escalation is possible through zonal commissioners if unresolved.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — a "24-hour" pothole-filling commitment was reported repeatedly by news coverage (newsmeter.in headline explicitly states this) of GHMC's Citizen's Charter, and the official PDF's URL was independently located (see source below) — but the figure was not read directly from GHMC's own PDF body text in this pass. Do not treat as verified.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: MyGHMC mobile app, Ward Level Offices, ghmc.gov.in online services, Integrated Grievance System (igs.ghmc.gov.in), GHMC call centre 040-2111 1111
contact_information: GHMC call centre 040-2111 1111

escalation_procedure: Escalation to zonal commissioners is possible for unresolved road-maintenance complaints (per general search summaries); the same Citizen's Charter-based escalation to the Public Grievance Cell / Commissioner / Joint Commissioners described in the Waste record above is presumed to apply, though not confirmed specifically for this category.
escalation_authority: Zonal Commissioner (GHMC) → Public Grievance Cell / Commissioner (GHMC) — same general chain as other GHMC services

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen's Charter — Hyderabad
source_url: https://www.ghmc.gov.in/CitizenCharter/CitizenCharter-19.06.pdf
source_type: citizen_charter
source_organization: Greater Hyderabad Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: The GHMC-vs-HMDA jurisdiction split for roads is a genuinely useful cross-cutting finding (city roads = GHMC, regional/ORR = HMDA) but was not traced to one single authoritative comparison document in this pass — multiple independent search summaries converged on it, which increases confidence, but it should still be direct-fetch-confirmed (e.g. against an HMDA G.O. — one such document, hmda.gov.in/wp-content/uploads/2020/07/G.O.Ms_.No_.-470-dt-09-07-08.pdf, surfaced in search results and is a promising follow-up target).
```

### Record: Telangana-Hyderabad-Streetlight
```
service_id: ts-hyderabad-streetlight
service_name: Streetlights
sub_service: Streetlight repair, non-functioning streetlight
problem_type: streetlight_not_working

state: Telangana
district: Hyderabad
city: Hyderabad
municipality: Greater Hyderabad Municipal Corporation (GHMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: Citizen's Charter services (including streetlight repair) are stated to be delivered at Ward Level Offices, GHMC's 150 wards

department: NOT FOUND IN OFFICIAL SOURCE
authority: Greater Hyderabad Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GHMC's Citizen's Charter lists streetlight repair among the 17 civic services delivered at Ward Level Offices. The MyGHMC app separately allows citizens to report dysfunctional streetlights alongside potholes and open manholes.
procedure: Report via the MyGHMC app, at the nearest Ward Level Office, or via ghmc.gov.in online services / igs.ghmc.gov.in.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — a "24-hour" streetlight-repair commitment was reported by news coverage of GHMC's Citizen's Charter (grouped together with pothole-filling and catch-pit replacement in the same 24-hour tier) — not read directly from the official PDF in this pass. Do not treat as verified.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: MyGHMC mobile app, Ward Level Offices, ghmc.gov.in online services, Integrated Grievance System (igs.ghmc.gov.in)
contact_information: GHMC call centre 040-2111 1111

escalation_procedure: ESCALATION INFORMATION NOT FOUND specifically for streetlights (same general GHMC chain as other services is presumed to apply — see Waste record above — but not confirmed category-specifically)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE (category-specific)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen's Charter — Hyderabad
source_url: https://www.ghmc.gov.in/CitizenCharter/CitizenCharter-19.06.pdf
source_type: citizen_charter
source_organization: Greater Hyderabad Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Notably, unlike Pune/Mumbai/Nagpur in Maharashtra and both AP cities, Hyderabad's streetlight category is NOT the thinnest-documented one here — it is explicitly folded into GHMC's Ward Level Office Citizen's Charter alongside potholes, which is a more concrete channel than most other cities researched had for this category. Still, no dedicated Smart-City/ICCC-specific streetlight channel distinct from the general MyGHMC app was found.
```

### Record: Telangana-Warangal-Waste-GarbageCollection
```
service_id: ts-warangal-waste-garbage-collection
service_name: Waste & Public Sanitation
sub_service: Garbage collection, general sanitation complaints
problem_type: garbage_collection

state: Telangana
district: Warangal / Hanumakonda
city: Warangal
municipality: Greater Warangal Municipal Corporation (GWMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (Health Section is named among GWMC's general departments — health, town planning, citizen charter, engineering, grievance, pension, property tax, trade license — but sanitation/SWM specifically was not further broken out on an official page in this pass)
authority: Greater Warangal Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GWMC provides services through several departments including its Health Section (general sanitation function implied). Citizens register online complaints by selecting the complaint type and locality, and providing name, email, phone number, address, house number, and complaint details.
procedure: Register online via gwmc.gov.in/grievance_registration.aspx, selecting complaint type and locality.
required_information: Name, email id, phone number, address, house number, complaint details
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND. The GWMC Commissioner has publicly directed officials to "expedite the resolution of citizen complaints" and address them "within the stipulated time frame" per a news report (thehansindia.com) about a Commissioner directive — but no specific published day-count was found on an official gwmc.gov.in page, and per the environment constraint this news-sourced figure/claim is excluded from this field.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: gwmc.gov.in online grievance registration form
contact_information: Call Center 0870-2500781, Email admin@gwmc.gov.in (unconfirmed exact address), Website gwmc.gov.in

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Grievance Registration — GWMC
source_url: https://gwmc.gov.in/grievance_registration.aspx
source_type: grievance_portal
source_organization: Greater Warangal Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: GWMC's coverage in this pass is thinner than GHMC's — no dedicated app or citizen charter PDF for GWMC specifically was located (a training/NGO PDF from covanetwork.org claims GWMC and its "Water Works & Electricity Department" have adopted Citizens' Charters, but per the D-quality rule for non-official sources this is logged as a lead for future direct-fetch follow-up, not used as a confirmed fact).
```

### Record: Telangana-Warangal-Water-Drainage
```
service_id: ts-warangal-water-drainage
service_name: Water & Drainage
sub_service: Water and sewerage connections/complaints
problem_type: sewage_drainage_problems

state: Telangana
district: Warangal / Hanumakonda
city: Warangal
municipality: Greater Warangal Municipal Corporation (GWMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (a "Water Works & Electricity Department" is referenced as having adopted its own Citizens' Charter, per a non-official training-material PDF found in this pass — NOT confirmed on an official gwmc.gov.in page, so not entered as a confirmed department name)
authority: Greater Warangal Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GWMC provides Water & Sewerage Connection services (per the National Government Services Portal listing). Unlike Hyderabad (where HMWSSB is a wholly separate board — see the Hyderabad Water & Drainage record above), no evidence surfaced in this pass of a separate water board serving Warangal; water/sewerage appears to sit within GWMC itself, though this should be reconfirmed directly.
procedure: Register a water/sewerage complaint via gwmc.gov.in's general grievance registration form (selecting the appropriate complaint type/locality), or apply for a new water/sewerage connection via the National Government Services Portal listing.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: gwmc.gov.in online grievance registration form
contact_information: Call Center 0870-2500781

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Water & Sewerage Connection for Warangal Municipal Corporation, Telangana
source_url: https://services.india.gov.in/service/detail/water-and-sewerage-connection-for-warangal-municipal-corporation-telangana
source_type: govt_portal
source_organization: National Government Services Portal (Govt. of India), describing a Warangal Municipal Corporation service

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: The water/drainage jurisdiction question (own GWMC dept vs. a separate board) is unresolved for Warangal in this pass — flagged as a specific follow-up item, especially since it differs by city even within the same state (compare Hyderabad's HMWSSB split above).
```

### Record: Telangana-Warangal-Roads-Potholes
```
service_id: ts-warangal-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting, road maintenance
problem_type: potholes

state: Telangana
district: Warangal / Hanumakonda
city: Warangal
municipality: Greater Warangal Municipal Corporation (GWMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (a training-material PDF, not an official government source, claims potholes fall under GWMC's "Engineering Section" — logged in notes only, not entered as a confirmed department name per the D-quality rule)
authority: Greater Warangal Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GWMC's general online complaint form covers road-related issues among other civic complaint types (per its complaint-type/locality selection structure).
procedure: Register via gwmc.gov.in/grievance_registration.aspx, selecting the road/pothole complaint type and locality.
required_information: Name, email id, phone number, address, house number, complaint details
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: gwmc.gov.in online grievance registration form
contact_information: Call Center 0870-2500781

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Grievance Registration — GWMC
source_url: https://gwmc.gov.in/grievance_registration.aspx
source_type: grievance_portal
source_organization: Greater Warangal Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Thin record — GWMC's own domain confirms the existence of a general complaint channel covering roads, but no department name, SLA, or escalation chain specific to this category was found on an official page in this pass.
```

### Record: Telangana-Warangal-Streetlight
```
service_id: ts-warangal-streetlight
service_name: Streetlights
sub_service: Non-functioning streetlight
problem_type: streetlight_not_working

state: Telangana
district: Warangal / Hanumakonda
city: Warangal
municipality: Greater Warangal Municipal Corporation (GWMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (a non-official training PDF references GWMC's "Water Works & Electricity Department" as the streetlight-adjacent unit — see notes; not entered as a confirmed department per the D-quality rule)
authority: Greater Warangal Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GWMC's general online complaint form covers streetlight issues among other civic complaint types.
procedure: Register via gwmc.gov.in/grievance_registration.aspx.
required_information: Name, email id, phone number, address, house number, complaint details
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: gwmc.gov.in online grievance registration form
contact_information: Call Center 0870-2500781

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Grievance Registration — GWMC
source_url: https://gwmc.gov.in/grievance_registration.aspx
source_type: grievance_portal
source_organization: Greater Warangal Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: As expected per 01_service_data_requirements.md, this is the thinnest-documented of GWMC's 4 categories — no dedicated channel, department, SLA, or escalation path distinct from the general grievance form was found.
```

### Record: Telangana-Warangal-Waste-SolidWasteDisposal-Dataset
```
service_id: ts-warangal-waste-swm-dataset
service_name: Waste & Public Sanitation
sub_service: Solid waste management — structured operational dataset
problem_type: garbage_collection

state: Telangana
district: Warangal / Hanumakonda
city: Warangal
municipality: Greater Warangal Municipal Corporation (GWMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Ministry of Housing & Urban Affairs — Smart Cities Mission (dataset published on behalf of Greater Warangal Smart City)
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: OGD Platform India catalog entry "Solid Waste Disposal : Warangal" — defines source segregation, D2D collection efficiency, bin placement/sizes, collection vehicles/capacity, and disposal/processing options.
procedure: NOT APPLICABLE (structured dataset)
required_information: NOT APPLICABLE
required_documents: NOT APPLICABLE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: NOT APPLICABLE
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Solid Waste Disposal : Warangal
source_url: https://www.data.gov.in/catalog/solid-waste-disposal-warangal
source_type: smart_city_dataset
source_organization: Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD Platform India

publication_date: 29/04/2019 (per search-result metadata)
last_updated: 18/02/2025 (per search-result metadata)
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: C
geographic_scope: city
notes: Structured/SQL-oriented; no equivalent data.gov.in dataset for Hyderabad/GHMC specifically was located in this pass (only a third-party OpenCity.in portal had a Hyderabad SWM dataset — NOT data.gov.in, logged as a gap rather than substituted in).
```

### Record: Telangana-StateWide-AllServices-MAUD-GrievanceRedressal
```
service_id: ts-statewide-all-maud-grievance-redressal
service_name: (cross-cutting — applies to all 4 categories, all Telangana ULBs)
sub_service: General state-level grievance intake and ULB routing
problem_type: multiple

state: Telangana
district: NOT APPLICABLE (state-wide)
city: NOT APPLICABLE (applies to all Urban Local Bodies under CDMA Telangana, including Hyderabad/GHMC and Warangal/GWMC)
municipality: All Telangana Urban Local Bodies
zone: NOT APPLICABLE
ward: NOT APPLICABLE

department: Commissioner and Director of Municipal Administration (CDMA), Telangana
authority: Municipal Administration and Urban Development (MA&UD) Department, Government of Telangana
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: An integrated, portal-based citizen help-desk and grievance-redressal mechanism is described (per CDMA Telangana's own page) under which citizens send complaints/suggestions/grievances via post, phone, fax, or email; grievances are forwarded to the concerned Department/Section of the respective ULB depending on the nature of the grievance, and the relevant staff attend to the complaint within a given time period and reply to the citizen help-desk. Citizens with internet access can check grievance status online.
procedure: Submit via post, phone, fax, or email to the relevant ULB; status can be checked online.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND (a "given time period" is referenced generically but no specific day-count was found on this page)
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Post, phone, fax, email, online status-check; individual ULB pages (e.g. nalgondamunicipality.telangana.gov.in/086/grievance-redressal, miryalagudamunicipality.telangana.gov.in/pages/grievance-redressal) follow the same general template
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: ESCALATION INFORMATION NOT FOUND at this state-policy-description level
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Commissioner and Director of Municipal Administration (CDMA), Municipal Administration and Urban Development (MA&UD) Department — Grievance Redressal
source_url: https://emunicipal.telangana.gov.in/Grievance_Redressal
source_type: govt_portal
source_organization: Commissioner and Director of Municipal Administration, Telangana

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: state
notes: A separate Telangana-wide state grievance system, Prajavani (Centralized Public Grievance Redress and Monitoring System / PGRAMS), was also found — it reportedly auto-escalates unresolved grievances within 12 days to the Chief Innovation Officer of Telangana State. This is a specific, promising day-count claim, but it was found via a general aggregator-style summary (filemyrti.com) rather than confirmed directly on an official telangana.gov.in Prajavani page in this pass — flagged here as a high-priority direct-fetch target rather than entered into the sla/escalation fields above. Note also that Telangana's older CPGRAMS-style portal (cpgrams.ts.nic.in) was reported as discontinued (per search summary) as of June 1, 2026 — worth confirming which state grievance system is currently authoritative before relying on any URL found under the old system.
```

---

## Coverage notes for Telangana

- **Best-covered service:** Roads & Potholes and Streetlights for
  Hyderabad specifically — unusually, both are explicitly named among
  GHMC's 17 Ward-Level-Office Citizen's Charter services, giving them
  more concrete channel/structure detail than is typical for these two
  categories elsewhere in this 3-state research pass (compare
  Maharashtra's `maharashtra.md`, where streetlights was consistently
  the weakest category).
- **Weakest-covered city:** Warangal (GWMC) — no dedicated app or
  citizen-charter PDF for GWMC specifically was located on an official
  domain; all 4 of its service records are thin, differing mainly by
  complaint-type label within the same generic online form.
- **Most significant jurisdiction-split finding of the whole 3-state
  pass:** Hyderabad's water supply and sewerage sit with **HMWSSB, a
  wholly separate statutory board** from GHMC — confirmed via HMWSSB's
  own official domain (`hyderabadwater.gov.in`), its own Citizen's
  Charter, and its own call centre/helpline numbers, distinct from
  GHMC's. This is a textbook example of exactly the kind of split
  `01_service_data_requirements.md` warns must be captured explicitly
  per city, never assumed. By contrast, Warangal shows no evidence of a
  separate water board (water/sewerage appears to sit with GWMC
  directly) — so the split does not even hold consistently *within*
  Telangana, let alone across states.
- **Highest-value direct-fetch follow-up found in this entire pass:**
  GHMC's official Citizen's Charter PDF
  (`https://www.ghmc.gov.in/CitizenCharter/CitizenCharter-19.06.pdf`).
  Its existence and exact URL were independently located on GHMC's own
  domain, and multiple independent news outlets consistently describe
  specific SLA tiers (24-hour / same-day / 48-hour) and a per-day-of-
  delay compensation clause (Rs.50 for Revenue/Engineering/Health,
  Rs.100 for Town Planning) as being drawn from it — but because none of
  that was read directly from the PDF itself in this pass, none of it
  was entered into any `sla` field. If a future pass can actually open
  this PDF, it could upgrade several NOT-FOUND fields across all 4
  Hyderabad service records simultaneously.
- **Quality-A sources found:** `ghmc.gov.in/CitizenCharter/CitizenCharter-19.06.pdf`,
  `igs.ghmc.gov.in`, `hyderabadwater.gov.in` (both the Citizen's Charter
  PDF and the Contact Us page), and `gwmc.gov.in`'s grievance/contact
  pages — all rated A on domain-and-topic specificity per the rubric,
  none independently fetched and read.
- As with the other two states in this pass, no specific SLA day-count
  anywhere in this file was traced to an official-domain page body text
  directly — every numeric figure that surfaced came from news or
  third-party summaries and was deliberately excluded from `sla` /
  `response_time` / `resolution_time` / `escalation_procedure` fields,
  logged only in `notes`.
