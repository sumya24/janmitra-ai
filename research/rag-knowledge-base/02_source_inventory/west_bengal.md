# West Bengal — Official Source Inventory

**Cities researched:** Kolkata (KMC), Howrah (HMC)
**Method:** WebSearch only — WebFetch (direct page-fetch/verification) was
unavailable in this environment for the entire duration of this research
pass. Every record is marked `NOT INDEPENDENTLY FETCHED` in
`verification_status` as a result. `source_quality` still reflects how
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
> below. One specific figure — a claimed "resolved within a week" SLA for
> KMC online complaints — appeared in a search-engine-synthesized answer
> that mixed the official kmcgov.in domain with a third-party aggregator
> in the same result set; because its exact origin domain could not be
> isolated, it is **not** entered into any `sla` field below and is
> logged only in `notes` as unconfirmed.

---

## Summary table

| State | City | Service | Source | Authority | URL | Format | Data Available | RAG or SQL | Quality |
|---|---|---|---|---|---|---|---|---|---|
| West Bengal | Kolkata | All services (complaint procedure) | Complaint Procedure — Official Website of KMC | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/ComplaintProcedure.jsp | HTML | Procedure, channels | RAG | B |
| West Bengal | Kolkata | All services (complaint form) | KMC Common Complaint e-Form | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/ComplaintFormAction.do | Web form | Channel | RAG | B |
| West Bengal | Kolkata | All services (citizen charter) | Citizen Charter — Official Website of KMC | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/CitizenCharter.jsp | HTML | Service standards | RAG | B |
| West Bengal | Kolkata | Waste & Sanitation | Solid Waste Management Services | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/Solid_Waste_Services.html | HTML | Department info, service description | RAG | A |
| West Bengal | Kolkata | Waste & Sanitation | Solid Waste FAQs | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/SolidWasteFAQs.jsp | HTML | FAQ, citizen guidance | RAG | A |
| West Bengal | Kolkata | Water & Drainage (water supply) | Water Supply Department page | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/Water_Supply.html | HTML | Department info | RAG | A |
| West Bengal | Kolkata | Water & Drainage (water supply — citizen charter) | Citizens' Charter — Water Supply Department | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/downloads/citizens_charter_water_supply.pdf | PDF | Service-by-service standards | RAG | A |
| West Bengal | Kolkata | Water & Drainage (water supply — citizen charter, dated version) | Citizen's Charter of Water Supply Department (2016) | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/downloads/citizens_charter_water_supply_2016.pdf | PDF | Service-by-service standards (dated) | RAG | A |
| West Bengal | Kolkata | Water & Drainage (new connection) | How to get Water Connection in Your New House? | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/WaterConnection.jsp | HTML | Procedure | RAG | B |
| West Bengal | Kolkata | Water & Drainage (sewerage/drainage) | Sewerage and Drainage Services | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/SewerageAndDrainageServices.jsp | HTML | Department info, service description | RAG | A |
| West Bengal | Kolkata | Water & Drainage (manholes) | Manholes — report to Control Room/Borough Office | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/Manholes.jsp | HTML | Procedure, channel | RAG | A |
| West Bengal | Kolkata | Roads & Potholes | Roads Dept. — Official Website of KMC | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/Roads.jsp | HTML | Department info | RAG | A |
| West Bengal | Kolkata | Roads & Potholes (contact) | Roads Dept. Contact | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/RoadsContact.jsp | HTML | Contact/channel | RAG | A |
| West Bengal | Kolkata | Roads & Potholes (development scheme) | List of KMC Road Development Scheme | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/KMCRoadDevelopmentDetails.jsp | HTML | Policy/scheme reference | RAG | B |
| West Bengal | Kolkata | Streetlights | Street Lighting — Official Website of KMC | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/KMCStreetLight.jsp | HTML | Department info | RAG | A |
| West Bengal | Kolkata | Streetlights | Lighting Services | Kolkata Municipal Corporation | https://www.kmcgov.in/KMCPortal/jsp/Lighting.html | HTML | Service description | RAG | A |
| West Bengal | Howrah | All services | Contacts — Howrah Municipal Corporation | Howrah Municipal Corporation (HMC) | https://www.myhmc.in/contacts/ | HTML | Contact/channel | RAG | B |
| West Bengal | Howrah | All services (complaint submission) | HMC-GRS — Complaint Submission | Howrah Municipal Corporation | https://www.myhmc.in/grs/ | Web form | Procedure, channel | RAG | B |
| West Bengal | Howrah | All services (status check) | View Complaint Status — HMC-GRS | Howrah Municipal Corporation | https://www.myhmc.in/grs/viewgrsticket.php | Web app | Status tracking | RAG | B |
| West Bengal | Howrah | All services (district portal reference) | HMC related services | District Howrah, Government of West Bengal | https://howrah.gov.in/service/hmc-related-services/ | HTML | Directory | RAG | B |
| West Bengal | (state-wide) | All services (escalation) | Our Vision — CMO Grievance Cell (Public Grievance Monitoring System, PGMS) | Government of West Bengal, Chief Minister's Office | https://cmo.wb.gov.in/default1.aspx | HTML | Escalation (state-level appellate channel) | RAG | B |
| West Bengal | (state-wide) | Roads & Potholes (state PWD, jurisdiction-split reference) | PWD West Bengal grievance login | Public Works Department, West Bengal | https://pwd.wb.gov.in/general/login?module=grievance | Web app | Channel (state-highway/PWD-road jurisdiction) | RAG | B |
| West Bengal | (state-wide) | Urban Development (department) | Department of Urban Development & Municipal Affairs | Government of West Bengal | https://udma.wb.gov.in/ | HTML | Policy, department directory | RAG | B |
| West Bengal | New Town, Kolkata | Waste & Sanitation | Solid Waste Management_NewTown_Kolkata | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | https://www.data.gov.in/catalog/solid-waste-managementnewtownkolkata | Dataset (catalog) | Source segregation, D2D efficiency, bin placement, vehicle capacity | Structured/SQL | C |
| West Bengal | Kolkata | (reference only, not verified fact source) | KMC — How to File a Complaint to Kolkata Municipal Corporation? | complainthub.org (third-party) | https://complainthub.org/kmc-kolkata/ | HTML | Aggregated complaint-channel info, unverifiable SLA claims | reference only | D |
| West Bengal | Kolkata | (reference only, not verified fact source) | KMC to show-cause officials if complaints remain pending | millenniumpost.in (news, third-party) | https://www.millenniumpost.in/bengal/kmc-to-show-cause-officials-if-complaints-remain-pending-577330 | HTML | News report referencing internal KMC accountability process | reference only | D |
| West Bengal | Kolkata | (reference only, not verified fact source) | Municipal Corporation of Kolkata Complaints & Reviews | consumercomplaints.in (third-party) | https://www.consumercomplaints.in/municipal-corporation-of-kolkata-b102049 | HTML | Unverified citizen complaint anecdotes | reference only | D |

