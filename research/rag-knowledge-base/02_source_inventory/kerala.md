# Kerala — Official Source Inventory

**Cities researched:** Kochi (Cochin Corporation), Thiruvananthapuram (TMC)
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
> below. Kerala's Local Self Government Department runs almost all ULB
> websites on a shared `*.lsgkerala.gov.in` domain family, which gave
> unusually high domain-level confidence throughout this pass — but
> "genuinely an official domain" is still not the same as "content
> independently confirmed by direct read," and every specific figure
> below is qualified accordingly.

---

## Summary table

| State | City | Service | Source | Authority | URL | Format | Data Available | RAG or SQL | Quality |
|---|---|---|---|---|---|---|---|---|---|
| Kerala | Kochi | All services (grievance cell) | Public Grievance Cell | Cochin Corporation (LSGD Kerala) | https://kochicorporation.lsgkerala.gov.in/en/form/public-grievance-cellnew | HTML | Procedure, channel | RAG | B |
| Kerala | Kochi | All services (app/portal) | My Kochi — Complaints | Cochin Corporation (LSGD Kerala) | https://mykochi.lsgkerala.gov.in/index/complaint | Web app | Procedure, channel | RAG | B |
| Kerala | Kochi | All services (status check) | My Kochi — All Complaints / Complaint Status | Cochin Corporation (LSGD Kerala) | https://mykochi.lsgkerala.gov.in/index/complaintstatus | Web app | Status tracking | RAG | B |
| Kerala | Kochi | Waste & Sanitation | Solid Waste Management | Cochin Corporation (LSGD Kerala) | https://kochicorporation.lsgkerala.gov.in/en/solid-waste-management/368 | HTML | Department info, service description | RAG | A |
| Kerala | Kochi | Waste & Sanitation | List of Empanelment Agencies for Solid Waste Management | Cochin Corporation (LSGD Kerala) | https://kochicorporation.lsgkerala.gov.in/en/list-empanelment-agencies-solid-waste-management/491 | HTML | Service delivery detail | RAG | A |
| Kerala | Kochi | Water & Drainage (sewerage) | Septage Management Byelaw (Draft) | Cochin Corporation (LSGD Kerala) | https://kochicorporation.lsgkerala.gov.in/system/files/2022-02/Septage_management_bylaw.pdf | PDF | Policy, sewerage/septage rules | RAG | A |
| Kerala | Kochi | Roads & Potholes / Streetlights | Engineering | Cochin Corporation (LSGD Kerala) | https://kochicorporation.lsgkerala.gov.in/en/engineering | HTML | Department directory (minimal content) | RAG | B |
| Kerala | Thiruvananthapuram | All services (grievance mechanism) | Grievances Redressal Mechanism | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | https://tmc.lsgkerala.gov.in/en/grievances-redressal-mechanism/1749 | HTML | Procedure, escalation | RAG | B |
| Kerala | Thiruvananthapuram | All services (grievance cell) | Public Grievance Cell | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | https://tmc.lsgkerala.gov.in/en/public-grievance-cell | HTML | Procedure, channel | RAG | B |
| Kerala | Thiruvananthapuram | All services (organisational structure) | Organisational Structure | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | https://tmc.lsgkerala.gov.in/en/organisational-structure | HTML | Jurisdiction, department roles | RAG | B |
| Kerala | Thiruvananthapuram | Waste & Sanitation | Solid Waste Management | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | https://tmc.lsgkerala.gov.in/en/solid-waste-management | HTML | Department info, service description | RAG | A |
| Kerala | Thiruvananthapuram | Waste & Sanitation | Solid Waste Disposal | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | https://tmc.lsgkerala.gov.in/en/kharamaalainaya-nairamaarajajanam | HTML | Service description | RAG | A |
| Kerala | Thiruvananthapuram | Waste & Sanitation | Capital city, Clean city — waste collection centres and calendar | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | https://tmc.lsgkerala.gov.in/en/english | HTML | Collection schedule/locations | RAG | A |
| Kerala | Thiruvananthapuram | Roads & Potholes / Streetlights | Engineering | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | https://tmc.lsgkerala.gov.in/en/engineering | HTML | Department structure, jurisdiction (KSEB streetlight split) | RAG | A |
| Kerala | Thiruvananthapuram | All services (integrated portal) | Smart Trivandrum — Civic Services Portal | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | https://smarttvm.tmc.lsgkerala.gov.in/ | Web app | Procedure, channel, tracking | RAG | A |
| Kerala | Thiruvananthapuram | All services (complaint intake) | Smart Trivandrum — Report a Complaint | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | https://smarttvm.tmc.lsgkerala.gov.in/complaint/report | Web app | Channel | RAG | A |
| Kerala | Kochi + Thiruvananthapuram | Water & Drainage | Consumer Grievances | Kerala Water Authority (KWA) | https://kwa.kerala.gov.in/en/consumer-grievances/ | HTML | Procedure, channel | RAG | A |
| Kerala | Kochi + Thiruvananthapuram | Water & Drainage | Contact Us — KWA | Kerala Water Authority (KWA) | https://kwa.kerala.gov.in/en/contact-us/ | HTML | Contact/channel | RAG | B |
| Kerala | Kochi + Thiruvananthapuram | Water & Drainage | Consumers Corner | Kerala Water Authority (KWA) | https://kwa.kerala.gov.in/en/citizen-corner/ | HTML | Procedure, citizen guidance | RAG | B |
| Kerala | Kochi + Thiruvananthapuram | Water & Drainage | Aqualoom — KWA online complaint system | Kerala Water Authority (KWA) | https://aqualoom.kwa.kerala.gov.in/ | Web app | Channel (leak, shortage, billing, JJM, sewerage complaints) | RAG | A |
| Kerala | (state-wide) | All services (citizen charter) | Citizen Charter | Local Self Government Department (LSGD), Govt. of Kerala | https://lsgkerala.gov.in/en/resources/citizen-charter | HTML | Policy, service standards | RAG | B |
| Kerala | (state-wide) | Waste & Sanitation | Policy & Guidelines — Solid Waste Management | Local Self Government Department (LSGD), Govt. of Kerala | https://lsgd.kerala.gov.in/en/waste-management/solid-waste-management/policy-guidelines/ | HTML | Policy | RAG | B |
| Kerala | (state-wide) | All services (grievance mechanism, general) | Public Grievance Redressal Mechanism | Local Self Government Department (LSGD), Govt. of Kerala | https://lsgkerala.gov.in/index.php/en/public-grievance-redressal-mechanism | HTML | Procedure (general LSGD-wide, not city-specific) | RAG | B |
| Kerala | Kochi | All services (state appellate escalation) | Chief Minister's Public Grievance Redressal Cell (CMPGRC) reference | Government of Kerala | (referenced via search summary of Kochi Corporation grievance escalation; no independently confirmed CMPGRC URL surfaced in this pass) | — | Escalation authority name only | RAG | B |
| Kerala | Roads (state-wide, jurisdiction-split reference) | Roads & Potholes | PWD4U app listing | Public Works Department, Govt. of Kerala (per Play Store listing description) | https://play.google.com/store/apps/details?id=com.iroads.pwd.pwd4u&hl=en_IN | App store listing | Channel (state PWD road-defect reporting) | RAG | B |
| Kerala | (national, indexes Kerala datasets) | Waste & Sanitation | kerala.data.gov.in OGD portal | Open Government Data (OGD) Platform India — Kerala instance | https://kerala.data.gov.in/ | Dataset portal | Various structured datasets | Structured/SQL | C |
| Kerala | Ernakulam | (reference only, context on state watchdog body) | Suchitwa Mission — Waste management rules | Suchitwa Mission (Technical Support Group under LSGD; domain suchitwamission.org is not independently confirmed as an official .gov.in property in this pass) | https://suchitwamission.org/ | HTML | Policy context | reference only | D |
| Kerala | Kochi | (reference only, not verified fact source) | Brahmapuram fire coverage / Kerala HC observations | theprint.in, downtoearth.org.in, onmanorama.com (news, third-party) | https://www.onmanorama.com/news/kerala/2023/03/14/brahmapuram-fire-waste-dumping-yard-kochi.html | HTML | Context on Kochi Corp.'s waste-management enforcement history — NOT a procedural/SLA fact source | reference only | D |
| Kerala | (state-wide) | (reference only, context) | Waste Management in Urban Local Bodies (audit report) | Comptroller and Auditor General of India (CAG) | https://cag.gov.in/webroot/uploads/download_audit_report/2022/Full-Report---Waste-Management-in-Urban-Local-Bodies---English-06502eef24d3134.31315455.pdf | PDF | Policy/compliance audit context, not citizen procedure | reference only | D |

