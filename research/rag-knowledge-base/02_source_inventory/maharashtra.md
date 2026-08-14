# Maharashtra — Official Source Inventory (Primary Pilot)

**Cities researched:** Mumbai (BMC), Pune (PMC), Nagpur (NMC)
**Method:** WebSearch only — WebFetch (direct page-fetch/verification) was
unavailable in this environment for the entire duration of this research
pass (see note below). Every record is marked `NOT INDEPENDENTLY FETCHED`
in `verification_status` as a result. `source_quality` still reflects how
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
> below.

---

## Summary table

| State | City | Service | Source | Authority | URL | Format | Data Available | RAG or SQL | Quality |
|---|---|---|---|---|---|---|---|---|---|
| Maharashtra | Pune | All services (grievance mechanism) | GRIEVANCE REDRESSAL MECHANISM | Pune Municipal Corporation | https://www.pmc.gov.in/en/grievance-redressal | HTML | Procedure, channels | RAG | B |
| Maharashtra | Pune | All services (complaint portal) | तक्रार :मुख्यपृष्ठ (Complaint Portal) | Pune Municipal Corporation | https://complaint.pmc.gov.in/ | Web app | Procedure, tracking | RAG | B |
| Maharashtra | Pune | Roads & Potholes | PMC Apps Store — PMC Road Mitra | Pune Municipal Corporation | https://www.pmc.gov.in/en/b/pmc-apps-store | HTML | Channel (app) | RAG | B |
| Maharashtra | Pune | All services | Check Complaint Status for PMC | National Government Services Portal (Govt. of India) | https://services.india.gov.in/service/detail/check-complaint-status-for-pune-municipal-corporation-maharashtra | HTML | Channel, status-check | RAG | B |
| Maharashtra | Mumbai | All services | Central Complaint Registration System | BMC / Disaster Management, MCGM | https://dm.mcgm.gov.in/central-complaint-registration-system | HTML | Procedure | RAG | B |
| Maharashtra | Mumbai | All services | Lodging Civic Complaints / Complaint Registration | BMC (MCGM) | https://portal.mcgm.gov.in/irj/portal/anonymous/qlcomplaintreg?guest_user=english | Web form | Procedure, channel | RAG | B |
| Maharashtra | Mumbai | Waste & Sanitation | Solid Waste Management dept RTI Manual (Sec 4(1)(b)) | BMC — Chief Engineer, Solid Waste Management | https://www.mcgm.gov.in/irj/go/km/docs/documents/MCGM%20Department%20List/ChiefEngineerSolidWasteManagement/RTI%20Manuals/CESWM_RTI_E02.pdf | PDF | Department info, responsibility | RAG | A |
| Maharashtra | Mumbai | Waste & Sanitation | Solid Waste Management (portal section) | BMC (MCGM) | https://portal.mcgm.gov.in/irj/portal/anonymous/qltendersswm_new | HTML | Service info | RAG | B |
| Maharashtra | Mumbai | All services (ward-level) | WardC — MyBMC | BMC (MCGM) | https://portal.mcgm.gov.in/irj/portal/anonymous/qlwardc?guest_user=english | HTML | Jurisdiction (ward) | RAG | B |
| Maharashtra | Nagpur | All services | Grievance Redressal System — NMC | Nagpur Municipal Corporation | https://www.nmcnagpur.gov.in/grievance/ | HTML | Procedure, escalation | RAG | B |
| Maharashtra | Nagpur | All services | New Complaint Registration | Nagpur Municipal Corporation | https://nmcnagpur.gov.in/grievance/complaint_form.php | Web form | Channel | RAG | B |
| Maharashtra | (state-wide) | All services | Grievance Redressal System (IGR) | Government of Maharashtra | https://grievanceigr.maharashtra.gov.in/home/contactus | HTML | Escalation (state-level appellate channel) | RAG | B |
| Maharashtra | Pune | Waste & Sanitation | Solid Waste Management: Pune (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | https://www.data.gov.in/catalog/solid-waste-managementpune | Dataset (catalog) | Collection vehicles, D2D efficiency, bin placement | Structured/SQL | C |
| Maharashtra | Thane | Waste & Sanitation | Solid Waste Management Efficiency in Thane : 2021 | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | https://www.data.gov.in/resource/solid-waste-management-efficiency-thane-2021 | Dataset | Source segregation, D2D efficiency, bin placement, vehicle capacity | Structured/SQL | C |
| Maharashtra | (national, indexes all states) | Waste & Sanitation | D19-SolidWasteDisposal | data.gov.in OGD Platform India | https://www.data.gov.in/resource/d19-solidwastedisposal | Dataset | Solid waste disposal (large, not location-filtered in search result) | Structured/SQL | C |
| Maharashtra | Mumbai | (reference only, not verified fact source) | Praja Foundation — Status of Civic Issues in Mumbai 2023 | Praja Foundation (NGO, not government) | https://www.praja.org/praja_docs/praja_downloads/Report%20of%20Status%20of%20Civic%20Issues%20in%20Mumbai%202023.pdf | PDF | Complaint-resolution analysis referencing BMC's Citizen Charter SLAs | reference only | D |
| Maharashtra | Pune | (reference only, not verified fact source) | complainthub.org — PMC complaint guide | Third-party (not government) | https://complainthub.org/pmc-pune/ | HTML | Aggregated complaint-channel info, unverifiable SLA claims | reference only | D |

---

## Full records

### Record: Maharashtra-Pune-Waste-GarbageCollection
```
service_id: mh-pune-waste-garbage-collection
service_name: Waste & Public Sanitation
sub_service: Garbage collection / missed collection
problem_type: garbage_collection

state: Maharashtra
district: Pune
city: Pune
municipality: Pune Municipal Corporation (PMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE (ward-level routing exists per search results but no specific ward document surfaced)

department: PMC Solid Waste Management department (inferred from complaint-category list; exact department name not confirmed on an official page)
authority: Pune Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: PMC's Complaint Management System accepts garbage-disposal complaints alongside other civic issues.
procedure: File via PMC's online grievance portal (complaint.pmc.gov.in), toll-free number, WhatsApp, email, or Facebook page, per pmc.gov.in's grievance-redressal page.
required_information: Grievance details, area details, name; photo of the issue where relevant (per PMC's grievance page).
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — a numeric garbage-collection SLA (reported elsewhere as "3-7 days") appeared only in third-party aggregator search results (complainthub.org / pmc.opinify.co.in), not confirmed on an official pmc.gov.in page in this pass. Do not treat as verified.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online portal (complaint.pmc.gov.in), toll-free 18001030222, WhatsApp 9689900002, email feedback@punecorporation.org, Facebook (PMCFMC)
contact_information: Toll-free 18001030222 / WhatsApp 9689900002 / feedback@punecorporation.org

escalation_procedure: ESCALATION INFORMATION NOT FOUND (not surfaced for Pune specifically in this pass)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: GRIEVANCE REDRESSAL MECHANISM
source_url: https://www.pmc.gov.in/en/grievance-redressal
source_type: govt_portal
source_organization: Pune Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Multiple complaint channels confirmed to exist and to be genuinely official (pmc.gov.in domain); exact per-category SLA and escalation chain need direct-fetch confirmation.
```

### Record: Maharashtra-Pune-Roads-Potholes
```
service_id: mh-pune-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting
problem_type: potholes

state: Maharashtra
district: Pune
city: Pune
municipality: Pune Municipal Corporation (PMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: Complaint is auto-routed to the ward's junior engineer per app description (mechanism confirmed via search summary, not directly fetched)

department: PMC Public Works / Road department (via PMC Road Mitra app)
authority: Pune Municipal Corporation
officer_designation: "Junior Engineer" responsible for the relevant ward — reported by search summary from a news source describing the PMC Road Mitra app, NOT an official PMC document; treat as unverified until fetched.

description: PMC Road Mitra is PMC's dedicated mobile app for pothole reporting, allowing photo/video + GPS-tagged submissions.
procedure: Citizen submits 2-3 photos/videos via the PMC Road Mitra app; GPS location auto-attached; complaint auto-routes to ward's junior engineer; before/after photos required to close the complaint.
required_information: Photos/videos of the pothole, GPS location (auto-captured by app)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: PMC Road Mitra mobile app (Android, Google Play Store)
contact_information: NOT FOUND IN OFFICIAL SOURCE (app-based, no separate phone/email surfaced for this specific channel)

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: PMC Apps Store
source_url: https://www.pmc.gov.in/en/b/pmc-apps-store
source_type: govt_portal
source_organization: Pune Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: App's existence and PMC ownership confirmed via pmc.gov.in's own apps store listing; workflow detail (photo requirement, junior-engineer routing) came from a news-source search summary, not an official document — flagged separately above, do not upgrade to A without direct confirmation. News coverage also notes the app had a period of inactivity due to an SMS-gateway lapse — a live-status caveat worth re-checking before relying on it as an active channel.
```

### Record: Maharashtra-Pune-Water-Drainage
```
service_id: mh-pune-water-drainage
service_name: Water & Drainage
sub_service: Drain blockage / overflow, manhole damage, sewerage/pipeline issues
problem_type: drain_blockage_overflow

state: Maharashtra
district: Pune
city: Pune
municipality: Pune Municipal Corporation (PMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (likely PMC Drainage/Sewerage department, name not confirmed on an official page in this pass)
authority: Pune Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: PMC's complaint system covers manhole replacement, drainage leakage into nalla/river, choked/overflowing drains, and sewerage pipeline issues. A separate dedicated grievance channel for water-supply issues specifically was reportedly launched (per a search result), but its official URL was not directly confirmed in this pass.
procedure: Same general channels as other PMC complaints (portal, toll-free, WhatsApp, email, Facebook) per pmc.gov.in's grievance-redressal page.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — a "15-30 day" figure appeared only via third-party aggregator search results, not confirmed on an official page.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online portal (complaint.pmc.gov.in), toll-free 18001030222, WhatsApp 9689900002, email feedback@punecorporation.org
contact_information: Toll-free 18001030222 / WhatsApp 9689900002 / feedback@punecorporation.org

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: GRIEVANCE REDRESSAL MECHANISM
source_url: https://www.pmc.gov.in/en/grievance-redressal
source_type: govt_portal
source_organization: Pune Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Water supply vs. drainage/sewerage split of responsibility (per 01_service_data_requirements.md's cross-state caution) was not resolvable to a single named department in this pass — flag for direct-fetch follow-up.
```

### Record: Maharashtra-Pune-Streetlight
```
service_id: mh-pune-streetlight
service_name: Streetlights
sub_service: Non-functioning streetlight, damaged pole, new-light request
problem_type: streetlight_not_working

state: Maharashtra
district: Pune
city: Pune
municipality: Pune Municipal Corporation (PMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (electrical/street-lighting department name not confirmed on an official page)
authority: Pune Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: PMC's Complaint Management System / PMC CARE app handles streetlight repair/replacement, including non-burning lights, new-light requests, and damaged pole/wire issues.
procedure: File via toll-free number, WhatsApp, or PMC's complaint portal; a token number and expected-resolution info are reportedly provided (per search summary — not confirmed via direct fetch).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — a "7-14 day" figure appeared only via third-party aggregator results.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Toll-free 18001030222, WhatsApp 9689900002, complaint.pmc.gov.in portal, Facebook (@PMCFMC), Twitter/X (@PMCPune)
contact_information: Toll-free 18001030222 / WhatsApp 9689900002

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: तक्रार :मुख्यपृष्ठ (PMC Complaint Portal)
source_url: https://complaint.pmc.gov.in/
source_type: grievance_portal
source_organization: Pune Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: No dedicated Smart City/ICCC streetlight channel surfaced for Pune specifically in this pass (contrast with what 01_service_data_requirements.md flags as common in Smart-City-integrated cities) — worth a targeted follow-up search.
```

### Record: Maharashtra-Mumbai-Waste-SolidWasteManagement
```
service_id: mh-mumbai-waste-solid-waste-management
service_name: Waste & Public Sanitation
sub_service: Solid waste management (general — collection, segregation bylaws)
problem_type: garbage_collection

state: Maharashtra
district: Mumbai City / Mumbai Suburban
city: Mumbai
municipality: Brihanmumbai Municipal Corporation (BMC / MCGM)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: BMC operates 24 administrative wards, each with a Citizen Facilitation Centre (CFC) — general structure confirmed via search summary referencing BMC's own ward system, specific ward list not fetched in this pass.

department: Solid Waste Management department, headed by a Chief Engineer (per the department's own RTI manual document name)
authority: Brihanmumbai Municipal Corporation
officer_designation: Chief Engineer, Solid Waste Management (from the source document's own title — "ChiefEngineerSolidWasteManagement"); specific named individual NOT FOUND IN OFFICIAL SOURCE

description: BMC's Solid Waste Management department publishes an RTI (Right to Information) manual under Section 4(1)(b) of the RTI Act, describing its structure and functions. Waste-management bylaws mandate source segregation (wet/dry) and set penalty clauses for non-adherence.
procedure: General civic complaints (including garbage-related) are filed via BMC's central complaint registration system or the mobile app; specific SWM-department-level procedure text not extracted in this pass (PDF not directly fetched).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND (search results referenced that BMC's own Citizen Charter contains SLA day-counts compared against complaints-closed data, per a third-party NGO report — the Citizen Charter document itself was not directly reached in this pass)
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Central Complaint Registration System (dm.mcgm.gov.in), MyBMC portal complaint form, MCGM 24×7 mobile app, Citizen Facilitation Centres (24, one per ward)
contact_information: Central helpline 1916 (24×7, per search summary — confirm on an official page before use)

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: Segregate wet and dry waste at source; do not dump in plastic/non-biodegradable bags (per bylaw description in search summary — verify against the primary bylaw document before citing directly).

source_title: INFORMATION OF SOLID WASTE MANAGEMENT DEPARTMENT UNDER SUB SECTION 4(1)(b)
source_url: https://www.mcgm.gov.in/irj/go/km/docs/documents/MCGM%20Department%20List/ChiefEngineerSolidWasteManagement/RTI%20Manuals/CESWM_RTI_E02.pdf
source_type: official_pdf
source_organization: Brihanmumbai Municipal Corporation — Solid Waste Management Department

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A (rather than B) because the document is an official department-specific RTI disclosure PDF, the most specific/authoritative source type found for this record — but the PDF's actual body text was not read in this pass, only its existence and title confirmed via search. Re-verify contents before treating any specific procedural claim as final.
```

### Record: Maharashtra-Mumbai-Water-Drainage
```
service_id: mh-mumbai-water-drainage
service_name: Water & Drainage
sub_service: Water supply / sewerage complaints
problem_type: no_low_water_supply

state: Maharashtra
district: Mumbai City / Mumbai Suburban
city: Mumbai
municipality: Brihanmumbai Municipal Corporation (BMC / MCGM)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (BMC is confirmed as the responsible body for "water supply, sewerage/sanitation" per its own general responsibility statement in search summary, but a specific department name/officer was not surfaced)
authority: Brihanmumbai Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: BMC is directly responsible for water supply and sewerage/sanitation citywide (unlike some other states, this is not split off to a separate state water board, per the general responsibility statement found — but this should be re-confirmed directly, since 01_service_data_requirements.md flags this split as common elsewhere).
procedure: Filed via ward control room, the central helpline (1916), or the MCGM 24×7 app.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Ward control room, central helpline 1916, MCGM 24×7 app, online portal
contact_information: 1916 (24×7 central helpline, per search summary)

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Lodging Civic Complaints — MyBMC
source_url: https://portal.mcgm.gov.in/irj/portal/anonymous?NavigationTarget=navurl%3A%2F%2F292767acb759a47eeb3b07911ad27c98&guest_user=english
source_type: govt_portal
source_organization: Brihanmumbai Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: URL is a stateful/session-style MCGM portal navigation link, which may not resolve identically on a fresh visit — flag as a URL that especially needs direct re-confirmation.
```

### Record: Maharashtra-Mumbai-Roads-Potholes
```
service_id: mh-mumbai-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting
problem_type: potholes

state: Maharashtra
district: Mumbai City / Mumbai Suburban
city: Mumbai
municipality: Brihanmumbai Municipal Corporation (BMC / MCGM)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: Handled via each of BMC's 24 wards' control rooms (general structure, not fetched in detail for this record)

department: NOT FOUND IN OFFICIAL SOURCE
authority: Brihanmumbai Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Citizens report potholes via BMC's MCGM 24×7 mobile app, sharing photos and exact location; a complaint number is issued for tracking.
procedure: Submit photo + location via MCGM 24×7 app or the online portal; receive a complaint/tracking number.
required_information: Photo and location of the pothole
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — a "48-hour deadline" for pothole-filling was referenced only in a news article about BMC missing that deadline during monsoon season (pressreader.com, third-party), not confirmed on an official page.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: MCGM 24×7 mobile app, online complaint portal, ward Citizen Facilitation Centres
contact_information: 1916 (24×7 central helpline)

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Central Complaint Registration System
source_url: https://dm.mcgm.gov.in/central-complaint-registration-system
source_type: govt_portal
source_organization: Brihanmumbai Municipal Corporation (Disaster Management portal)

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: The "48-hour" figure is a notable, widely-reported public commitment — worth a targeted direct-fetch follow-up to find it on an official BMC page (e.g. a monsoon-preparedness circular), since if confirmed it would upgrade this to a proper SLA record instead of NOT FOUND.
```

### Record: Maharashtra-Mumbai-Streetlight
```
service_id: mh-mumbai-streetlight
service_name: Streetlights
sub_service: Non-functioning streetlight, damaged pole
problem_type: streetlight_not_working

state: Maharashtra
district: Mumbai City / Mumbai Suburban
city: Mumbai
municipality: Brihanmumbai Municipal Corporation (BMC / MCGM)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Brihanmumbai Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Streetlight issues are one of the civic services citizens can report through each ward's control room, alongside water and road issues.
procedure: Call the ward control room or use the central helpline / online portal / app.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Ward control room, central helpline 1916, online portal/app
contact_information: 1916 (24×7 central helpline)

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: WardC — MyBMC
source_url: https://portal.mcgm.gov.in/irj/portal/anonymous/qlwardc?guest_user=english
source_type: govt_portal
source_organization: Brihanmumbai Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Least-detailed of Mumbai's 4 service records — this category, as anticipated in 01_service_data_requirements.md, appears to have the thinnest dedicated documentation.
```

### Record: Maharashtra-Nagpur-AllServices-GrievanceSystem
```
service_id: mh-nagpur-all-grievance-system
service_name: (cross-cutting — grievance system covers all 4 categories)
sub_service: General civic grievance registration and escalation
problem_type: multiple (sewerage choking, solid waste/irregular garbage lifting, low-pressure water supply, bad roads, non-functioning streetlights all explicitly named as handled)

state: Maharashtra
district: Nagpur
city: Nagpur
municipality: Nagpur Municipal Corporation (NMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (routed by category internally; specific department names not surfaced)
authority: Nagpur Municipal Corporation
officer_designation: Deputy Commissioner (of the relevant Department/Zone) is named as the first escalation point; Commissioner/Mayor as a further escalation point — per NMC's own grievance system description (see escalation_procedure below).

description: NMC's Grievance Redressal System accepts complaints across categories including choked sewerage, solid waste/garbage lifting, low-pressure water supply, encroachments, bad roads, stray dogs, illegal dumping, and non-functioning streetlights.
procedure: File via NMC's online complaint form (nmcnagpur.gov.in/grievance/complaint_form.php), the Nagpur Live City app (launched 2020), or WhatsApp helpline.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — NMC's own citizen charter is referenced as having a resolution timeline ("if not resolved according to the citizen charter timeline"), but the specific day-counts were not surfaced/fetched in this pass.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online complaint form, Nagpur Live City app, WhatsApp helpline 8600004746, toll-free citizen helpline
contact_information: WhatsApp 8600004746

escalation_procedure: If unresolved per the citizen charter timeline, or the citizen is unsatisfied, escalate to NMC's Public Grievance Cell, then to the Deputy Commissioner of the relevant Department/Zone, then to the Commissioner or Mayor of NMC.
escalation_authority: NMC Public Grievance Cell → Deputy Commissioner (Dept/Zone) → Commissioner/Mayor, NMC

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Grievance Redressal System — NMC
source_url: https://www.nmcnagpur.gov.in/grievance/
source_type: govt_portal
source_organization: Nagpur Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Best-documented escalation chain of the three Maharashtra cities in this pass — worth prioritizing for direct-fetch confirmation, since a confirmed multi-level escalation chain (Public Grievance Cell → Deputy Commissioner → Commissioner/Mayor) would be a strong, reusable RAG fact once verified.
```

---

## Coverage notes for Maharashtra

- **Best-covered service:** Waste & Sanitation (SWM), consistent with the
  expectation in `01_service_data_requirements.md` that Swachh Bharat
  Mission's national push gives this category the most published
  material — plus it's the only category with genuine `data.gov.in` OGD
  datasets found (Pune, Thane).
- **Weakest-covered service:** Streetlights — no dedicated department
  name, SLA, or escalation path surfaced for any of the 3 cities, matching
  the expectation flagged in the service-requirements doc.
- **Water vs. drainage jurisdiction split**: not clearly resolved for any
  of the 3 cities in this pass — flagged as a specific follow-up item in
  `13_missing_data_report.md`.
- **Third city choice**: Nagpur was used instead of Nashik — NMC's own
  domain (`nmcnagpur.gov.in`) surfaced richer, more specific grievance/
  escalation detail in search results than what came back for Nashik in a
  quick comparison search, making it the stronger pilot candidate of the
  two.
- Nothing in this file should be read as confirming exact SLA numbers —
  every specific day-count claim found in this pass traced back to
  third-party aggregator sites, not an official page, and is logged only
  as such (`SLA NOT FOUND` in the official record, third-party figures
  mentioned in `notes` for context only).