---

## Full records

### Record: WestBengal-Kolkata-Waste-SolidWasteManagement
```
service_id: wb-kolkata-waste-solid-waste-management
service_name: Waste & Public Sanitation
sub_service: Garbage collection, removal of garbage/carcasses, public-place cleanliness, garbage vehicles
problem_type: garbage_collection

state: West Bengal
district: Kolkata
city: Kolkata
municipality: Kolkata Municipal Corporation (KMC)
zone: KMC operates through 16 boroughs covering 144 wards, per general search-summary description of KMC's structure — specific zone/borough-to-ward mapping document not fetched in this pass.
ward: Complaints require a ward number as mandatory input on KMC's online grievance form, per search summary — specific ward routing logic not confirmed.

department: Solid Waste Management department (confirmed via KMC's own dedicated "Solid Waste Management Services" page)
authority: Kolkata Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: KMC is responsible for collection, transportation, disposal, and treatment of waste generated in the city — approximately 4,000 MT/day per search summary. KMC has also run a "One-Week Solid Waste Management Drive" (announced via its own social-media account) aimed at eliminating garbage black spots/dumps across all 144 wards and encouraging complaint-based public participation. Complaints covered include garbage collection, removal of garbage/carcasses, solid waste management issues, garbage-vehicle problems, and public places not being cleaned.
procedure: File via KMC's online Common Complaint e-Form (mandatory: name, address, contact number, pin code, complaint type, complaint details, ward number), or in person at designated grievance counters at KMC HQ, e-Kolkata citizen service centers, and Borough Offices.
required_information: Name, address, contact number, pin code, complaint type/category, complaint details, ward number
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — a "resolved within a week" figure for KMC's general online complaints appeared in a search-engine-synthesized answer whose exact source domain (kmcgov.in vs. a mixed-in third-party aggregator) could not be isolated in this pass. Do not treat as verified.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online Common Complaint e-Form (kmcgov.in), in-person grievance counters (KMC HQ, e-Kolkata centers, Borough Offices), KMC Control Room (033) 2286 1212 / 1313 / 1414
contact_information: KMC Control Room (033) 2286 1212 / (033) 2286 1313 / (033) 2286 1414

escalation_procedure: If not redressed within the given time limit, or the citizen is unsatisfied with the final response, escalate to the Public Grievance Cell or Public Relations Department of KMC, or approach the Commissioner (Head Office) or Joint Commissioners of the concerned Ward/Zone — per search summary of KMC's general grievance-escalation description; not confirmed as waste-specific.
escalation_authority: KMC Public Grievance Cell / Public Relations Department → Joint Commissioner (Ward/Zone) → Commissioner, KMC

faq: KMC publishes a dedicated "Solid Waste FAQs" page (https://www.kmcgov.in/KMCPortal/jsp/SolidWasteFAQs.jsp) — specific Q&A content was not extracted from search snippets in this pass; flagged as a priority direct-fetch target given it is the most citizen-facing, service-specific document found for this record.
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE (beyond the existence of the FAQ page above)

source_title: Solid Waste Management Services
source_url: https://www.kmcgov.in/KMCPortal/jsp/Solid_Waste_Services.html
source_type: govt_portal
source_organization: Kolkata Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A because kmcgov.in hosts a dedicated, service-specific department page (not just a general complaint form) — the strongest domain-level signal found for Kolkata waste. The SolidWasteFAQs.jsp page is a strong candidate for citizen_guidance/faq once directly fetched. KMC's landfill-capacity/siting difficulties are widely reported in secondary sources but are NOT logged as facts here since they are policy-context, not a citizen-complaint-procedure fact, and were not found stated on an official KMC page in this pass.
```