---

## Full records

### Record: Kerala-Kochi-Waste-SolidWasteManagement
```
service_id: kl-kochi-waste-solid-waste-management
service_name: Waste & Public Sanitation
sub_service: Solid waste collection, disposal, septage management
problem_type: garbage_collection

state: Kerala
district: Ernakulam
city: Kochi
municipality: Kochi Municipal Corporation (Cochin Corporation)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Health Department — the corporation's own website structure groups solid waste management under Health, and search summary describes the Health Inspector / Junior Health Inspector as enforcing waste-management-operation regulations.
authority: Kochi Municipal Corporation (Cochin Corporation)
officer_designation: Health Inspector / Junior Health Inspector — named as enforcement roles per search summary; not independently confirmed via direct fetch of an official org-chart document.

description: Cochin Corporation publishes a dedicated Solid Waste Management page and a List of Empanelment Agencies for Solid Waste Management (i.e. contracted service providers), plus a draft Septage Management Byelaw covering septic-tank/septage handling rules. The corporation has historically operated the Brahmapuram waste-processing site — its regulatory and legal history (Kerala HC observations on rule violations, a 2023 landfill fire, an NGT-ordered environmental-compensation order) is well documented in third-party/news sources but is NOT used here as a citizen-complaint-procedure fact, only logged for context in the summary table (quality D).
procedure: Register a complaint via My Kochi (mykochi.lsgkerala.gov.in) or the Public Grievance Cell form; empanelled agencies handle actual collection/processing per the corporation's published list.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: My Kochi app/portal (mykochi.lsgkerala.gov.in), Public Grievance Cell online form, corporation phone 91-484-2369007
contact_information: 91-484-2369007 (general corporation contact per search summary, not confirmed as waste-specific)

escalation_procedure: If concerns are not resolved satisfactorily, escalate to the Appellate Authority of the Urban Development Department via the Chief Minister's Public Grievance Redressal Cell (CMPGRC), Government of Kerala — per search summary of Kochi Corporation's general escalation description; not independently confirmed as waste-specific, and no direct CMPGRC URL was confirmed in this pass.
escalation_authority: Appellate Authority, Urban Development Department, Govt. of Kerala (via CMPGRC) — general escalation path, not waste-specific

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Solid Waste Management
source_url: https://kochicorporation.lsgkerala.gov.in/en/solid-waste-management/368
source_type: govt_portal
source_organization: Kochi Municipal Corporation (Cochin Corporation)

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A for the dedicated, corporation-specific department page (not a generic complaint form) hosted on the corporation's own lsgkerala.gov.in subdomain. The Brahmapuram fire/regulatory-violation history is a major, widely-reported real event but is deliberately excluded from the procedural fields above — it belongs in policy-context research, not a citizen-facing SLA/procedure record, and none of the sources reporting it are government-official per the 00_README.md rubric (news outlets, an NGO-adjacent academic paper, a think-tank article).
```

