# Andhra Pradesh — Official Source Inventory

**Cities researched:** Visakhapatnam (GVMC), Vijayawada (VMC)
**Method:** WebSearch only. WebFetch (direct page-fetch/verification) was
completely unavailable in this environment for this entire pass (tested
against multiple domains including government sites — all
`EGRESS_BLOCKED`). Every record below is marked `NOT INDEPENDENTLY
FETCHED — confirm before production use` in `verification_status`.
`source_quality` reflects how official/specific the *domain and
search-result context* is per the `00_README.md` rubric — quality A is
only assigned where the URL itself is unambiguously an official
government domain (`.gov.in`, `cdma.ap.gov.in`, `gvmc.gov.in`,
`data.gov.in`, etc.), never upgraded because a search-engine summary
sounded detailed.

> **Environment note (same caveat as `maharashtra.md`):** Everything here
> relies on WebSearch result metadata (URL, title, search-engine-
> generated summary), not a direct fetch-and-read of page content.
> Anything presented as an official-domain URL is genuinely real and
> currently indexed, but exact wording (SLA day-counts, escalation
> chains, officer titles) is reported-by-search, not confirmed-by-direct-
> read, until someone with working fetch access opens the URL directly.
> Per the environment constraint given for this pass, **any specific
> numeric SLA or escalation-day-count that only appeared attributed to a
> non-government domain (news sites, blogs, complaint aggregators) was
> NOT entered into the `sla` / `escalation_procedure` fields** — those
> fields carry the sentinel value instead, with the third-party figure
> (clearly labeled unverified) moved to `notes` for context only.

---

## Summary table