### Record: WestBengal-Kolkata-Water-Drainage
```
service_id: wb-kolkata-water-drainage
service_name: Water & Drainage
sub_service: Water supply (new connection, leakage), sewerage/drainage, manholes, waterlogging
problem_type: no_low_water_supply

state: West Bengal
district: Kolkata
city: Kolkata
municipality: Kolkata Municipal Corporation (KMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Two distinct KMC departments confirmed via official pages — the "Water Supply Department" (own citizen charter PDF) and the separate "Sewerage and Drainage" department/services page. This is a within-corporation department split rather than a separate external authority (unlike, e.g., a state Jal Board model) — both sit under KMC itself, per the pages found.
authority: Kolkata Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: KMC's Water Supply Department has expanded piped-water supply via treatment plants (Indira Gandhi WTP, Dhapa WTP), booster pumping stations (e.g. Tallah), reservoirs, headworks, and new tubewells where piped supply is lacking; it publishes new domestic, industrial/commercial/institutional (ICI), and bulk-meter connection services, and has a dedicated Citizens' Charter PDF (with an earlier, dated 2016 version also indexed separately). KMC's Sewerage and Drainage department provides outfall for drainage and discharge of stormwater/sewage; the city's sewer network includes ~180 km of century-old brick sewers, contributing to recurring monsoon waterlogging from siltation/structural deterioration (per search summary — infrastructure-condition context, not a citizen-complaint procedure fact).
procedure: New water connection — apply online via KMC's Online Application for New Water Connection page (WaterConnectionSanction.jsp). Manhole/pipeline/sewage-outflow issues — immediately inform the KMC Control Room / Borough Office (per the dedicated Manholes.jsp page). Sewerage/drainage complaints generally — file via KMC's online grievance form with ward number.
required_information: For sewerage/drainage complaints: name, address, contact number, pin code, complaint type, complaint details, ward number (per general KMC grievance-form requirements)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online grievance form (kmcgov.in), Water Connection application portal, Manholes reporting instructions (Control Room/Borough Office), Cossipur Section office (033-2558 8553), Behala S.S. Unit (033-2468 1034)
contact_information: Cossipur Section 2558 8553 / Behala S.S. Unit 2468 1034 (specific water-supply operational units found in search results — likely not a complete list)

escalation_procedure: ESCALATION INFORMATION NOT FOUND specifically for water/drainage (general KMC escalation path — Public Grievance Cell → Joint Commissioner → Commissioner — is expected to apply per the AllServices pattern, but not confirmed tied to this department specifically)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizens' Charter — Water Supply Department
source_url: https://www.kmcgov.in/KMCPortal/downloads/citizens_charter_water_supply.pdf
source_type: citizen_charter
source_organization: Kolkata Municipal Corporation — Water Supply Department

publication_date: NOT FOUND IN OFFICIAL SOURCE (a separately-indexed "2016" version of this PDF also exists — https://www.kmcgov.in/KMCPortal/downloads/citizens_charter_water_supply_2016.pdf — suggesting the charter has been updated at least once; whether the non-dated URL is a newer version was not confirmed)
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A — this is a dedicated, department-specific, service-by-service Citizens' Charter PDF, the most specific document type found across all three states in this pass (matching how Mumbai's SWM RTI manual PDF was rated A in the Maharashtra pilot). The PDF's actual body text (service numbers, day-counts) was not read in this pass — only its existence, title, and URL were confirmed via search; this is the single highest-priority direct-fetch target in this file, since if its per-service SLA table is confirmed it would upgrade several `SLA NOT FOUND` fields above to real values. The water-supply-vs-sewerage/drainage split is a within-KMC departmental split, not a separate external authority — this differs from the Jal Board-style split flagged as common elsewhere in 01_service_data_requirements.md, and should not be assumed to generalize to other West Bengal cities.
```