### Record: Kerala-Kochi-Water-Drainage
```
service_id: kl-kochi-water-drainage
service_name: Water & Drainage
sub_service: Water leak, water shortage, water-charge issues, Jal Jeevan Mission-related, sewerage
problem_type: no_low_water_supply

state: Kerala
district: Ernakulam
city: Kochi
municipality: Water supply and sewerage in Kochi is handled by the Kerala Water Authority (KWA), a state-level statutory body — this is a clear, confirmed jurisdiction split from the Kochi Municipal Corporation itself, distinct from the corporation's own Septage Management Byelaw (which appears to cover on-site septic-tank rules within corporation limits, a narrower scope than KWA's piped supply/sewerage mandate).
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Kerala Water Authority (KWA) — state-wide nodal agency for drinking water supply and sewerage
authority: Kerala Water Authority
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: KWA operates "Aqualoom," a web-based 24/7 online consumer-complaint system covering water leak, water shortage, water-charge-related, Jal Jeevan Mission-related, and sewerage complaints, plus a general toll-free helpline. The Kerala Water Supply Infrastructure Improvement Project (KUWSIP) is described in search summary as targeting both Kochi and Thiruvananthapuram Corporations for rehabilitation of aging production facilities and leaky distribution networks, aiming at 24x7 supply via reduced non-revenue water (NRW) — this indicates KWA's mandate explicitly spans both researched Kerala cities, not just Kochi.
procedure: Register a complaint (with photos/videos supported) via Aqualoom (aqualoom.kwa.kerala.gov.in) or call the toll-free helpline.
required_information: Photos/videos of the issue where relevant (per Aqualoom's described complaint-registration capability)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Aqualoom online complaint system (aqualoom.kwa.kerala.gov.in), toll-free 1916, phone +91-471-2738300
contact_information: Toll-free 1916 / +91-471-2738300

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Consumer Grievances — KWA
source_url: https://kwa.kerala.gov.in/en/consumer-grievances/
source_type: grievance_portal
source_organization: Kerala Water Authority

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city (KWA's own scope is state-wide, but this record's geographic_scope reflects that Kochi is the specific city under research here)
notes: This is the clearest, most confidently-confirmed authority-jurisdiction split found in this entire 3-state research pass — Kerala's water supply/sewerage sits with a distinct state statutory body (KWA), not the municipal corporation, matching exactly the caution flagged in 01_service_data_requirements.md as "sometimes a separate state-level Water Board/Jal Board with its own jurisdiction." Recent pipeline-burst/tank-collapse incidents in Kochi (Mullassery Canal Road, Thammanam) were found in news-source search results and are NOT logged as facts here — they are infrastructure-condition news, not an official procedural fact, and are excluded per the 00_README.md rule against citing news sources as fact.
```