| State | City | Service | Source | Authority | URL | Format | Data Available | RAG or SQL | Quality |
|---|---|---|---|---|---|---|---|---|---|
| Andhra Pradesh | Visakhapatnam | All services (grievance mechanism) | Modes Of Registering Grievances By The Citizens / IVRS | Greater Visakhapatnam Municipal Corporation (GVMC) | https://www.gvmc.gov.in/static_content/Grievances.jsp | HTML | Procedure, 3-level escalation, IVRS | RAG | A |
| Andhra Pradesh | Visakhapatnam | All services (app channel) | Smart Vizag (GVMC's citizen app) | GVMC | https://www.gvmc.gov.in/ | HTML | Channel (app), general info | RAG | A |
| Andhra Pradesh | Visakhapatnam | Waste & Sanitation | Solid Waste Management : Visakhapatnam (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | https://www.data.gov.in/catalog/solid-waste-management-visakhapatnam | Dataset (catalog) | Source segregation, D2D efficiency, bin placement, collection vehicles | Structured/SQL | C |
| Andhra Pradesh | Vijayawada | All services (grievance mechanism) | Grievances for Vijayawada Municipal Corporation Commissioner | services.india.gov.in (National Government Services Portal, Govt. of India) | https://services.india.gov.in/service/detail/grievances-for-vijayawada-municipal-corporation-commissioner-andhra-pradesh | HTML | Procedure (write to commissioner) | RAG | B |
| Andhra Pradesh | Vijayawada | All services (status check) | Check status of complaints against Vijayawada Municipal Corporation | services.india.gov.in | https://services.india.gov.in/service/detail/check-status-of-complaints-against-vijayawada-municipal-corporation-1 | HTML | Channel, status-check | RAG | B |
| Andhra Pradesh | Vijayawada | All services (ULB portal) | Vijayawada Municipal Corporation — Online Services | Vijayawada Municipal Corporation, via CDMA AP State Portal | https://vijayawada.cdma.ap.gov.in/services | HTML | Channel, generic complaint categories | RAG | A |
| Andhra Pradesh | Vijayawada | Water & Drainage | Vijayawada City Development Plan — Ch.4.14 (JNNURM) | Vijayawada Municipal Corporation (via ourvmc.org, VMC's own legacy domain) | http://www.ourvmc.org/jnnurm/ch414.pdf | PDF | Water source mix, sewage generation/STP capacity (dated, city-planning context) | RAG | B |
| Andhra Pradesh | (state-wide, applies to both cities) | All services | Citizen Charter | CDMA — Commissioner & Director of Municipal Administration, Govt. of Andhra Pradesh | https://www.cdma.ap.gov.in/others/portal-info/citizen-charter/ | HTML | Policy framework (applies to all AP ULBs incl. GVMC, VMC) | RAG | B |
| Andhra Pradesh | (state-wide) | All services | Grievances | CDMA, Govt. of Andhra Pradesh | https://cdma.ap.gov.in/services/grievances/ | HTML | Procedure, channel | RAG | B |
| Andhra Pradesh | (state-wide) | All services | Puramithra Initiative | CDMA, Govt. of Andhra Pradesh | https://cdma.ap.gov.in/initiatives/puramithra/ | HTML | ERP/app description, channel | RAG | B |
| Andhra Pradesh | (state-wide) | All services | Public Grievance Redressal System (PGRS) | Government of Andhra Pradesh | https://pgrs.ap.gov.in/Dashboard/OfficerDashboard | Web app | Escalation levels, re-open mechanism | RAG | B |
| Andhra Pradesh | Visakhapatnam (reference only) | (reference only, not verified fact source) | GVMC, Vizag: How to File a Complaint | complainthub.org (third-party) | https://complainthub.org/gvmc-vizag-help/ | HTML | Aggregated complaint-channel info, unverifiable claims | reference only | D |
| Andhra Pradesh | Visakhapatnam (reference only) | (reference only, not verified fact source) | GVMC contact numbers to register complaints | yovizag.com (local news, third-party) | https://www.yovizag.com/gvmc-complaints-number-visakhapatnam/ | HTML | Contact numbers, unverifiable procedural detail | reference only | D |
| Andhra Pradesh | Vijayawada (reference only) | (reference only, not verified fact source) | Vijayawada Municipal Corporation Complaints | consumercomplaints.in (third-party) | https://www.complaintboard.in/complaints-reviews/vijayawada-municipal-corporation-l545689.html | HTML | Citizen-submitted complaint log, not an authoritative procedure source | reference only | D |

---

## Full records

### Record: AndhraPradesh-Visakhapatnam-Waste-GarbageCollection
```
service_id: ap-visakhapatnam-waste-garbage-collection
service_name: Waste & Public Sanitation
sub_service: Garbage collection / missed collection, illegal dumping, UGD-related sanitation
problem_type: garbage_collection

state: Andhra Pradesh
district: Visakhapatnam
city: Visakhapatnam
municipality: Greater Visakhapatnam Municipal Corporation (GVMC)
zone: NOT FOUND IN OFFICIAL SOURCE (GVMC operates a zonal structure per its escalation chain — see below — but a specific zone list was not surfaced)
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (routed internally by category; specific SWM department/officer name not confirmed on an official page in this pass)
authority: Greater Visakhapatnam Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE (see escalation_authority below for the escalation-chain designations, which ARE named)

description: GVMC's citizen grievance system accepts e-complaints covering removal of garbage, desilting of drains, absenteeism of the door-to-door garbage collector, UGD (underground drainage) overflow, and other civic/sanitation concerns, alongside water supply and other issues.
procedure: File via the Smart Vizag app, the gvmc.gov.in website's online grievance system, the toll-free helpline, WhatsApp, email, or by writing to designated officers; complaints are also logged into the state's Public Grievance Redressal System (PGRS). Written grievances can be submitted in person every Monday between 11:00am and 1:00pm.
required_information: Grievance/area details, name (per GVMC's own grievance-mechanism description); photo capture supported via the Smart Vizag app for civic-issue reporting.
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — no numeric day-count for garbage-collection resolution was found attributed to an official gvmc.gov.in or cdma.ap.gov.in page in this pass.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Smart Vizag mobile app, gvmc.gov.in online grievance system, toll-free 1800-4250-0009, WhatsApp 9666909192, in-person Monday 11am-1pm
contact_information: Toll-free 1800-4250-0009 / WhatsApp 9666909192 / GVMC HQ phone 0891-2746300 (Tenneti Bhavan, Opp. Royal Fort, Ramnagar, Visakhapatnam-530002)

escalation_procedure: 3-level mechanism per GVMC's own grievance page. Level 1: complaint to the concerned department officer of GVMC. Level 2: if unresolved within the redressal time limit, escalate to the Zonal Municipal Commissioner or the Additional Deputy Commissioner (ADC) of the relevant department. Level 3: if still unresolved to the citizen's satisfaction, lodge a grievance with the Public Grievance Cell (Nodal Officer) of the Municipal Administration and Urban Development (MA&UD) Department, Government of Andhra Pradesh.
escalation_authority: Concerned department officer (GVMC) → Zonal Municipal Commissioner / ADC (GVMC) → Public Grievance Cell (Nodal Officer), MA&UD Dept, Govt. of Andhra Pradesh

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Modes Of Registering Grievances By The Citizens (IVRS)
source_url: https://www.gvmc.gov.in/static_content/Grievances.jsp
source_type: govt_portal
source_organization: Greater Visakhapatnam Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A because gvmc.gov.in is unambiguously GVMC's own official domain and the page (title confirmed via search: "Modes Of Registering Grievances By The Citizens IVRS") is directly about this exact procedure — but page body text was not read directly, only confirmed to exist via search metadata; re-verify before treating any specific claim as final. Some third-party sources (complainthub.org, yovizag.com) claim a 3-7 day resolution window for garbage complaints — this did NOT appear on an official page in this pass and is NOT used above; treat as unverified if it resurfaces elsewhere.
```

### Record: AndhraPradesh-Visakhapatnam-Water-Drainage
```
service_id: ap-visakhapatnam-water-drainage
service_name: Water & Drainage
sub_service: Drinking water supply issues, UGD overflow, drain desilting, pipeline/leak problems
problem_type: no_low_water_supply

state: Andhra Pradesh
district: Visakhapatnam
city: Visakhapatnam
municipality: Greater Visakhapatnam Municipal Corporation (GVMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE — GVMC appears to run its own water-supply engineering wing (references to a Superintending Engineer overseeing water supply/sewerage with Executive/Assistant Engineers by zone), but this was only corroborated via non-official sources (Scribd document, Grokipedia) in this pass, not a gvmc.gov.in page directly — do not treat the engineering-hierarchy detail as confirmed.
authority: Greater Visakhapatnam Municipal Corporation (GVMC is directly responsible for water supply — unlike some states, no separate water board jurisdiction was found for Visakhapatnam city itself in this pass; this should still be reconfirmed directly per 01_service_data_requirements.md's caution against assuming)
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GVMC's citizen e-complaint categories explicitly include drinking water supply issues, UGD (underground drainage) overflow, and desilting of drains, alongside general sanitation/hygiene complaints.
procedure: Same channels as other GVMC complaints — Smart Vizag app, gvmc.gov.in online grievance system, toll-free helpline, WhatsApp, IVRS (with Telugu/English/Hindi language options and complaint-category selection).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Smart Vizag app, gvmc.gov.in online grievance system, toll-free 1800-4250-0009 (IVRS with language + category selection), WhatsApp 9666909192
contact_information: Toll-free 1800-4250-0009 / WhatsApp 9666909192

escalation_procedure: Same 3-level mechanism as other GVMC services (see Waste record above): department officer → Zonal Commissioner/ADC → MA&UD Public Grievance Cell.
escalation_authority: Concerned department officer (GVMC) → Zonal Municipal Commissioner / ADC → Public Grievance Cell (Nodal Officer), MA&UD Dept, Govt. of Andhra Pradesh

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Modes Of Registering Grievances By The Citizens (IVRS)
source_url: https://www.gvmc.gov.in/static_content/Grievances.jsp
source_type: govt_portal
source_organization: Greater Visakhapatnam Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Unlike Hyderabad (see telangana.md — HMWSSB is a separate board), no evidence surfaced in this pass of a separate water board for Visakhapatnam city proper; GVMC appears to hold water-supply responsibility directly. This is a meaningful jurisdiction-split finding worth flagging for direct-fetch confirmation, since it differs from the Telangana pattern.
```

### Record: AndhraPradesh-Visakhapatnam-Roads-Potholes
```
service_id: ap-visakhapatnam-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting, road/bridge maintenance
problem_type: potholes

state: Andhra Pradesh
district: Visakhapatnam
city: Visakhapatnam
municipality: Greater Visakhapatnam Municipal Corporation (GVMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Greater Visakhapatnam Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: The Smart Vizag app lets citizens create service requests for roads (in addition to streetlights and drains), reporting civic issues such as potholes and bridges/roads maintenance.
procedure: Submit a service request via the Smart Vizag app or gvmc.gov.in's online grievance system; a complaint number is issued, an SMS is sent to the concerned official, and the complainant is informed of the complaint number and the responsible official's contact details.
required_information: NOT FOUND IN OFFICIAL SOURCE (app supports QR-code-based complaint registration per search summary, but photo/GPS requirement specifics not confirmed)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Smart Vizag mobile app, gvmc.gov.in online grievance system, toll-free 1800-4250-0009, WhatsApp 9666909192
contact_information: Toll-free 1800-4250-0009 / WhatsApp 9666909192

escalation_procedure: Same 3-level mechanism as other GVMC services (see Waste record above).
escalation_authority: Concerned department officer (GVMC) → Zonal Municipal Commissioner / ADC → Public Grievance Cell (Nodal Officer), MA&UD Dept, Govt. of Andhra Pradesh

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: GVMC official site / Smart Vizag app listing
source_url: https://www.gvmc.gov.in/
source_type: govt_portal
source_organization: Greater Visakhapatnam Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: No jurisdiction split (municipal road vs. state highway/NH) surfaced for Visakhapatnam in this pass — worth a targeted follow-up given the port city has NH sections running through it.
```

### Record: AndhraPradesh-Visakhapatnam-Streetlight
```
service_id: ap-visakhapatnam-streetlight
service_name: Streetlights
sub_service: Non-functioning streetlight, damaged pole
problem_type: streetlight_not_working

state: Andhra Pradesh
district: Visakhapatnam
city: Visakhapatnam
municipality: Greater Visakhapatnam Municipal Corporation (GVMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Greater Visakhapatnam Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: The Smart Vizag app allows citizens to create service requests for street lights (alongside roads and drains); GVMC's citizen services page also lists streetlight-related complaints as a standard e-complaint category.
procedure: File via Smart Vizag app, gvmc.gov.in online grievance system, toll-free helpline, or WhatsApp.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Smart Vizag mobile app, gvmc.gov.in online grievance system, toll-free 1800-4250-0009, WhatsApp 9666909192
contact_information: Toll-free 1800-4250-0009 / WhatsApp 9666909192

escalation_procedure: Same 3-level mechanism as other GVMC services (see Waste record above).
escalation_authority: Concerned department officer (GVMC) → Zonal Municipal Commissioner / ADC → Public Grievance Cell (Nodal Officer), MA&UD Dept, Govt. of Andhra Pradesh

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: GVMC official site / Smart Vizag app listing
source_url: https://www.gvmc.gov.in/
source_type: govt_portal
source_organization: Greater Visakhapatnam Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Least-detailed of GVMC's 4 service records, consistent with the expectation in 01_service_data_requirements.md that streetlights tend to have the thinnest dedicated documentation. No dedicated Smart-City/ICCC streetlight channel distinct from the general Smart Vizag app surfaced in this pass.
```

### Record: AndhraPradesh-Visakhapatnam-Waste-SolidWasteManagement-Dataset
```
service_id: ap-visakhapatnam-waste-swm-dataset
service_name: Waste & Public Sanitation
sub_service: Solid waste management — structured operational dataset
problem_type: garbage_collection

state: Andhra Pradesh
district: Visakhapatnam
city: Visakhapatnam
municipality: Greater Visakhapatnam Municipal Corporation (GVMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Ministry of Housing & Urban Affairs — Smart Cities Mission (dataset published on behalf of GVMC/Visakhapatnam Smart City)
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: OGD Platform India catalog entry "Solid Waste Management : Visakhapatnam" — defines source segregation, door-to-door (D2D) collection efficiency, placement/sizes of bins, collection vehicles and their capacity, and disposal/processing options for the city.
procedure: NOT APPLICABLE (structured dataset, not a citizen procedure page)
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

source_title: Solid Waste Management : Visakhapatnam
source_url: https://www.data.gov.in/catalog/solid-waste-management-visakhapatnam
source_type: smart_city_dataset
source_organization: Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD Platform India

publication_date: 09/02/2019 (per search-result metadata)
last_updated: 18/02/2025 (per search-result metadata)
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: C
geographic_scope: city
notes: Structured/SQL-oriented record, not citizen-facing procedural text — useful for analytics (collection efficiency, fleet capacity) rather than complaint-handling grounding. Dates above are as reported by search-result metadata, not independently confirmed by opening the catalog page.
```

### Record: AndhraPradesh-Vijayawada-AllServices-GrievanceMechanism
```
service_id: ap-vijayawada-all-grievance-mechanism
service_name: (cross-cutting — grievance system covers all 4 categories)
sub_service: General civic grievance registration, status check, reminder
problem_type: multiple (garbage/street cleanliness, water supply issues, road damage/potholes explicitly named as reportable categories per the CDMA ULB portal's generic service listing)

state: Andhra Pradesh
district: Krishna
city: Vijayawada
municipality: Vijayawada Municipal Corporation (VMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Vijayawada Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Vijayawada's citizen-services portal (hosted on the CDMA AP State Portal, the same platform template used across Andhra Pradesh's ULBs) lists grievance categories including garbage collection/street cleaning/public sanitation, water supply issues/leakages/quality concerns, and road damage/potholes/maintenance requirements. Citizens can also write directly to the VMC Commissioner online with name, phone, email, and complaint details (per the National Government Services Portal listing).
procedure: File via vijayawada.cdma.ap.gov.in's online services section, or write to the VMC Commissioner online (name, phone, email id, feedback/problem details) per services.india.gov.in. Complaint status and history can be checked by entering a registration number; a complaint reminder can also be filed online by registration number.
required_information: Name, phone number, email id, complaint/feedback details (per services.india.gov.in's description of the Commissioner write-in channel); registration number (for status check/reminder)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: vijayawada.cdma.ap.gov.in online services, write-to-Commissioner web form, complaint status-check and reminder services via services.india.gov.in
contact_information: 0864-527-7727 (per VMC's official contact-information page); NOT FOUND IN OFFICIAL SOURCE for a dedicated toll-free/WhatsApp channel distinct from GVMC's

escalation_procedure: ESCALATION INFORMATION NOT FOUND (VMC-specific escalation chain not surfaced in this pass — VMC, like other AP ULBs, is presumably covered by the same state PGRS/CDMA framework described in the state-wide records below, but this was not confirmed specifically for Vijayawada)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Vijayawada Municipal Corporation — Online Services
source_url: https://vijayawada.cdma.ap.gov.in/services
source_type: govt_portal
source_organization: Vijayawada Municipal Corporation (via CDMA AP State Portal)

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Vijayawada's official web presence found in this pass is noticeably thinner and more templated (generic CDMA ULB-portal boilerplate) than GVMC's, which has its own distinct grievance page, app, and IVRS. This is a genuine coverage gap, not an oversight — worth a targeted follow-up search specifically for a VMC-specific citizen charter PDF or app (distinct from the generic CDMA template).
```

### Record: AndhraPradesh-Vijayawada-Water-Drainage
```
service_id: ap-vijayawada-water-drainage
service_name: Water & Drainage
sub_service: Drinking water supply, sewerage/underground drainage, storm-water drainage
problem_type: sewage_drainage_problems

state: Andhra Pradesh
district: Krishna
city: Vijayawada
municipality: Vijayawada Municipal Corporation (VMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Vijayawada Municipal Corporation (stated as directly responsible for maintaining and supplying drinking water to the city, per VMC's own City Development Plan document — see source below)
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: VMC's City Development Plan (prepared under JNNURM) describes the city's water sources as the Krishna River, groundwater, overhead tanks, and hand bores, and states total sewage generation in corporation limits was estimated at 148 MLD against only ~20 MLD of utilizable sewage treatment plant (STP) capacity at the time of writing — a capacity shortfall the document itself flags as "very low."
procedure: NOT FOUND IN OFFICIAL SOURCE (this document is a planning/CDP report, not a citizen complaint-procedure page — see the AllServices record above for VMC's general complaint channels)
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: See AllServices record (vijayawada.cdma.ap.gov.in online services, write-to-Commissioner)
contact_information: NOT FOUND IN OFFICIAL SOURCE (specific to water/drainage)

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Vijayawada City Development Plan — Chapter 4.14 (Water Supply / Sewerage)
source_url: http://www.ourvmc.org/jnnurm/ch414.pdf
source_type: official_pdf
source_organization: Vijayawada Municipal Corporation (legacy VMC domain, ourvmc.org)

publication_date: NOT FOUND IN OFFICIAL SOURCE (JNNURM-era document, so likely mid-to-late 2000s; exact date not confirmed)
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: OUTDATED / VERIFY BEFORE PRODUCTION USE — this is a JNNURM-era (National Urban Renewal Mission, active ~2005-2014) City Development Plan document on VMC's own legacy `ourvmc.org` domain (served over plain HTTP, not HTTPS), so both its currency and its long-term availability are uncertain. It is planning/infrastructure-capacity content, not a citizen complaint procedure — useful only as background context on the water/sewerage jurisdiction (confirms VMC, not a separate board, is responsible), not as a source of any current SLA or procedure fact.
```

### Record: AndhraPradesh-StateWide-AllServices-CDMACitizenCharter
```
service_id: ap-statewide-all-cdma-citizen-charter
service_name: (cross-cutting — applies to all 4 categories, all AP Urban Local Bodies)
sub_service: Citizen Charter policy framework
problem_type: multiple

state: Andhra Pradesh
district: NOT APPLICABLE (state-wide)
city: NOT APPLICABLE (applies to all Urban Local Bodies under CDMA, including Visakhapatnam and Vijayawada)
municipality: All Andhra Pradesh Urban Local Bodies (123 ULBs per the PURAMITHRA platform description)
zone: NOT APPLICABLE
ward: NOT APPLICABLE

department: Commissioner & Director of Municipal Administration (CDMA)
authority: Municipal Administration and Urban Development (MA&UD) Department, Government of Andhra Pradesh
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: CDMA's own portal hosts a Citizen Charter page describing a Government Order on the Citizen Charter and citizen rights/services applicable across Andhra Pradesh's municipal administration system. CDMA also operates PURAMITHRA, the state's municipal-administration ERP covering all 123 ULBs (property tax, water tax, trade licenses, building permissions, municipal accounting, and grievance redressal), accessible via emunicipal.ap.gov.in and the Puramithra citizen app/portal.
procedure: Citizens log in via the Puramithra App or Citizen Portal, select the grievance category, submit required information, and track status/resolution progress. A dedicated Puramithra Grievances Dashboard is also published by CDMA.
required_information: NOT FOUND IN OFFICIAL SOURCE (category-dependent, not detailed at this state-policy level)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND (a Citizen Charter, by design, is meant to publish per-service timelines, but the specific day-counts per service were not surfaced/confirmed on an official CDMA page in this pass)
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Puramithra App / Citizen Portal, emunicipal.ap.gov.in
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: ESCALATION INFORMATION NOT FOUND at this state-policy level (see the PGRS record below for the state's general 3-level grievance-escalation structure, which appears to be the applicable mechanism)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen Charter
source_url: https://www.cdma.ap.gov.in/others/portal-info/citizen-charter/
source_type: citizen_charter
source_organization: Commissioner & Director of Municipal Administration (CDMA), Government of Andhra Pradesh

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: state
notes: Rated B (not A) because this is a state-level policy framework applying broadly across all AP ULBs, not tied to one specific city/service — per the quality rubric this is the correct rating even though the domain is unambiguously official. The actual Citizen Charter document body (with any per-service SLA table) was not read in this pass — a high-value direct-fetch follow-up target, since a confirmed SLA table here would apply as a B-quality baseline for both Visakhapatnam and Vijayawada.
```

### Record: AndhraPradesh-StateWide-AllServices-PGRS
```
service_id: ap-statewide-all-pgrs
service_name: (cross-cutting — applies to all 4 categories, state-wide)
sub_service: Public Grievance Redressal System — escalation/appellate mechanism
problem_type: multiple

state: Andhra Pradesh
district: NOT APPLICABLE (state-wide)
city: NOT APPLICABLE (state-wide, applies as the appellate layer above GVMC/VMC's own grievance systems)
municipality: NOT APPLICABLE (state-wide, all departments)
zone: NOT APPLICABLE
ward: NOT APPLICABLE

department: Public Grievance Redressal System (PGRS) — a cross-department platform, not a single line department
authority: Government of Andhra Pradesh (grievances ultimately route toward the Chief Minister's Office per the system's description)
officer_designation: Public Grievance Officer (Level 2); Head of Department / Secretary (Level 3) — per PGRS's own described level structure

description: PGRS is a universal, cross-department grievance-redressal helpline/platform for Andhra Pradesh allowing citizens to raise issues that can ultimately reach the Chief Minister's Office. It functions as the appellate layer above individual department/ULB-level grievance systems (e.g. GVMC's own 3-level mechanism feeds into PGRS per GVMC's grievance page).
procedure: Register a grievance via the official website, mobile app, or toll-free helpline. If not satisfied with the redressal, a citizen may re-open the grievance up to twice: the first re-open assigns it to a District Level Officer; if still unsatisfied, the second re-open escalates it to the Head of Department (HoD) level.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Official website (pgrs.ap.gov.in), mobile app, toll-free helpline
contact_information: NOT FOUND IN OFFICIAL SOURCE (specific toll-free number not confirmed on an official page in this pass)

escalation_procedure: 3-level structure per PGRS's own description: Level 1 — Local Office or Department (Nodal Officer); Level 2 — District/Department Grievance Cell (Public Grievance Officer); Level 3 — State Grievance Redressal Authority (Head of Department/Secretary). Citizens may additionally re-open a "resolved" grievance up to twice if unsatisfied, each re-open triggering escalation to a higher officer level as described above.
escalation_authority: Nodal Officer (Local Office/Dept) → Public Grievance Officer (District/Dept Grievance Cell) → Head of Department / Secretary (State Grievance Redressal Authority)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Public Grievance Redressal System (PGRS)
source_url: https://pgrs.ap.gov.in/Dashboard/OfficerDashboard
source_type: grievance_portal
source_organization: Government of Andhra Pradesh

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: state
notes: This is the strongest, most specific escalation-chain finding in the whole Andhra Pradesh pass (matches GVMC's own stated Level-3 destination) — a good direct-fetch priority since a confirmed multi-level escalation chain, once verified, is a highly reusable RAG fact applicable to both Visakhapatnam and Vijayawada records. A third-party source (The Wire, an independent news outlet — NOT used as a fact source here) raised concerns about delays and false closures within PGRS; not reflected in any field above, mentioned here only as context that the system's real-world performance may not match its documented process.
```

---

## Coverage notes for Andhra Pradesh

- **Best-covered city/service combination:** Visakhapatnam (GVMC) across all
  4 categories — GVMC has its own distinct, confirmed-official domain
  (`gvmc.gov.in`) with a dedicated grievance page, a named 3-level
  escalation chain, an app (Smart Vizag), and IVRS. This is the strongest
  single-city coverage found in this AP pass.
- **Weakest-covered city:** Vijayawada — its web presence surfaced in this
  pass is largely generic CDMA ULB-portal boilerplate rather than a
  VMC-specific citizen charter or dedicated app; only 2 full records
  were produced (vs. 4 for GVMC) plus the general grievance-mechanism
  record. A follow-up search specifically for a VMC-branded app or a
  standalone VMC citizen charter PDF (distinct from the CDMA template)
  is the highest-value next step for this city.
- **Weakest-covered service (both cities):** Streetlights, consistent
  with `01_service_data_requirements.md`'s expectation — no dedicated
  department name, SLA, or distinct channel surfaced for either city.
- **Water vs. drainage jurisdiction split:** Notably **different from the
  Telangana pattern** (see `telangana.md`, where Hyderabad's water supply
  and sewerage sit with a *separate* board, HMWSSB, not GHMC). For both
  Visakhapatnam and Vijayawada, water supply appears to sit **directly
  with the municipal corporation** (GVMC / VMC) rather than a separate
  state water board — worth flagging explicitly since
  `01_service_data_requirements.md` warns this split must never be
  assumed to transfer across cities/states.
- **Escalation chain:** the clearest, most specific finding of this whole
  pass. GVMC's own 3-level chain (department officer → Zonal
  Commissioner/ADC → MA&UD Public Grievance Cell) and the state PGRS's
  own 3-level chain (Nodal Officer → Public Grievance Officer → HoD/
  Secretary) are consistent with each other and both traced to official
  `.gov.in` domains — a strong direct-fetch-confirmation priority.
- **Quality-A sources found:** `gvmc.gov.in/static_content/Grievances.jsp`,
  `gvmc.gov.in` (general), and `vijayawada.cdma.ap.gov.in/services` — all
  rated A because the domain is unambiguously the ULB's own official
  portal and the page is directly on-topic, even though (per the
  environment constraint) none of their body text was independently
  fetched and read in this pass.
- Nothing in this file should be read as confirming exact SLA numbers —
  no numeric day-count for any AP service in this pass was traced to an
  official `.gov.in`/ULB-domain page; every specific figure that
  surfaced came from third-party aggregator or news sources and was
  deliberately excluded from the `sla`/`response_time`/`resolution_time`
  fields above.