### Record: WestBengal-Kolkata-Roads-Potholes
```
service_id: wb-kolkata-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting, road repair, road development
problem_type: potholes

state: West Bengal
district: Kolkata
city: Kolkata
municipality: Kolkata Municipal Corporation (KMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Roads Department (confirmed via KMC's own dedicated "Roads Dept." and "Roads Dept. Contact" pages)
authority: Kolkata Municipal Corporation (for municipal roads); Public Works Department, West Bengal (pwd.wb.gov.in — separate grievance portal found, implying a jurisdiction split for state-highway/PWD-classified roads within city limits, though the exact road-classification boundary was not confirmed in this pass)
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: KMC's Roads Department has documented major civil works and road works (search summary references a range spanning 2005-06 to 2008-09, likely an old/archival project list rather than current status — flagged as OUTDATED / VERIFY BEFORE PRODUCTION USE if used for anything beyond confirming the department's existence). Citizens report road-repair-needed complaints through KMC's general complaint system; the corporation logs these centrally in a complaints e-database to monitor action taken.
procedure: Submit via KMC's online complaint form or standard paper complaint forms available at public grievance counters at KMC HQ, e-Kolkata citizen service centers, and Borough Offices; recorded in a central complaints logging e-database.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online complaint form (kmcgov.in), paper forms at grievance counters (KMC HQ, e-Kolkata centers, Borough Offices)
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Roads Dept. — Official Website of Kolkata Municipal Corporation
source_url: https://www.kmcgov.in/KMCPortal/jsp/Roads.jsp
source_type: govt_portal
source_organization: Kolkata Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A for the dedicated department page + dedicated Roads Dept. Contact page combination — but the road-project date range surfaced in search summary (2005-06 to 2008-09) looks stale and should not be used to characterize current road-maintenance activity without a fresh direct fetch. The West Bengal PWD grievance portal (pwd.wb.gov.in) is logged in the summary table as a likely-relevant jurisdiction-split source for state-highway-classified roads within Kolkata, but this split was not independently confirmed for Kolkata specifically in this pass.
```