### Record: Kerala-Kochi-Roads-Streetlight
```
service_id: kl-kochi-roads-streetlight
service_name: Roads & Potholes / Streetlights
sub_service: Road maintenance, pothole reporting, streetlight maintenance (combined record — both categories were equally thin for Kochi in this pass)
problem_type: potholes; streetlight_not_working

state: Kerala
district: Ernakulam
city: Kochi
municipality: Kochi Municipal Corporation (Cochin Corporation)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Engineering Department (corporation's own site confirms an "Engineering" section exists, alongside Town Planning, Health, Revenue, Accounts, and Council Section — but the Engineering page itself returned minimal indexed content in this pass)
authority: Kochi Municipal Corporation (for municipal roads/streetlights); Public Works Department, Kerala (PWD4U app) for state-PWD-classified roads within city limits — jurisdiction split not independently confirmed as applying inside Kochi specifically, only inferred from PWD4U being a state-wide tool.
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: The corporation's Engineering department is confirmed to exist via its own website structure, but no Kochi-specific dedicated road-maintenance or streetlight page (comparable to Thiruvananthapuram's, see below) was surfaced in this pass. PWD4U, a Government of Kerala digital initiative, allows citizens to geotag and report road defects statewide, with automatic routing to PWD and status tracking — its applicability to Kochi's own municipal (non-PWD) roads was not confirmed.
procedure: General complaints likely route via My Kochi / Public Grievance Cell (as with other categories); PWD4U specifically for PWD-classified roads.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: My Kochi app/portal (general channel, not roads/streetlight-specific); PWD4U app (state PWD roads only)
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Engineering — Cochin Corporation
source_url: https://kochicorporation.lsgkerala.gov.in/en/engineering
source_type: govt_portal
source_organization: Kochi Municipal Corporation (Cochin Corporation)

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: This is the thinnest record in the Kerala file. IMPORTANT — do NOT assume Kochi's streetlights are handled by KSEB (Kerala State Electricity Board) just because that split was confirmed for Thiruvananthapuram below; per 00_README.md rule 3 ("geography is never assumed to transfer"), this must be checked independently for Kochi. No Kochi-specific streetlight-authority statement was found in this pass — flagged as a priority follow-up question given how significant the TVM finding was.
```

