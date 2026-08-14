# Gujarat — Official Source Inventory

**Cities researched:** Ahmedabad (AMC), Surat (SMC), Vadodara (VMC)
**Method:** WebSearch only. WebFetch (direct page-fetch/verification) was
completely unavailable in this environment for this entire pass (tested
against multiple domains including government sites — all
`EGRESS_BLOCKED`). Every record below is marked `NOT INDEPENDENTLY
FETCHED — confirm before production use` in `verification_status`.

> **Environment note (same caveat as the other two state files in this
> pass):** Everything here relies on WebSearch result metadata (URL,
> title, search-engine-generated summary), not a direct fetch-and-read
> of page content. `source_quality` reflects domain-and-topic
> specificity only, never search-summary detail. Gujarat's three
> researched cities each turned out to have their own distinct,
> department-level official web pages (e.g. Surat's separate Drainage /
> Water Supply / Streetlight department pages, Ahmedabad's dedicated
> Solid Waste Management page and PDFs) — a notably richer official web
> footprint at the department level than was found for most cities in
> Maharashtra, Andhra Pradesh, or Telangana. Despite that, **no specific
> numeric SLA/escalation-day-count was confirmed as read directly from
> any of those official pages' body text** in this pass — every
> "N-level grievance system" or day-count claim found was attributed
> only to third-party summary sites (complainthub.org and similar), so
> per the environment constraint those figures are excluded from the
> `sla`/`escalation_procedure` fields and logged in `notes` only.

---

## Summary table