### Record: WestBengal-Kolkata-Streetlight
```
service_id: wb-kolkata-streetlight
service_name: Streetlights
sub_service: Streetlight not working, installation/maintenance
problem_type: streetlight_not_working

state: West Bengal
district: Kolkata
city: Kolkata
municipality: Kolkata Municipal Corporation (KMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Lighting Department (confirmed via KMC's own dedicated "Street Lighting" and "Lighting Services" pages)
authority: Kolkata Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: KMC's Lighting Department manages installation and maintenance of streetlights, including both routine and emergency maintenance.
procedure: File online via KMC's grievance form (entering name, contact number, address, pin code) at the Common Complaint e-Form link, or contact the KMC Control Room directly.
required_information: Name, contact number, address, pin code (per general KMC grievance-form requirements)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online Common Complaint e-Form (https://www.kmcgov.in/KMCPortal/ComplaintFormAction.do), KMC Control Room (033) 2286 1212 / (033) 2286 1313 / (033) 2286 1414
contact_information: KMC Control Room (033) 2286 1212 / 1313 / 1414

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Street Lighting — Official Website of Kolkata Municipal Corporation
source_url: https://www.kmcgov.in/KMCPortal/jsp/KMCStreetLight.jsp
source_type: govt_portal
source_organization: Kolkata Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A — this is the one state/city in this 3-state pass where Streetlights, usually the weakest-documented category per 01_service_data_requirements.md, actually has its own dedicated official department page (KMCStreetLight.jsp) distinct from the general lighting-services page (Lighting.html). Still no discrete SLA found, matching the expectation that this category rarely publishes one.
```

### Record: WestBengal-Howrah-AllServices-GrievanceSystem
```
service_id: wb-howrah-all-grievance-system
service_name: (cross-cutting — grievance system covers all 4 categories)
sub_service: Garbage collection, road maintenance, streetlight issues, other municipal services
problem_type: multiple (garbage disposal, street cleanliness, solid waste management, road/street building and maintenance, and street lighting all explicitly named as HMC responsibilities per search summary)

state: West Bengal
district: Howrah
city: Howrah
municipality: Howrah Municipal Corporation (HMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: Complaint form requires a ward number per general HMC-GRS grievance-form description (consistent with the KMC pattern) — not independently confirmed for HMC specifically.

department: NOT FOUND IN OFFICIAL SOURCE (HMC is confirmed generally responsible for garbage disposal, street cleanliness, solid waste management, road/street building and maintenance, and street lighting per search summary; specific internal department names not surfaced)
authority: Howrah Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: HMC operates an online Grievance Redressal System (HMC-GRS) allowing citizens to submit and track complaint status. The HMC website (myhmc.in) covers garbage collection, road maintenance, streetlight issues, and other civic services.
procedure: Submit online via HMC-GRS complaint submission form; track status via the "View Complaint Status" tool using a ticket reference.
required_information: NOT FOUND IN OFFICIAL SOURCE beyond general grievance-form fields (name, address, contact, complaint type/details, likely ward number, per the pattern seen elsewhere in West Bengal)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: HMC-GRS online portal (myhmc.in/grs/), Toll-free 1800 121 500 000, Phone 033-2638 3211 / 3212 / 3213, WhatsApp 6292232868, email citizen.care@myhmc.in, "Chairman On Call" 8100883300 (Mon–Fri, 12–2 PM)
contact_information: Toll-free 1800 121 500 000 (for complaints) / 033-2638 3211 (Mon–Sat, 10:30am–5:30pm) / email citizen.care@myhmc.in

escalation_procedure: ESCALATION INFORMATION NOT FOUND for HMC specifically in this pass. The state-wide West Bengal CMO Public Grievance Monitoring System (PGMS) allows escalation of unresolved municipal-body grievances to the Grievance Cell, WB CMO, and ultimately to the Chief Minister — this is a state-wide channel, not confirmed as an HMC-specific escalation step.
escalation_authority: NOT FOUND IN OFFICIAL SOURCE (HMC-specific); WB CMO Grievance Cell (state-wide fallback channel, per cmo.wb.gov.in)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Contacts — Howrah Municipal Corporation
source_url: https://www.myhmc.in/contacts/
source_type: govt_portal
source_organization: Howrah Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: myhmc.in is not a .gov.in/.wb.gov.in domain, but is consistently referenced as HMC's own portal across multiple independent search results, including the official howrah.gov.in district site listing it under "HMC related services" — treated as B (official-but-unconfirmed-TLD), the same treatment given to comparable ULB-branded non-.gov.in domains in the Uttar Pradesh file. Howrah did not surface any service-specific department pages comparable to KMC's dedicated Solid_Waste_Services.html / Roads.jsp / KMCStreetLight.jsp pages in this pass — this is the main reason Kolkata, not Howrah, is the better-documented West Bengal city overall, and no individual per-service (waste/water/roads/streetlight) full records were built for Howrah given how thin each would be beyond what's already captured here.
```