### Record: Kerala-Thiruvananthapuram-Waste-SolidWasteManagement
```
service_id: kl-thiruvananthapuram-waste-solid-waste-management
service_name: Waste & Public Sanitation
sub_service: Solid waste collection, disposal, conservancy services
problem_type: garbage_collection

state: Kerala
district: Thiruvananthapuram
city: Thiruvananthapuram
municipality: Thiruvananthapuram Municipal Corporation (TMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Health Department, headed by a Corporation Health Officer (CHO)
authority: Thiruvananthapuram Municipal Corporation
officer_designation: Corporation Health Officer (CHO) heads the department; assisted by a Veterinary Surgeon, Health Supervisors, 23 Health Inspectors, and 71 Junior Health Inspectors (JHI) — per TMC's own organisational-structure description.

description: TMC's Health Department is responsible for conservancy service, sanitation facilities, solid waste management, and other public-health duties. TMC publishes a dedicated Solid Waste Management page, a separate "Solid Waste Disposal" page, and a "Capital city, Clean city" page listing waste-collection centres and a collection calendar. The state-wide Kerala Solid Waste Management Project (World Bank/AIIB-supported) is referenced as strengthening institutional/service-delivery systems, applicable to TMC among other ULBs.
procedure: Report via Smart Trivandrum portal (smarttvm.tmc.lsgkerala.gov.in/complaint/report), which explicitly supports reporting waste dumping and other waste-related issues alongside booking drinking-water/septage tankers and applying for bio-compost schemes.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — Smart Trivandrum's own marketing/description states complaints are "closed within service-level deadlines with full audit trail," but the specific day-count for waste complaints was not surfaced/fetched in this pass.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Smart Trivandrum portal (complaint reporting, waste-collection-centre info, bio-compost scheme application, waste-dumping reporting), TMC's own Solid Waste Management/Disposal pages
contact_information: Corporation Office, Vikas Bhavan P.O., Thiruvananthapuram, 695033; email mycitybeautifulcity@gmail.com; phone 9496434488

escalation_procedure: ESCALATION INFORMATION NOT FOUND specifically for waste (see the AllServices record below for TMC's general Engineering-wing escalation chain, which does not clearly apply to the Health-department-run waste service)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Solid Waste Management — City Of Thiruvananthapuram
source_url: https://tmc.lsgkerala.gov.in/en/solid-waste-management
source_type: govt_portal
source_organization: Thiruvananthapuram Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: TMC's Health department org-chart detail (CHO + 23 Health Inspectors + 71 JHIs) is unusually specific for a search-summary result — flagged as a strong, specific, likely-genuine fact worth prioritizing for direct-fetch confirmation, since exact headcounts of this kind are not the sort of thing search engines typically fabricate/hallucinate at this level of detail, but per this research program's rules it still cannot be marked "verified" without an actual page read.
```