| State | City | Service | Source | Authority | URL | Format | Data Available | RAG or SQL | Quality |
|---|---|---|---|---|---|---|---|---|---|
| Gujarat | Ahmedabad | All services (Citizen Charter) | Citizen Charter :: Ahmedabad Municipal Corporation | Ahmedabad Municipal Corporation (AMC) | https://ahmedabadcity.gov.in/portal/jsp/Static_pages/pi_ccharter.jsp | HTML | Policy framework, service standards | RAG | A |
| Gujarat | Ahmedabad | Waste & Sanitation | Solid Waste Management — AMC | AMC | https://ahmedabadcity.gov.in/StaticPage/solid_waste_mgmt | HTML | Department overview | RAG | A |
| Gujarat | Ahmedabad | Waste & Sanitation | SWM Dept — Brief Note (PDF) | AMC | https://ahmedabadcity.gov.in/Images/_SWM%20Dept_SWM%20BREIF%20NOTE%20IN%20ENGLISH.pdf | PDF | Department structure/operations | RAG | A |
| Gujarat | Ahmedabad | All services (complaint portal) | AMCCRS — Comprehensive Complaint Redressal System | AMC | https://amccrs.apphost.in/AMCPortal | Web app | Procedure, tracking, SLA colour-coding (mechanism only, no day-counts confirmed) | RAG | B |
| Gujarat | Surat | All services (Citizen Charter) | Citizen Charter | Surat Municipal Corporation (SMC) | https://www.suratmunicipal.gov.in/Downloads/CitizenCharter | HTML | Policy framework, service standards | RAG | A |
| Gujarat | Surat | Waste & Sanitation | Solid Waste Management Home | SMC | https://www.suratmunicipal.gov.in/departments/solidwastemanagementhome | HTML | Department overview, operations | RAG | A |
| Gujarat | Surat | Water & Drainage | Drainage — Introduction | SMC | https://www.suratmunicipal.gov.in/departments/drainageintroduction | HTML | Department overview | RAG | A |
| Gujarat | Surat | Water & Drainage | Drainage — How Do I Get a Connection? | SMC | https://www.suratmunicipal.gov.in/Departments/DrainageHowDoI | HTML | Connection procedure, approval SLA (connection, not complaint) | RAG | A |
| Gujarat | Surat | Water & Drainage | Water Supply (Hydraulic) — Home | SMC | https://www.suratmunicipal.gov.in/departments/hydraulichome | HTML | Department overview | RAG | A |
| Gujarat | Surat | Streetlights | Streetlight — Home | SMC | https://www.suratmunicipal.gov.in/Departments/StreetLightsHome | HTML | Department structure (8 zone offices) | RAG | A |
| Gujarat | Surat | Waste & Sanitation | Solid Waste Management : Surat (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | https://www.data.gov.in/catalog/solid-waste-management-surat | Dataset (catalog) | Source segregation, D2D efficiency, bin/vehicle data | Structured/SQL | C |
| Gujarat | Vadodara | All services (public service portal) | Public Service — VMC | Vadodara Municipal Corporation (VMC) | https://vmc.gov.in/PublicService.aspx | HTML | Channel list | RAG | A |
| Gujarat | Vadodara | Waste & Sanitation | Department — Solid Waste Management Approach | VMC | https://vmc.gov.in/Department_SWM_Approach.aspx | HTML | Department overview, approach | RAG | A |
| Gujarat | Vadodara | Streetlights | Street Light — VMC | VMC | https://vmc.gov.in/StreetLight.aspx | HTML | Department page | RAG | A |
| Gujarat | Vadodara | Waste & Sanitation | Solid Waste Generated/Collected/Processed Data : Vadodara (dataset) | MoHUA Smart Cities Mission, via Smart Cities Mission Data Portal | https://smartcities.data.gov.in/catalog/solid-waste-generated-collected-processed-data-vadodara | Dataset | Waste generation/collection/processing figures | Structured/SQL | C |
| Gujarat | (state-wide) | Water & Drainage (context/jurisdiction) | Gujarat Water Supply & Sewerage Board (GWSSB) — Helpline | Gujarat Water Supply & Sewerage Board | https://gwssb.gujarat.gov.in/helpline | HTML | Contact channel, statewide service scope | RAG | B |
| Gujarat | (state-wide) | All services | Urban Development & Urban Housing Department | Government of Gujarat | https://udd.gujarat.gov.in/ | HTML | Department overview, policy | RAG | B |
| Gujarat | (state-wide) | All services | eNagar / DigiGOV | Government of Gujarat, Urban Development & Urban Housing Dept. | https://enagar.gujarat.gov.in/enagar/login.jsp | Web app | Channel (complaints & grievance module) | RAG | B |
| Gujarat | Ahmedabad (reference, odd domain) | (structured, quality caveat) | Solid Waste Management Basic : Ahmedabad | data.gov.in OGD, mirrored under a karnataka.data.gov.in subdomain (domain oddity — see notes) | https://karnataka.data.gov.in/catalog/solid-waste-management-basic-ahmedabad | Dataset (catalog) | Solid waste basic data | Structured/SQL | C |
| Gujarat | Ahmedabad (reference only) | (reference only, not verified fact source) | AMC — How to Register a Complaint | complainthub.org (third-party) | https://complainthub.org/amc-ahmedabad/ | HTML | Aggregated complaint-channel info, unverifiable claims | reference only | D |
| Gujarat | Vadodara (reference only) | (reference only, not verified fact source) | VMC Helpline: File a Complaint Online | complainthub.org (third-party) | https://complainthub.org/vmc-vadodara-help/ | HTML | 4-level grievance claim, unverified against an official page in this pass | reference only | D |

---

## Full records

### Record: Gujarat-Ahmedabad-Waste-SolidWasteManagement
```
service_id: gj-ahmedabad-waste-solid-waste-management
service_name: Waste & Public Sanitation
sub_service: Solid waste management — collection, transport, processing
problem_type: garbage_collection

state: Gujarat
district: Ahmedabad
city: Ahmedabad
municipality: Ahmedabad Municipal Corporation (AMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Solid Waste Management (SWM) Department, AMC
authority: Ahmedabad Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: AMC publishes a dedicated Solid Waste Management department page and multiple supporting documents (a departmental brief note, an SWM presentation, and an SWM profile document), all hosted on AMC's own official domain (ahmedabadcity.gov.in).
procedure: General civic complaints (including waste-related) are filed via the toll-free citizen helpline (155303 / 1800-233-2330), the AMC mobile app, or the AMCCRS (Comprehensive Complaint Redressal System) online portal.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Toll-free 155303 / 1800-233-2330, AMC mobile app (CCRS Citizen / AMC CCRS on Google Play & App Store), AMCCRS online portal (amccrs.apphost.in/AMCPortal), written application at department reception/PR counter
contact_information: Toll-free 155303 / 1800-233-2330

escalation_procedure: If not satisfied with the response of officers, or if issues are not redressed within the timeline set by AMC's citizen charter, citizens may lodge a grievance with the Public Grievance Cell, AMC, or write to the zonal commissioner or the Municipal Commissioner.
escalation_authority: Public Grievance Cell, AMC → Zonal Commissioner / Municipal Commissioner, AMC

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Solid Waste Management — AMC
source_url: https://ahmedabadcity.gov.in/StaticPage/solid_waste_mgmt
source_type: govt_portal
source_organization: Ahmedabad Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: AMC has an unusually rich set of official SWM documents for this pass — a static department page plus 3 distinct PDFs (brief note, presentation, profile), all on ahmedabadcity.gov.in. None of their body text was read directly in this pass (existence/URLs only confirmed via search), but this is a strong direct-fetch priority given the volume of dedicated material. The CCRS system is reported (via app-store descriptions, not an official page) to use "colour-coded SLA" and "automatic multi-level escalation" — the mechanism's existence is plausible given AMC's own citizen-charter-based escalation language, but no specific day-count was confirmed on an official page and none is entered above.
```

### Record: Gujarat-Ahmedabad-Water-Drainage
```
service_id: gj-ahmedabad-water-drainage
service_name: Water & Drainage
sub_service: Water supply (inadequate supply/low pressure, main pipeline leakage, water-timing issues), waterlogging
problem_type: no_low_water_supply

state: Gujarat
district: Ahmedabad
city: Ahmedabad
municipality: Ahmedabad Municipal Corporation (AMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (AMC is confirmed as directly responsible per its own CCRS complaint categories — no separate board found for Ahmedabad, unlike Hyderabad's HMWSSB split — but the specific water-supply department name was not confirmed on an official page in this pass)
authority: Ahmedabad Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: AMC's CCRS complaint system accepts water-supply complaints covering inadequate supply/low inflow pressure, main pipeline leakage, and problems with water-supply timing.
procedure: File via the AMCCRS portal/app, toll-free 155303, or the Danapith Control Room (079-25353858 / 079-25353717).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: AMCCRS portal/app, toll-free 155303 / 1800-233-2330, Danapith Control Room 079-25353858 / 079-25353717
contact_information: Toll-free 155303 / Control Room 079-25353858, 079-25353717

escalation_procedure: Same citizen-charter-based escalation as other AMC services: Public Grievance Cell, AMC → zonal commissioner / Municipal Commissioner.
escalation_authority: Public Grievance Cell, AMC → Zonal Commissioner / Municipal Commissioner, AMC

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen Charter :: Ahmedabad Municipal Corporation
source_url: https://ahmedabadcity.gov.in/portal/jsp/Static_pages/pi_ccharter.jsp
source_type: citizen_charter
source_organization: Ahmedabad Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: No separate water board jurisdiction found for Ahmedabad city proper in this pass — AMC appears directly responsible, similar to the pattern found for Visakhapatnam/Vijayawada (see andhra_pradesh.md) and unlike Hyderabad's HMWSSB split (see telangana.md). The statewide Gujarat Water Supply & Sewerage Board (GWSSB) exists (see the state-wide GWSSB record below) but its own materials describe statewide/regional coverage, not an Ahmedabad-specific role — worth direct-fetch confirmation that GWSSB truly excludes AMC's own service area.
```

### Record: Gujarat-Ahmedabad-Roads-Potholes
```
service_id: gj-ahmedabad-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting, road maintenance
problem_type: potholes

state: Gujarat
district: Ahmedabad
city: Ahmedabad
municipality: Ahmedabad Municipal Corporation (AMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Ahmedabad Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Road/pothole complaints are handled through AMC's general CCRS complaint system alongside other civic-service complaint categories.
procedure: File via the AMCCRS portal/app or toll-free 155303 / 1800-233-2330.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: AMCCRS portal/app, toll-free 155303 / 1800-233-2330
contact_information: Toll-free 155303 / 1800-233-2330

escalation_procedure: Same citizen-charter-based escalation as other AMC services.
escalation_authority: Public Grievance Cell, AMC → Zonal Commissioner / Municipal Commissioner, AMC

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen Charter :: Ahmedabad Municipal Corporation
source_url: https://ahmedabadcity.gov.in/portal/jsp/Static_pages/pi_ccharter.jsp
source_type: citizen_charter
source_organization: Ahmedabad Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: No dedicated pothole-specific department page or app (comparable to Pune's Road Mitra or GHMC's Ward-Level Citizen's Charter tier) was found for AMC specifically in this pass — roads appear folded into the general CCRS system rather than given their own dedicated channel.
```

### Record: Gujarat-Ahmedabad-Streetlight
```
service_id: gj-ahmedabad-streetlight
service_name: Streetlights
sub_service: Non-functioning streetlight
problem_type: streetlight_not_working

state: Gujarat
district: Ahmedabad
city: Ahmedabad
municipality: Ahmedabad Municipal Corporation (AMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Ahmedabad Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Streetlight complaints are handled through AMC's general CCRS complaint system alongside other civic-service complaint categories (water, drainage, streetlights, garbage, sanitation, road repair, manholes are explicitly grouped together in AMC's own complaint-category description).
procedure: File via the AMCCRS portal/app or toll-free 155303 / 1800-233-2330.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: AMCCRS portal/app, toll-free 155303 / 1800-233-2330
contact_information: Toll-free 155303 / 1800-233-2330

escalation_procedure: Same citizen-charter-based escalation as other AMC services.
escalation_authority: Public Grievance Cell, AMC → Zonal Commissioner / Municipal Commissioner, AMC

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen Charter :: Ahmedabad Municipal Corporation
source_url: https://ahmedabadcity.gov.in/portal/jsp/Static_pages/pi_ccharter.jsp
source_type: citizen_charter
source_organization: Ahmedabad Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Thinnest of AMC's 4 category records, consistent with the pattern found across all 3 states in this research pass for streetlights.
```

### Record: Gujarat-Surat-Waste-SolidWasteManagement
```
service_id: gj-surat-waste-solid-waste-management
service_name: Waste & Public Sanitation
sub_service: Solid waste management — storage, source segregation, primary collection, day-to-day cleaning
problem_type: garbage_collection

state: Gujarat
district: Surat
city: Surat
municipality: Surat Municipal Corporation (SMC)
zone: SMC operates through 8 zone offices for at least some decentralized functions (confirmed for Streetlight — see that record; likely also applies more broadly, but not confirmed specifically for SWM in this pass)
ward: NOT FOUND IN OFFICIAL SOURCE

department: Solid Waste Management Department, SMC
authority: Surat Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: SMC's Solid Waste Management department page describes its focus on devising systems for waste storage, source segregation of recyclable waste, improving primary collection, and running efficient day-to-day cleaning systems. A companion "Approaches" page covers transportation and recycling/processing of recyclable waste from a Material Recovery Facility (MRF) under the Swachh Bharat Mission, and a "Key Aspects" page covers "Micro Planning" for sanitation, collection, transportation, and final disposal. Surat was awarded "Best Big City in Solid Waste Management Practices" in Swachh Survekshan-2019 (per search-summary description of SMC's own page content).
procedure: Register complaints via SMC's website, mobile app, helpline, or WhatsApp to SMC nodal officers; a Complaint Ticket is issued for tracking. Complaints are auto-assigned to the concerned officer based on complaint category, complaint code, and ward.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: SMC website/app, toll-free helpline, control-room helpline numbers (Ward/Zonal offices), WhatsApp to SMC nodal officers, integrated online complaint portal (office.suratmunicipal.org/nwcomplain/Login.aspx)
contact_information: Main office +91-261-2423750 to 2423756, Control Room +91-261-2423751-59

escalation_procedure: If complaints are not resolved, or the citizen is not satisfied with the final resolution/order of the designated nodal officer, the citizen may escalate to the Public Grievance Cell, SMC (which consists of deputy commissioners of the respective department and the Commissioner of the Municipal Corporation).
escalation_authority: Designated nodal officer (ward/zone) → Public Grievance Cell, SMC (Deputy Commissioners + Municipal Commissioner)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Solid Waste Management Home
source_url: https://www.suratmunicipal.gov.in/departments/solidwastemanagementhome
source_type: govt_portal
source_organization: Surat Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: SMC's escalation chain (nodal officer → Public Grievance Cell of deputy commissioners + Commissioner) is the most specific and clearly-named escalation structure found for Gujarat in this pass, and appears consistently across multiple SMC service categories, increasing confidence — still worth direct-fetch confirmation since it was pieced together from search summaries, not read as a single official document.
```

### Record: Gujarat-Surat-Water-Drainage
```
service_id: gj-surat-water-drainage
service_name: Water & Drainage
sub_service: Water supply distribution, drainage connection, manhole/desilting maintenance
problem_type: sewage_drainage_problems

state: Gujarat
district: Surat
city: Surat
municipality: Surat Municipal Corporation (SMC)
zone: Zonal Officers approve drainage-connection plans (per SMC's own Drainage department page — see below)
ward: NOT FOUND IN OFFICIAL SOURCE

department: Drainage Department and Hydraulic (Water Supply) Department — two distinct SMC departments, each with its own official page
authority: Surat Municipal Corporation
officer_designation: Zonal Officer (named as the approving authority for drainage-connection plans, per SMC's own Drainage department page)

description: SMC operates separate Drainage and Water Supply (Hydraulic) departments, each with dedicated official pages. The Drainage department's stated goal includes contracting private agencies for desilting of manholes and drainage lines across the city. The Water Supply (Hydraulic) department's stated goal is that every citizen receives safe, reliable drinking water on a continuous basis via the distribution network.
procedure: For a NEW drainage connection: the Zonal Officer approves the drainage plan and grants connection permission within 15 days (per SMC's own "How Do I Get a Drainage Connection?" page) — note this is a connection-approval timeline, NOT a complaint-resolution SLA, and must not be conflated with one. For COMPLAINTS (leaks, blockages, no-supply), citizens use SMC's general channels: website, app, helpline, WhatsApp.
required_information: NOT FOUND IN OFFICIAL SOURCE (for complaints); for new drainage connections, a drainage plan is required for Zonal Officer approval
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND for complaint resolution. A 15-day timeline IS explicitly published on an official SMC page, but only for Zonal Officer approval of a NEW drainage connection application — not for resolving a leak/blockage/no-supply complaint. Recording this distinction explicitly so it is not mistakenly reused as a complaint-resolution SLA.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: SMC website/app, toll-free helpline, ward/zonal control-room helplines, WhatsApp to nodal officers
contact_information: Main office +91-261-2423750 to 2423756, Control Room +91-261-2423751-59

escalation_procedure: Same general SMC escalation as other categories: nodal officer → Public Grievance Cell, SMC.
escalation_authority: Designated nodal officer (ward/zone) → Public Grievance Cell, SMC (Deputy Commissioners + Municipal Commissioner)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: How Do I Get a Drainage Connection?
source_url: https://www.suratmunicipal.gov.in/Departments/DrainageHowDoI
source_type: govt_portal
source_organization: Surat Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: This is the only genuinely confirmed, official-domain-published numeric timeline (15 days) found anywhere across all 3 states in this research pass — but it applies to a NEW CONNECTION APPROVAL, not a citizen complaint SLA, so it must not be miscoded as a complaint-resolution figure in any downstream compilation step. No separate water board was found serving Surat (SMC runs its own Hydraulic/Water Supply department directly), similar to Ahmedabad and unlike Hyderabad's HMWSSB split.
```

### Record: Gujarat-Surat-Roads-Potholes
```
service_id: gj-surat-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting, footpath/traffic-light maintenance, new road construction requests
problem_type: potholes

state: Gujarat
district: Surat
city: Surat
municipality: Surat Municipal Corporation (SMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (a dedicated Roads/Public Works department page was not located distinctly in this pass, unlike SMC's Drainage/Hydraulic/Streetlight departments which each have their own page)
authority: Surat Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: SMC's general complaint categories explicitly include potholes, footpaths, traffic lights, and requests for new road construction, alongside streetlight problems.
procedure: File via SMC's website, mobile app, helpline, or WhatsApp; complaints auto-assign to the concerned officer by category/code/ward and generate a Complaint Ticket.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: SMC website/app, toll-free helpline, control-room helplines (zone offices), WhatsApp, integrated online complaint portal
contact_information: Main office +91-261-2423750 to 2423756, Control Room +91-261-2423751-59

escalation_procedure: Same general SMC escalation as other categories.
escalation_authority: Designated nodal officer (ward/zone) → Public Grievance Cell, SMC (Deputy Commissioners + Municipal Commissioner)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Zone Officials
source_url: https://www.suratmunicipal.gov.in/home/zoneofficials
source_type: govt_portal
source_organization: Surat Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Unlike Drainage/Water Supply/Streetlight, roads did not surface a dedicated SMC department page distinct from the general zone/complaint structure in this pass — worth a targeted follow-up search for a Roads/Public Works-specific SMC page.
```

### Record: Gujarat-Surat-Streetlight
```
service_id: gj-surat-streetlight
service_name: Streetlights
sub_service: Streetlight installation, operation & maintenance
problem_type: streetlight_not_working

state: Gujarat
district: Surat
city: Surat
municipality: Surat Municipal Corporation (SMC)
zone: Streetlight services are provided through partial decentralized management via 8 zone offices (per SMC's own Streetlight department page — the most specific organizational detail found for this category anywhere in this 3-state pass)
ward: NOT FOUND IN OFFICIAL SOURCE

department: Streetlight Department, SMC
authority: Surat Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: SMC's Streetlight department page states that streetlight services are delivered through partial decentralized management across 8 zone offices, covering installation, operation, and maintenance of all streetlights on roads within SMC limits.
procedure: File via SMC's website, mobile app, helpline, or WhatsApp; complaints auto-assign to the concerned officer by category/code/ward.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: SMC website/app, toll-free helpline, zone-office control-room helplines, WhatsApp
contact_information: Main office +91-261-2423750 to 2423756, Control Room +91-261-2423751-59

escalation_procedure: Same general SMC escalation as other categories.
escalation_authority: Designated nodal officer (zone office) → Public Grievance Cell, SMC (Deputy Commissioners + Municipal Commissioner)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Streetlight — Home
source_url: https://www.suratmunicipal.gov.in/Departments/StreetLightsHome
source_type: govt_portal
source_organization: Surat Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Notably, this is the ONLY streetlight record across all 3 states in this pass with a confirmed dedicated department page AND a specific organizational detail (8 zone offices, partial decentralized management) attributable to an official municipal domain — contrast with the "thinnest category" pattern seen everywhere else.
```

### Record: Gujarat-Vadodara-Waste-SolidWasteManagement
```
service_id: gj-vadodara-waste-solid-waste-management
service_name: Waste & Public Sanitation
sub_service: Solid waste management — collection and processing approach
problem_type: garbage_collection

state: Gujarat
district: Vadodara
city: Vadodara
municipality: Vadodara Municipal Corporation (VMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: Door-to-door collection is reported to be operating across all wards to varying degrees (per search-summary description of VMC's own tender/department material — see notes)
department: Solid Waste Management Department, VMC
authority: Vadodara Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: VMC's official Solid Waste Management department page describes VMC's approach to solid waste handling. A VMC tender document (also on vmc.gov.in) references the scale of the operation: approximately 550 tons of waste generated per day, of which around 484 tons per day is handled, with door-to-door collection reported as started in 45% of the area spread across all wards (figures as reported in search-result summaries of VMC's own material, not independently confirmed by direct read).
procedure: Register complaints via VMC's online complaint system (auto-assigned by category and ward), toll-free helpline, WhatsApp, or the eNagar Gujarat / e-Nagarsewa state portal.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: VMC online complaint portal, toll-free 1800-233-0265, phone +91-265-2433116 / +91-265-2433118, WhatsApp +91-9913166666, eNagar Gujarat / e-Nagarsewa
contact_information: Toll-free 1800-233-0265 / WhatsApp +91-9913166666

escalation_procedure: ESCALATION INFORMATION NOT FOUND on an official page in this pass. Third-party summaries (complainthub.org) describe a 4-level VMC grievance process, with Level 4 reaching the State Public Grievance Authority, Urban Development Department (Govt. of Gujarat) — but since this was not confirmed as read from an official vmc.gov.in page, the sentinel value is used here per the environment constraint; see notes.
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Department — Solid Waste Management Approach
source_url: https://vmc.gov.in/Department_SWM_Approach.aspx
source_type: govt_portal
source_organization: Vadodara Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: The claimed 4-level VMC grievance escalation (with Level 4 = State Public Grievance Authority, Urban Development Dept.) is a plausible, specific, and reasonably credible claim — it echoes Gujarat's real state-level Samadhan/Grievance Appellate Authority mechanism (see the state-wide UDD record below) — but per the strict environment rule it was found ONLY via complainthub.org-style secondary summaries in this pass, not read directly from an official vmc.gov.in page, so it is deliberately excluded from escalation_procedure/escalation_authority above and logged here as an unverified, high-priority direct-fetch target instead.
```

### Record: Gujarat-Vadodara-Water-Drainage
```
service_id: gj-vadodara-water-drainage
service_name: Water & Drainage
sub_service: Water supply, drainage, manhole-related complaints
problem_type: no_low_water_supply

state: Gujarat
district: Vadodara
city: Vadodara
municipality: Vadodara Municipal Corporation (VMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (no VMC-specific Water Supply/Drainage department page distinct from the general Public Service page was located in this pass, unlike Surat's separate Hydraulic and Drainage pages)
authority: Vadodara Municipal Corporation (the statewide Gujarat Water Supply & Sewerage Board, GWSSB, exists but its own materials describe statewide/regional coverage — no evidence surfaced in this pass that GWSSB, rather than VMC itself, handles complaints within Vadodara city limits; needs direct confirmation)
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: VMC's general online complaint system covers water, drainage, streetlights, garbage, sanitation, road repair, and manhole-related issues, auto-assigned by category and ward.
procedure: Register via VMC's online complaint portal, toll-free helpline, WhatsApp, or eNagar Gujarat / e-Nagarsewa.
required_information: Full name and current residential address, nature of the complaint, department involved (if known), and Area/Ward/Zone location details (per a third-party summary describing VMC's complaint-form requirements — treated cautiously as it wasn't confirmed on an official vmc.gov.in page directly)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: VMC online complaint portal, toll-free 1800-233-0265, phone +91-265-2433116 / +91-265-2433118, WhatsApp +91-9913166666, eNagar Gujarat / e-Nagarsewa
contact_information: Toll-free 1800-233-0265 / WhatsApp +91-9913166666

escalation_procedure: ESCALATION INFORMATION NOT FOUND on an official page in this pass (see notes for the unverified third-party 4-level claim, same as the Waste record above).
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Public Service — VMC
source_url: https://vmc.gov.in/PublicService.aspx
source_type: govt_portal
source_organization: Vadodara Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: The water-supply-vs-GWSSB jurisdiction question is unresolved for Vadodara in this pass, same open question as for Ahmedabad — worth a direct-fetch follow-up specifically checking whether GWSSB's own coverage-area page lists Vadodara city as in- or out-of-scope.
```

### Record: Gujarat-Vadodara-Roads-Potholes
```
service_id: gj-vadodara-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting, road repair
problem_type: potholes

state: Gujarat
district: Vadodara
city: Vadodara
municipality: Vadodara Municipal Corporation (VMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Vadodara Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: VMC's general online complaint system covers road repair among water, drainage, streetlights, garbage, sanitation, and manhole-related issues.
procedure: Register via VMC's online complaint portal, toll-free helpline, WhatsApp, or eNagar Gujarat / e-Nagarsewa.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: VMC online complaint portal, toll-free 1800-233-0265, phone +91-265-2433116 / +91-265-2433118, WhatsApp +91-9913166666
contact_information: Toll-free 1800-233-0265 / WhatsApp +91-9913166666

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Public Service — VMC
source_url: https://vmc.gov.in/PublicService.aspx
source_type: govt_portal
source_organization: Vadodara Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: No dedicated Roads/Public Works department page distinct from the general Public Service page was located for VMC in this pass, unlike its SWM and Streetlight departments which each have their own page.
```

### Record: Gujarat-Vadodara-Streetlight
```
service_id: gj-vadodara-streetlight
service_name: Streetlights
sub_service: Non-functioning streetlight, damaged pole
problem_type: streetlight_not_working

state: Gujarat
district: Vadodara
city: Vadodara
municipality: Vadodara Municipal Corporation (VMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE (complaint form is reported to require Area/Ward/Zone detail per a third-party summary — see the Water & Drainage record's notes on required_information)

department: Street Light Department, VMC
authority: Vadodara Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: VMC has a dedicated Street Light department page on its official domain. Its complaint-registration system auto-assigns streetlight complaints based on category and ward.
procedure: Register via VMC's online complaint portal, toll-free helpline 1800-233-0265, phone +91-265-2433116 / +91-265-2433118, or WhatsApp +91-9913166666.
required_information: NOT FOUND IN OFFICIAL SOURCE (specific to this category)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: VMC online complaint portal, toll-free 1800-233-0265, phone +91-265-2433116 / +91-265-2433118, WhatsApp +91-9913166666
contact_information: Toll-free 1800-233-0265 / WhatsApp +91-9913166666

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Street Light — VMC
source_url: https://vmc.gov.in/StreetLight.aspx
source_type: govt_portal
source_organization: Vadodara Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Like Surat, Vadodara has a dedicated official Street Light department page — a notable exception to the "thinnest category" pattern seen elsewhere in this research pass, though (unlike Surat's page) no organizational detail (e.g. zone-office count) was surfaced for it specifically.
```

### Record: Gujarat-StateWide-WaterDrainage-GWSSB
```
service_id: gj-statewide-water-gwssb
service_name: Water & Drainage
sub_service: Statewide water supply and sewerage — jurisdiction context
problem_type: no_low_water_supply

state: Gujarat
district: NOT APPLICABLE (state-wide)
city: NOT APPLICABLE (statewide/regional; the 3 researched cities — Ahmedabad, Surat, Vadodara — appear to run their own municipal water/drainage departments rather than being served by GWSSB, but this is not fully confirmed — see notes)
municipality: NOT APPLICABLE
zone: NOT APPLICABLE
ward: NOT APPLICABLE

department: NOT APPLICABLE (GWSSB is itself the department/board)
authority: Gujarat Water Supply & Sewerage Board (GWSSB)
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: GWSSB was established under Gujarat Act No. 18 of 1979 for the development and regulation of water supply and sewerage services across the state, per GWSSB's own official description. It states it serves all regions/districts of Gujarat for both urban and rural drinking water supply and sewerage, though the specific jurisdictional boundary relative to the 3 major municipal corporations researched (which each run their own water/drainage departments per the city-level records above) was not resolved in this pass.
procedure: Register a water/sewerage complaint via GWSSB's toll-free helpline, complaint number, email, or online grievance form.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Toll-free water helpline 1916, complaint number +91-79-23220859, email gwssbhocontrol@gmail.com / deecontrol-gwssb@gujarat.gov.in, online grievance form
contact_information: Toll-free 1916 / +91-79-23220859

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Helpline | Gujarat Water Supply and Sewerage Board
source_url: https://gwssb.gujarat.gov.in/helpline
source_type: govt_portal
source_organization: Gujarat Water Supply & Sewerage Board

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: state
notes: Logged primarily for jurisdiction-split context, per 01_service_data_requirements.md's instruction to capture the water-authority split explicitly per city rather than assume it. In this pass, none of the 3 researched Gujarat cities showed evidence of GWSSB (rather than their own municipal corporation) handling in-city water/drainage complaints — each of AMC/SMC/VMC appears to run its own water/drainage department directly. GWSSB most likely serves smaller towns/rural areas outside these 3 corporations' limits, but this was not independently confirmed by directly reading GWSSB's own coverage-area documentation in this pass.
```

### Record: Gujarat-StateWide-AllServices-UDD
```
service_id: gj-statewide-all-udd
service_name: (cross-cutting — applies to all 4 categories, all Gujarat ULBs)
sub_service: Urban Development & Urban Housing Department policy framework, eNagar portal, Samadhan escalation
problem_type: multiple

state: Gujarat
district: NOT APPLICABLE (state-wide)
city: NOT APPLICABLE (applies to all Gujarat Urban Local Bodies, including AMC, SMC, VMC)
municipality: All Gujarat Urban Local Bodies
zone: NOT APPLICABLE
ward: NOT APPLICABLE

department: Urban Development & Urban Housing Department (UDD)
authority: Government of Gujarat
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Citizen's Charters were introduced in Gujarat in 1998 (voluntary in character, detailing services and delivery time periods), per general policy-history search summaries. The Jan Seva Kendra, launched in 2004, provides an integrated approach to citizen-centric administration. UDD's eNagar Portal (also called DigiGOV/eNagar) provides online citizen-centric services to Urban Local Bodies statewide, including Shops & Establishment registration, marriage registration, building permission, professional tax, hall booking, property tax, estate management, fire & emergency, Complaints and Grievance, and Water & Drainage — all with online payment gateway. Gujarat also runs a 24x7 statewide complaint/grievance call centre (155303, per general policy-summary description — the same number independently found as AMC's own toll-free helpline, suggesting 155303 may be a shared statewide/AMC number rather than AMC-exclusive; not fully disambiguated in this pass).
procedure: Register and track complaints (water, drainage, streetlights, garbage, sanitation, road repair, manholes) via eNagar Gujarat / e-Nagarsewa (enagar.gujarat.gov.in).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: eNagar Gujarat / e-Nagarsewa (enagar.gujarat.gov.in), e-Nagar mobile app, 24x7 call centre 155303
contact_information: 155303 (statewide citizen complaint & grievance call centre, per general UDD policy description)

escalation_procedure: For unresolved complaints, citizens may submit to the Grievance Appellate Authority of the Urban Local Administration Department through Samadhan, the Gujarat Government's Public Grievance System.
escalation_authority: eNagar/ULB-level nodal officer → Grievance Appellate Authority, Urban Local Administration Department (via Samadhan, Govt. of Gujarat)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Urban Development & Urban Housing Development
source_url: https://udd.gujarat.gov.in/
source_type: govt_portal
source_organization: Urban Development & Urban Housing Department, Government of Gujarat

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: state
notes: The Samadhan/Grievance Appellate Authority escalation destination is a specific, credible-sounding state-level appellate mechanism (and matches the "Level 4 = State Public Grievance Authority, Urban Development Department" claim found separately for Vadodara — see that record's notes), increasing cross-source confidence — but it was pieced together from a training-resource PDF (pas.org.in) describing "Improvement in Public Grievance Redressal System - Gujarat ULBs" rather than read directly from an official udd.gujarat.gov.in page, so treat as a strong lead, not a confirmed fact, until direct-fetched.
```

---

## Coverage notes for Gujarat

- **Best-covered city:** Surat (SMC) — uniquely among all 9 cities
  researched across the 3 states in this pass, Surat has clearly
  separate, dedicated official department pages for Waste (2 pages),
  Drainage (2 pages), Water Supply/Hydraulic, and Streetlight, each
  confirmed on `suratmunicipal.gov.in`. It is also the only city in this
  entire 3-state pass with a genuinely official, numeric, directly-
  confirmed timeline (the 15-day drainage-connection-approval SLA) —
  though that figure is a connection-approval timeline, not a
  complaint-resolution SLA, and is flagged as such to avoid downstream
  miscoding.
- **Best-covered service:** Streetlights, unusually — both Surat and
  Vadodara have dedicated official Streetlight department pages, which
  is the opposite of the pattern found in every other state in this
  research pass (where streetlights was consistently the *weakest*-
  documented category). Waste & Sanitation remains strong too (all 3
  cities have dedicated SWM pages/PDFs plus data.gov.in datasets).
- **Weakest-covered service:** Roads & Potholes — none of the 3 Gujarat
  cities had a dedicated Roads/Public Works department page distinct
  from their general complaint-portal listing, which is a reversal of
  the more typical pattern (Roads was often better-documented than
  Streetlights elsewhere) — worth a targeted follow-up.
- **Water vs. drainage jurisdiction split:** Unresolved for all 3 cities
  in this pass regarding GWSSB (the statewide water board) vs. the
  municipal corporations' own water departments. The pattern found —
  AMC, SMC, and VMC each running their own dedicated water/drainage
  department directly — suggests GWSSB's role is likely limited to
  smaller towns/rural areas outside these 3 corporations, consistent
  with the AP pattern (GVMC/VMC handle water directly) and in contrast
  with Telangana's Hyderabad (where a genuinely separate board, HMWSSB,
  holds jurisdiction). This should still be confirmed by a direct fetch
  of GWSSB's own coverage-area documentation before being treated as
  settled.