---

## Coverage notes for West Bengal

- **Best-covered service:** Kolkata's civic services overall are unusually
  well-documented compared to the other cities/states researched in this
  pass — KMC's own domain (kmcgov.in) hosts dedicated, department-specific
  pages for all 4 categories (Solid_Waste_Services.html /
  SolidWasteFAQs.jsp, Water_Supply.html + a dedicated Water Supply
  Citizens' Charter PDF, SewerageAndDrainageServices.jsp, Roads.jsp +
  RoadsContact.jsp, KMCStreetLight.jsp + Lighting.html) — this let every
  Kolkata full record in this file reach quality A, a notably higher hit
  rate than either Maharashtra or Uttar Pradesh achieved in this research
  program so far.
- **Weakest-covered service / weakest-covered city:** Streetlights still
  had no discrete SLA anywhere (even with a dedicated official page,
  KMCStreetLight.jsp) — matching the pattern seen elsewhere. At the city
  level, Howrah is far thinner than Kolkata: HMC has a working grievance
  system (HMC-GRS) and general contact channels, but no service-specific
  department pages comparable to KMC's were found, so only one
  cross-cutting record was built for it rather than 4 per-service ones.
- **Water vs. drainage jurisdiction split**: for Kolkata specifically,
  this is a within-KMC departmental split (Water Supply Department vs.
  Sewerage and Drainage department), not a separate external
  board/authority — this is a meaningfully different pattern from what a
  Jal Board-style state split (flagged as common in
  `01_service_data_requirements.md`) would look like, and should not be
  assumed to hold for other West Bengal ULBs without separate
  confirmation.
- **Roads jurisdiction split**: a distinct West Bengal PWD grievance
  portal (pwd.wb.gov.in) was found, suggesting the usual
  municipal-road-vs-state-highway split noted in
  `01_service_data_requirements.md` likely applies within Kolkata too,
  but this was not independently confirmed as applying to any specific
  road/complaint in this pass — logged as a summary-table reference only.
- **Second city choice**: Howrah (HMC) was used instead of a Tier-2 city
  like Siliguri or Durgapur — Howrah's own domain (myhmc.in) surfaced a
  working, actively-referenced grievance system (HMC-GRS) with real
  contact channels, which is more than a quick comparison search returned
  for other West Bengal Tier-2 cities in this pass.
- The single highest-value follow-up target in this file is the KMC Water
  Supply Department's Citizens' Charter PDF
  (citizens_charter_water_supply.pdf) — its existence and title are
  confirmed, but its actual service-by-service SLA table was not read in
  this pass; if directly fetched and confirmed, it could upgrade several
  `SLA NOT FOUND` water-related fields above to real values.
- Nothing in this file should be read as confirming exact SLA numbers —
  the one specific day-count figure found ("resolved within a week" for
  KMC online complaints) could not be cleanly attributed to the official
  domain alone in the search-result synthesis and is logged only in
  `notes`, not in any `sla` field, per the same discipline applied in the
  Maharashtra and Uttar Pradesh files.