### Record: Kerala-Thiruvananthapuram-Roads-Streetlight
```
service_id: kl-thiruvananthapuram-roads-streetlight
service_name: Roads & Potholes / Streetlights
sub_service: Road/drain construction and maintenance; streetlight maintenance (KSEB jurisdiction split)
problem_type: potholes; streetlight_not_working

state: Kerala
district: Thiruvananthapuram
city: Thiruvananthapuram
municipality: Thiruvananthapuram Municipal Corporation (TMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Engineering Department, headed by a Superintending Engineer, assisted by 3 Executive Engineers, 4 Assistant Executive Engineers, and 40 Assistant Engineers — per TMC's own organisational description.
authority: Thiruvananthapuram Municipal Corporation for roads/drains; Kerala State Electricity Board (KSEB) for streetlight maintenance itself — TMC's role for streetlights is limited to supplying spare parts, per TMC's own Engineering-department description. This is a genuine, city-confirmed authority split, distinct from the general municipal-corporation-handles-everything assumption.
officer_designation: Executive Engineer (EE) is the designated Nodal Officer in the Corporation Office for service-related grievances, per TMC's search-summarized description. Escalation workflow named as EE → AEE (Assistant Executive Engineer) → AE (Assistant Engineer) → Concerned Overseer.

description: TMC's Engineering Department's major duties include construction and maintenance of roads, drains, and other public works. Street lighting itself is carried out by KSEB (the state electricity distribution utility), with the corporation's role limited to supplying spare parts for streetlight fixtures — meaning a citizen streetlight complaint in Thiruvananthapuram may need to route to KSEB rather than (or in addition to) TMC, unlike a typical municipal streetlight complaint.
procedure: Report road/drain issues to the Engineering Department, with Executive Engineer as Nodal Officer; if unresolved, escalation follows EE → AEE → AE → Overseer (direction of escalation, i.e. which end is "first contact" vs. "final escalation," was not disambiguated by the search summary — treat with caution). Streetlight-specific issues may require contacting KSEB directly given the corporation's limited spare-parts-only role, though the exact citizen-facing streetlight-complaint channel (TMC vs. KSEB vs. both) was not confirmed in this pass.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Smart Trivandrum portal (smarttvm.tmc.lsgkerala.gov.in) — explicitly described as supporting reports "from potholes to flickering lights" and tracking streetlights; TMC Engineering Department directly; KSEB (for streetlight maintenance itself, per the jurisdiction split noted above)
contact_information: Corporation Office, Vikas Bhavan P.O., Thiruvananthapuram, 695033; email mycitybeautifulcity@gmail.com; phone 9496434488

escalation_procedure: EE (Nodal Officer for service-related grievances) → AEE → AE → Concerned Overseer, per TMC's Engineering-department description (search summary; exact escalation direction and any day-count triggers not independently confirmed).
escalation_authority: Executive Engineer → Assistant Executive Engineer → Assistant Engineer → Overseer, TMC Engineering Department

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Engineering — City Of Thiruvananthapuram
source_url: https://tmc.lsgkerala.gov.in/en/engineering
source_type: govt_portal
source_organization: Thiruvananthapuram Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: The KSEB-handles-streetlight-maintenance / corporation-supplies-spare-parts-only split is the single most significant and specific jurisdiction-split finding in this Kerala pass, and is exactly the kind of DISCOM-vs-municipality split flagged as a real possibility in 01_service_data_requirements.md's Streetlights section ("in smaller ULBs the responsibility can sit with the state electricity distribution company (DISCOM) rather than the municipality") — notable that it applies even in a state capital, not just a "smaller ULB." This should NOT be assumed to transfer to Kochi (see the Kochi Roads/Streetlight record above, which explicitly flags this as unconfirmed for Kochi) or to any other Kerala ULB without independent confirmation.
```