- **Escalation chain:** Gujarat's apparent structure — ULB-level nodal
  officer/Public Grievance Cell → State Grievance Appellate Authority
  (Urban Local Administration Department) via the state's Samadhan
  system — was corroborated across two independent leads (a Vadodara-
  specific 4-level claim and a general UDD policy-training document),
  which is encouraging, but **neither lead traced to a directly-read
  official-domain page body** in this pass, so both remain in `notes`
  only, not in the `escalation_procedure` field, per the environment
  constraint.
- **Odd-domain finding:** the Ahmedabad solid-waste dataset surfaced
  under a `karnataka.data.gov.in` subdomain rather than
  `www.data.gov.in` or `ahmedabad.data.gov.in` — logged with a caveat in
  the summary table; this looks like a cross-state-mirroring quirk of
  the OGD platform's catalog infrastructure rather than a meaningful
  fact, but was left unresolved rather than silently corrected.
- As with the other two states in this pass, no specific SLA day-count
  for citizen complaint resolution anywhere in this file was confirmed
  as read directly from an official-domain page body text (the one
  exception — Surat's 15-day drainage-CONNECTION-approval timeline — is
  explicitly not a complaint SLA). Every other numeric or structural
  claim (4-level VMC escalation, CCRS colour-coded SLA, Samadhan
  appellate chain) that surfaced in this pass came from third-party or
  training-material summaries and was deliberately excluded from the
  `sla`/`escalation_procedure` fields, logged only in `notes`.