### Record: Kerala-Thiruvananthapuram-AllServices-SmartTrivandrum
```
service_id: kl-thiruvananthapuram-all-smart-trivandrum
service_name: (cross-cutting — integrated civic services portal covers all 4 categories)
sub_service: Pothole reporting, streetlight tracking, waste-dumping reporting, water/septage tanker booking, general complaint tracking
problem_type: multiple

state: Kerala
district: Thiruvananthapuram
city: Thiruvananthapuram
municipality: Thiruvananthapuram Municipal Corporation (TMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Cross-departmental — Smart Trivandrum is described as TMC's own integrated civic-services portal, not tied to a single department.
authority: Thiruvananthapuram Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Smart Trivandrum is TMC's official civic-services portal, allowing citizens to book drinking-water and septage tankers, lodge complaints ("from potholes to flickering lights"), track streetlights, pay fines, apply for bio-compost schemes, report waste dumping, and follow municipal vehicles in real time. Per its own description, complaints are "closed within service-level deadlines with full audit trail" — a genuine claim of an internal SLA system, though the specific deadline figures per complaint category were not surfaced/fetched in this pass.
procedure: Submit a complaint via smarttvm.tmc.lsgkerala.gov.in/complaint/report; track status via a reference ID (a sample tracked-complaint URL pattern was observed in search results, confirming a working status-tracking feature exists).
required_information: NOT FOUND IN OFFICIAL SOURCE (specific form fields not extracted from search snippets)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — the portal's own description claims complaints are closed "within service-level deadlines," implying a real internal SLA system exists, but the actual day-count figures per category were not confirmed via direct fetch in this pass. Do not treat "service-level deadlines" as a specific number.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Smart Trivandrum web portal (smarttvm.tmc.lsgkerala.gov.in)
contact_information: NOT FOUND IN OFFICIAL SOURCE (portal-specific contact channel not surfaced; general TMC contact details are in the AllServices/Engineering records above)

escalation_procedure: ESCALATION INFORMATION NOT FOUND (portal-specific)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Smart Trivandrum — Civic Services Portal
source_url: https://smarttvm.tmc.lsgkerala.gov.in/
source_type: grievance_portal
source_organization: Thiruvananthapuram Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A — this is a genuinely integrated, city-specific, all-4-category digital civic-services platform hosted on TMC's own subdomain, the single richest cross-cutting channel found across all three states in this research pass. It is the strongest direct-fetch priority in this file: if its complaint-category list and per-category SLA figures can be confirmed by an actual page read, this one portal could supply real (not NOT-FOUND) sla/response_time values for all 4 service categories in Thiruvananthapuram at once. A scam-check/reputation-checker site (scamadviser.com) also indexed this domain, which is a routine indexing pattern for any live domain and is not treated as a negative signal here — the domain's ownership by TMC (a .lsgkerala.gov.in subdomain) is the operative fact.
```

### Record: Kerala-Thiruvananthapuram-AllServices-GrievanceMechanism
```
service_id: kl-thiruvananthapuram-all-grievance-mechanism
service_name: (cross-cutting — general grievance mechanism)
sub_service: General civic grievance registration and escalation
problem_type: multiple

state: Kerala
district: Thiruvananthapuram
city: Thiruvananthapuram
municipality: Thiruvananthapuram Municipal Corporation (TMC)
zone: TMC operates through 11 zonal offices (Fort, Kazhakkuttom, Attipra, Sreekaryam, Ulloor, Kudappanakkunnu, Vattiyoorcavu, Nemom, Vizhinjam, Thiruvallom, Kadakompally), per TMC's own contact-information description.
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (specific to grievance handling; see the Engineering-department-specific EE→AEE→AE→Overseer chain in the Roads/Streetlight record above, which may or may not be the same as the general mechanism)
authority: Thiruvananthapuram Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE (beyond the Engineering-specific Executive Engineer nodal-officer role noted separately)

description: TMC operates an Online Public Grievance Redressal System, with a dedicated "Public Grievance Cell" page and a separate "Grievances Redressal Mechanism" page on its own website. The corporation additionally maintains a dedicated grievance-cell phone line distinct from its general office numbers.
procedure: Lodge a grievance via TMC's online Public Grievance Redressal System, or contact the Corporation Office / relevant zonal office directly.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online Public Grievance Redressal System (tmc.lsgkerala.gov.in), 11 zonal offices, dedicated grievance-cell phone
contact_information: Corporation Office (Palayam) 0471-2320821 / 2320922 / 2320795 / 2320597 / 2320047; email tvpmcorpn@gmail.com; dedicated Grievance Cell phone 0471-2534474

escalation_procedure: ESCALATION INFORMATION NOT FOUND at the general (non-Engineering-specific) level
escalation_authority: NOT FOUND IN OFFICIAL SOURCE (general); see Kochi's record above for the state-wide CMPGRC fallback channel description, which was found tied to Kochi's search results specifically but likely applies statewide including to TMC — not independently confirmed for TVM in this pass, so not asserted here.

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Grievances Redressal Mechanism — City Of Thiruvananthapuram
source_url: https://tmc.lsgkerala.gov.in/en/grievances-redressal-mechanism/1749
source_type: grievance_portal
source_organization: Thiruvananthapuram Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: TMC publishes two contact phone-number sets in different search results (a 5-number Corporation Office block from one query, a single "9496434488" number from another) — these were not reconciled in this pass and both are logged (Corporation Office numbers here; the 9496434488 number in the waste/roads records above, where it appeared attached to the smarttvm/engineering context) rather than picking one arbitrarily. Direct-fetch follow-up should confirm which number(s) are current/correct.
```

---

## Coverage notes for Kerala

- **Best-covered service:** Waste & Sanitation for both cities, and — more
  notably — the cross-cutting Smart Trivandrum portal, which is the
  single richest all-in-one civic-services source found across the whole
  3-state research pass (Uttar Pradesh + West Bengal + Kerala). Kerala's
  shared `*.lsgkerala.gov.in` domain family for ULB websites gave this
  state the highest domain-confidence hit rate overall — most full
  records here reached quality A.
- **Weakest-covered service:** Roads & Potholes and Streetlights for
  Kochi specifically — the corporation's own Engineering page returned
  minimal indexed content, in sharp contrast to Thiruvananthapuram's much
  richer Engineering-department description (staffing structure,
  escalation chain, and the KSEB streetlight split).
- **Jurisdiction-split findings — two genuine, well-corroborated ones**:
  1. **Water & Drainage**: Kerala Water Authority (KWA), a state
     statutory body, handles water supply/sewerage for both Kochi and
     Thiruvananthapuram — not the municipal corporations directly. This
     was independently corroborated across two separate search queries
     (KWA's own consumer-grievances page, and the KUWSIP infrastructure
     project description naming both corporations as beneficiaries).
  2. **Streetlights (Thiruvananthapuram only)**: streetlight maintenance
     itself is carried out by KSEB (Kerala State Electricity Board), with
     TMC's Engineering Department limited to supplying spare parts. This
     was found specifically for Thiruvananthapuram and — per
     `00_README.md` rule 3 — is explicitly NOT assumed to apply to Kochi,
     where the equivalent question remains unanswered (flagged as
     `NOT FOUND IN OFFICIAL SOURCE` with a specific warning against
     assuming transfer, in the Kochi Roads/Streetlight record).
- **Third city**: only 2 cities (Kochi, Thiruvananthapuram) were
  researched for Kerala rather than 3 — a comparison search for
  Kozhikode did surface an official `kozhikodecorporation.lsgkerala.gov.in`
  Public Grievance Cell page (logged only in passing, not built into a
  full record set), suggesting a third Kerala city could be added in a
  future pass with likely-good domain coverage, but was out of scope for
  this pass given the assignment's 1–3-city guidance and the depth
  already achieved for the first two.
- **Brahmapuram / waste-crisis context**: Kochi's Brahmapuram
  waste-processing site has a well-documented history of regulatory
  violations, a major 2023 fire, and an NGT environmental-compensation
  order — all confirmed only through news/NGO/academic sources (not
  government-official per the source-quality rubric) and therefore
  excluded from every procedural field, logged only as quality-D
  reference rows in the summary table. This is a case where a genuinely
  important real-world fact was deliberately left out of the structured
  fields because no official source stating it was found in this pass —
  exactly the intended behavior per `00_README.md` rule 1.
- Nothing in this file should be read as confirming exact SLA numbers —
  even Smart Trivandrum's own claim of "service-level deadlines with full
  audit trail" was left as `SLA NOT FOUND` because the actual deadline
  figures per category were not surfaced/fetched in this pass, per the
  same discipline applied throughout this research program.
