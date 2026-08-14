# Uttar Pradesh — Official Source Inventory

**Cities researched:** Lucknow (LMC), Varanasi (NNVNS), Bareilly (Nagar Nigam
Bareilly)
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
> below. Several search queries returned mixed result sets combining
> official domains (`.gov.in`, `.up.nic.in`, `.org.in`) with third-party
> aggregators (complainthub.org, consumercomplaints.in) in the *same*
> synthesized answer — where a specific figure's origin domain could not
> be cleanly isolated, it was treated conservatively as unverified and
> pushed to `notes` rather than into `sla`/`escalation_procedure`.

---

## Summary table

| State | City | Service | Source | Authority | URL | Format | Data Available | RAG or SQL | Quality |
|---|---|---|---|---|---|---|---|---|---|
| Uttar Pradesh | Lucknow | All services | Official website | Lucknow Municipal Corporation (LMC) | https://lmc.up.nic.in/ | HTML | Directory, leadership, contact | RAG | B |
| Uttar Pradesh | Lucknow | All services (grievance mechanism) | Grievances for Lucknow Municipal Corporation | National Government Services Portal (Govt. of India) | https://services.india.gov.in/service/detail/grievances-for-lucknow-municipal-corporation-uttar-pradesh-1 | HTML | Procedure, channels | RAG | B |
| Uttar Pradesh | (state-wide, applies to Lucknow/Varanasi/Bareilly ULBs) | All services | e-NagarSewa UP — ULB Integrations / Online Complaint | Directorate of Local Bodies, Govt. of Uttar Pradesh | https://e-nagarsewaup.gov.in/ | Web portal | Procedure, escalation | RAG | B |
| Uttar Pradesh | (state-wide) | All services | e-NagarSewa Online Complaint form | Directorate of Local Bodies, Govt. of Uttar Pradesh | http://e-nagarsewaup.gov.in/ulbapps/Grievance/onlineComplaint.jsp | Web form | Channel | RAG | B |
| Uttar Pradesh | Lucknow | Waste & Sanitation | LMC toll-free/WhatsApp helpline (via LMC's own contact channels, referenced through Swachhata-MoHUA app description) | Lucknow Municipal Corporation | https://lmc.up.nic.in/ | HTML | Channel, department | RAG | B |
| Uttar Pradesh | Lucknow | Water & Drainage | Lucknow Jal Sansthan online complaint system | Lucknow Jal Sansthan / Jal Kal Vibhag | http://www.jklmc.in/ (referenced; not independently opened) | Web app | Procedure, channel | RAG | B |
| Uttar Pradesh | Lucknow | Water & Drainage (state utility, general) | Official Website of Jal Nigam, Uttar Pradesh | Uttar Pradesh Jal Nigam (Urban) | https://jn.upsdc.gov.in/ | HTML | Authority (state-level bulk supply/infra body) | RAG | B |
| Uttar Pradesh | Lucknow | Streetlight / Smart City | Integrated Command and Control Centre (ICCC) — Lucknow | Smart Cities Mission, Govt. of India | https://iccc.smartcities.gov.in/icc/city-details/8b0afddce19abe9d79637044539da127 | HTML | Channel (ICCC-integrated grievance/monitoring) | RAG | B |
| Uttar Pradesh | Lucknow | Streetlight / Smart City | Lucknow Smart City Portal | Lucknow Smart City Ltd. / Lucknow Municipal Corporation | https://lucknowsmartcity.com/ | HTML | Channel, dashboard reference | RAG | B |
| Uttar Pradesh | Varanasi | All services | Home — Varanasi Nagar Nigam | Varanasi Nagar Nigam (NNVNS) | https://nnvns.org.in/ | HTML | Directory, procedure | RAG | B |
| Uttar Pradesh | Varanasi | All services (departments) | Departments — Varanasi Nagar Nigam | Varanasi Nagar Nigam (NNVNS) | https://nnvns.org.in:449/nnvns/index.php?option=com_content&view=article&id=57&Itemid=396&lang=en | HTML | Jurisdiction (department list incl. Street Light) | RAG | B |
| Uttar Pradesh | Varanasi | Water & Drainage | Jalkal Varanasi Public Grievance and Redressal System (PGR) | Jal Kal Vibhag, Varanasi Nagar Nigam | http://www.jalkalvaranasi.org/pgr/comlaint1.php | Web app | Channel, procedure | RAG | B |
| Uttar Pradesh | Varanasi | All services (grievance escalation) | How to lodge a Grievance? | District Varanasi, Government of Uttar Pradesh | https://varanasi.nic.in/service/how-to-lodge-a-grievance/ | HTML | Procedure, escalation | RAG | B |
| Uttar Pradesh | Bareilly | All services (citizen charter) | Citizen Charter — Nagar Nigam Bareilly | Bareilly Nagar Nigam | https://nagarnigambareilly.com/citizen-charter.php | HTML | Procedure, service standards | RAG | B |
| Uttar Pradesh | Bareilly | All services (grievance) | Grievances Redressal System — Nagar Nigam Bareilly | Bareilly Nagar Nigam | https://nagarnigambareilly.com/addcomplaint.php | Web form | Channel | RAG | B |
| Uttar Pradesh | Bareilly | Waste & Sanitation | Door to Door Collection (MSW) — official PDF | Bareilly Nagar Nigam | https://nagarnigambareilly.com/Download/DOOR_TO_DOOR_COLLECTION.pdf | PDF | Procedure, service description | RAG | B |
| Uttar Pradesh | Bareilly | Waste & Sanitation | City Sanitation Plan for Bareilly | Bareilly Nagar Nigam | https://nagarnigambareilly.com/Download/CITY_SANITATION_PLAN.pdf | PDF | Policy, service description | RAG | B |
| Uttar Pradesh | Bareilly | All services (grievance) | Grievances for Bareilly Municipal Corporation | National Government Services Portal (Govt. of India) | https://services.india.gov.in/service/detail/grievances-for-bareilly-municipal-corporation-uttar-pradesh-1 | HTML | Procedure, channels | RAG | B |
| Uttar Pradesh | Lucknow | Waste & Sanitation | Waste Collection Vehicle Data: Lucknow: 2019 | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | https://www.data.gov.in/resource/waste-collection-vehicle-data-lucknow2019 | Dataset | Collection vehicle counts/capacity | Structured/SQL | C |
| Uttar Pradesh | Prayagraj | Waste & Sanitation | Solid Waste Management-Efficiency: Prayagraj: 2018 | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | https://www.data.gov.in/resource/solid-waste-management-efficiency-prayagraj-2018 | Dataset | Source segregation, D2D efficiency, bin placement | Structured/SQL | C |
| Uttar Pradesh | Varanasi | Waste & Sanitation | Solid Waste Disposal in Varanasi: 2018 | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | https://www.data.gov.in/resource/solid-waste-disposal-varanasi-2018 | Dataset | Waste disposal figures | Structured/SQL | C |
| Uttar Pradesh | Kanpur Nagar | Waste & Sanitation | Solid Waste Management: Kanpur Nagar (catalog) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | https://www.data.gov.in/catalog/solid-waste-management-kanpur-nagar | Dataset (catalog) | Source segregation, D2D efficiency, vehicle capacity | Structured/SQL | C |
| Uttar Pradesh | Lucknow | (reference only, not verified fact source) | LMC — How to File a Complaint to Lucknow Nagar Nigam? | complainthub.org (third-party) | https://complainthub.org/lmc-lucknow/ | HTML | Aggregated complaint-channel info, unverifiable claims | reference only | D |
| Uttar Pradesh | Varanasi | (reference only, not verified fact source) | Varanasi Nagar Nigam (NNVNS): How to File a Complaint? | complainthub.org (third-party) | https://complainthub.org/varanasi-nagar-nigam-nnvns-help/ | HTML | Aggregated complaint-channel info | reference only | D |
| Uttar Pradesh | (state-wide) | (reference only, not verified fact source) | E-NagarSewa UP help guide | complainthub.org (third-party) | https://complainthub.org/e-nagarsewa-up-help/ | HTML | Unverified "15-day escalation" figure, procedure summary | reference only | D |
| Uttar Pradesh | Lucknow | (reference only, not verified fact source) | How to Report Garbage in Lucknow | trackyourgarbage.com (third-party) | https://trackyourgarbage.com/2026/05/07/how-to-report-garbage-in-lucknow/ | HTML | Unverified procedure claims | reference only | D |

---

## Full records

### Record: UttarPradesh-Lucknow-Waste-GarbageCollection
```
service_id: up-lucknow-waste-garbage-collection
service_name: Waste & Public Sanitation
sub_service: Garbage collection / missed collection, street cleanliness
problem_type: garbage_collection

state: Uttar Pradesh
district: Lucknow
city: Lucknow
municipality: Lucknow Municipal Corporation (LMC) / Lucknow Nagar Nigam
zone: NOT FOUND IN OFFICIAL SOURCE
ward: Swachhata-MoHUA app complaints are reportedly forwarded to the "sanitary inspector of the ward" per search summary — ward-level routing exists but no specific ward document surfaced.

department: Cleanliness, Sanitation, and Solid Waste Management (named as a civic service category under LMC per search summary; exact internal department name/officer not confirmed on an official page in this pass)
authority: Lucknow Municipal Corporation
officer_designation: Sanitary Inspector (per ward) — reported via search summary describing the Swachhata-MoHUA app's routing, not confirmed by direct fetch of an LMC document.

description: LMC accepts garbage/sanitation complaints via toll-free helpline, WhatsApp, e-mail, its emergency control room (HQ and Zonal Offices), and the national Swachhata-MoHUA app (which forwards city complaints to LMC).
procedure: File online to the nodal officer of the relevant LMC department, via toll-free/WhatsApp number, or via the Swachhata app; the Swachhata app additionally geo/ward-routes the complaint.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Toll-free helpline 1533 / +915222289782, WhatsApp +915222289782, LMC emergency control room (HQ + Zonal Offices), Swachhata-MoHUA app
contact_information: Toll-free 1533 / +915222289782 (also serves as WhatsApp number per search summary)

escalation_procedure: ESCALATION INFORMATION NOT FOUND for Lucknow-specific waste complaints in this pass (see the state-wide e-NagarSewa UP 3-stage process noted in the Lucknow-AllServices context below, which likely applies but was not confirmed tied to this specific service page).
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: LUCKNOW NAGAR NIGAM (official website) — supplemented by search-summary description of Swachhata app routing
source_url: https://lmc.up.nic.in/
source_type: govt_portal
source_organization: Lucknow Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: The 1533 toll-free number and WhatsApp channel were reported consistently across the search summary but need direct confirmation on an official LMC page — the search result mixed lmc.up.nic.in with third-party aggregator content, so exact phrasing could not be isolated to the official domain alone.
```

### Record: UttarPradesh-Lucknow-Water-Drainage
```
service_id: up-lucknow-water-drainage
service_name: Water & Drainage
sub_service: Water supply, pipeline leakage, sewage outflow, damaged manholes
problem_type: no_low_water_supply

state: Uttar Pradesh
district: Lucknow
city: Lucknow
municipality: Lucknow Municipal Corporation (LMC) — water/sewerage specifically administered by Lucknow Jal Sansthan (Jal Kal Vibhag), a distinct body from the general Nagar Nigam per search results.
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Lucknow Jal Sansthan (Jal Kal Vibhag) — this is a jurisdiction split worth flagging per 01_service_data_requirements.md's caution: water supply/sewerage in Lucknow appears to sit with Jal Sansthan rather than being a plain LMC department, though the exact legal/administrative relationship between LMC and Jal Sansthan was not confirmed in this pass.
authority: Lucknow Jal Sansthan
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Lucknow Jal Sansthan operates an online complaint system where residents upload photos of damaged manholes, pipelines, or sewage-outflow spots. Some old-city areas (Chowk, Sondhi Tola, Thakurganj, etc.) are reported to face unscheduled/inadequate supply, per search summary of secondary sources — not an official complaint statistic.
procedure: Log complaints via www.jklmc.in with photo uploads, or call the control room / alternate control room numbers.
required_information: Photo of the issue (damaged manhole/pipeline/sewage outflow), per search summary of the online system's description.
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online complaint system (jklmc.in), Control Room 81770 54003, Alternate Control Room 81770 54010
contact_information: Control Room 81770 54003 / Alternate Control Room 81770 54010

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Lucknow Jal Sansthan (jklmc.gov.in / www.jklmc.in — cached/mirrored search result; primary domain not independently confirmed to resolve)
source_url: http://www.jklmc.in/
source_type: govt_portal
source_organization: Lucknow Jal Sansthan

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: One search result surfaced "jklmc.gov.in" via a third-party mirror/status-checking site (jklmc.gov.in.usitestat.com) rather than the domain directly — treat the exact live domain (jklmc.gov.in vs www.jklmc.in) as unconfirmed until directly fetched. The water-vs-sewerage authority split (Jal Sansthan vs. LMC proper) should be prioritized for direct-fetch confirmation, per the cross-state caution in 01_service_data_requirements.md. Uttar Pradesh Jal Nigam (Urban), a separate state-level body (https://jn.upsdc.gov.in/), also appears in search results as relevant to bulk water infrastructure — its precise relationship to Lucknow's day-to-day complaint handling was not resolved in this pass.
```

### Record: UttarPradesh-Lucknow-Roads-Potholes
```
service_id: up-lucknow-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting, road damage
problem_type: potholes

state: Uttar Pradesh
district: Lucknow
city: Lucknow
municipality: Lucknow Municipal Corporation (LMC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (LMC Public Works/Engineering department name not confirmed on an official page in this pass)
authority: Lucknow Municipal Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: A "Lucknow 311" citizen-issue-reporting portal (lucknow.everythingcivic.com) and a "Lucknow-One" mobile app (published on Google Play/App Store, downloadable since July 2018) both surfaced in search results as citizen-facing infrastructure-reporting channels, but neither's direct government ownership/publisher chain could be confirmed as authoritative in this pass — the Play Store listing attributes the app to "Civic Solutions Pvt. Ltd." rather than to LMC or Lucknow Smart City directly, even though its stated purpose (community-leader/government issue resolution, GPS features) matches a municipal citizen app.
procedure: NOT FOUND IN OFFICIAL SOURCE (app-based reporting implied but exact steps not confirmed)
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: "Lucknow-One" app (Android/iOS, per app-store search results — official government ownership not independently confirmed); "Lucknow 311" web portal (lucknow.everythingcivic.com — a third-party civic-tech platform, not a lmc.up.nic.in or lucknowsmartcity.com domain)
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: (no single clean official-domain source found for this specific service in this pass)
source_url: https://lmc.up.nic.in/
source_type: govt_portal
source_organization: Lucknow Municipal Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Weakest-sourced Lucknow record in this pass — the two most-visible reporting channels found (Lucknow-One app, Lucknow 311) are both run through third-party civic-tech vendors ("Civic Solutions Pvt. Ltd.", "everythingcivic") rather than a domain that was clearly and directly confirmed as lmc.up.nic.in- or lucknowsmartcity.com-operated, so quality is capped at B pending direct verification of whether these are officially adopted/endorsed channels or independent products. Do not upgrade to A without confirming government ownership directly.
```

### Record: UttarPradesh-Lucknow-Streetlight
```
service_id: up-lucknow-streetlight
service_name: Streetlights
sub_service: Non-functioning streetlight, energy-efficiency monitoring
problem_type: streetlight_not_working

state: Uttar Pradesh
district: Lucknow
city: Lucknow
municipality: Lucknow Municipal Corporation (LMC) / Lucknow Smart City Ltd.
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (electrical/street-lighting department name not confirmed on an official page)
authority: Lucknow Municipal Corporation, via Integrated Command and Control Centre (ICCC) for monitoring
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Lucknow's Smart City ICCC includes a "Real Time Street Light ON/OFF Monitoring Dashboard," implemented as part of an energy-efficiency initiative that replaced sodium-vapor lights with smart LED lights (reported 50% energy-consumption reduction per search summary of the ICCC/Smart City brochure). A public grievance redressal call center is also set up at the ICCC covering city services generally.
procedure: NOT FOUND IN OFFICIAL SOURCE (dashboard appears to be for monitoring/energy-management rather than a citizen-facing complaint-filing tool specifically; whether citizens can report a non-working streetlight through this same ICCC channel was not confirmed)
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: ICCC public grievance call center (general, not confirmed streetlight-specific); Lucknow Smart City Portal
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Integrated Command and Control Centre (ICCC) — Lucknow
source_url: https://iccc.smartcities.gov.in/icc/city-details/8b0afddce19abe9d79637044539da127
source_type: smart_city_dataset
source_organization: Smart Cities Mission, Ministry of Housing & Urban Affairs (Govt. of India) — Lucknow city page

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: As anticipated in 01_service_data_requirements.md, this category is the thinnest for Lucknow — the ICCC dashboard is confirmed to exist via an official smartcities.gov.in city page, but whether it functions as a citizen complaint-intake channel (vs. purely internal monitoring) was not resolved in this pass.
```

### Record: UttarPradesh-Varanasi-AllServices-GrievanceSystem
```
service_id: up-varanasi-all-grievance-system
service_name: (cross-cutting — grievance mechanism covers all 4 categories)
sub_service: General civic grievance registration and escalation, incl. roads, water, streetlights, public toilets
problem_type: multiple (roads, water, streetlights, public toilets explicitly named as in scope per search summary)

state: Uttar Pradesh
district: Varanasi
city: Varanasi
municipality: Varanasi Nagar Nigam (VNN / NNVNS)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Multiple departments confirmed to exist under VNN per its own departments page, including Engineering, Street Light, and Sanitation.
authority: Varanasi Nagar Nigam
officer_designation: "Head (Deputy Municipal Commissioner) of the department" and "Nodal Officer of the Public Grievance Cell" are named as escalation-path roles per search summary — not independently confirmed by direct fetch of an official VNN document.

description: VNN operates an integrated grievance redressal mechanism covering civic-body services, public utilities (roads, water, streetlights, public toilets), and citizen-centric/trade-tax services. Complaints may also be routed through the state-wide e-NagarSewa UP portal. VNN's own citizen charter reportedly specifies a 3-level escalation structure.
procedure: Submit online or offline to the concerned VNN department; if unresolved at the initial stage, escalate to the next-level officer per the citizen charter's 3-level structure.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — VNN's citizen charter is referenced as defining a 3-level resolution structure, but specific day-counts per level were not surfaced/fetched in this pass.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online grievance portal (nnvns.org.in and/or e-nagarsewaup.gov.in), offline submission to VNN departments
contact_information: NNVNS office — Nagar Nigam Sigra, Varanasi, phone 0542-2221709

escalation_procedure: If unresolved at the initial stage, escalate to the Head (Deputy Municipal Commissioner) of the relevant department, then to the Nodal Officer of the Public Grievance Cell / Municipal Commissioner or Mayor — a 3-level structure per VNN's citizen charter (per search summary; day-counts and exact wording not independently confirmed).
escalation_authority: Department Head (Deputy Municipal Commissioner) → Public Grievance Cell Nodal Officer → Municipal Commissioner/Mayor, VNN

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Web Site of Varanasi Nagar Nigam / Departments — Varanasi Nagar Nigam
source_url: https://nnvns.org.in/
source_type: govt_portal
source_organization: Varanasi Nagar Nigam

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: nnvns.org.in uses a .org.in domain rather than .gov.in/.nic.in, but is consistently referenced across multiple independent search results (including varanasi.nic.in, an official district government site) as VNN's own website — treated as genuinely official per 00_README.md's "municipal corporation website" criterion, not downgraded to D. The departments page confirms a dedicated "Street Light" department exists, which is a useful, specific fact worth prioritizing for direct-fetch confirmation.
```

### Record: UttarPradesh-Varanasi-Water-Drainage
```
service_id: up-varanasi-water-drainage
service_name: Water & Drainage
sub_service: Water supply, sewer/drainage complaints, water-quality
problem_type: no_low_water_supply

state: Uttar Pradesh
district: Varanasi
city: Varanasi
municipality: Varanasi Nagar Nigam — water/sewerage specifically administered by Jal Kal Vibhag, Varanasi (a distinct sub-body per its own PGR system's naming), analogous to the Lucknow Jal Sansthan split noted above.
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Jal Kal Vibhag, Varanasi
authority: Jal Kal Vibhag, Varanasi (under Varanasi Nagar Nigam)
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Jal Kal Varanasi operates a dedicated "Public Grievance and Redressal System (PGR)" web application for water/sewerage complaints, separate from VNN's general grievance channel.
procedure: File via the Jal Kal Varanasi PGR web form.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Jal Kal Varanasi PGR web form (jalkalvaranasi.org/pgr/comlaint1.php)
contact_information: NOT FOUND IN OFFICIAL SOURCE (contact page exists at jalkalvaranasi.org/webpages.php?tag=contact but specific numbers were not surfaced in search results)

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Jalkal Varanasi Public Grievance and Redressal System (PGR)
source_url: http://www.jalkalvaranasi.org/pgr/comlaint1.php
source_type: grievance_portal
source_organization: Jal Kal Vibhag, Varanasi

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: The existence of a separate, dedicated water/sewerage PGR system (distinct from VNN's general grievance channel) is a clear water-vs-general jurisdiction split worth prioritizing for direct-fetch confirmation, consistent with 01_service_data_requirements.md's caution that this category's authority varies most across cities. jalkalvaranasi.org is not a .gov.in/.nic.in domain; treated as B (official-but-unconfirmed-TLD) rather than downgraded to D, since it consistently appears as Jal Kal Varanasi's own operational system across search results, not a third-party aggregator.
```

### Record: UttarPradesh-Bareilly-AllServices-CitizenCharter
```
service_id: up-bareilly-all-citizen-charter
service_name: (cross-cutting — citizen charter and grievance mechanism cover all 4 categories)
sub_service: General civic grievance registration; door-to-door waste collection; city sanitation planning
problem_type: multiple

state: Uttar Pradesh
district: Bareilly
city: Bareilly
municipality: Bareilly Nagar Nigam (Bareilly Municipal Corporation)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (specific department names not confirmed beyond the existence of a published Citizen Charter and a City Sanitation Plan)
authority: Bareilly Nagar Nigam
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Bareilly Nagar Nigam publishes a Citizen Charter describing service commitments, plus dedicated PDFs for door-to-door municipal solid waste (MSW) collection/transportation and a City Sanitation Plan. A 3-stage complaint-resolution process is referenced (matching the general Nagar Nigam/Nagar Palika Parishad structure used elsewhere in UP), and eNagarSewa UP plus the state-wide "Jansunwai-Samadhan" portal are both cited as filing channels for Bareilly.
procedure: File online via eNagarSewa UP (for ULB-specific civic complaints) or Jansunwai-Samadhan (for complaints against any state department/official generally); or use Bareilly Nagar Nigam's own online grievance form.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — search summary states Jansunwai-Samadhan complaints are "resolved within a specified time frame" but the specific day-count was not surfaced/fetched in this pass.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Bareilly Nagar Nigam online grievance form (nagarnigambareilly.com/addcomplaint.php), eNagarSewa UP, Jansunwai-Samadhan
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: ESCALATION INFORMATION NOT FOUND (the general 3-stage ULB structure referenced elsewhere in UP search results is expected to apply, per the pattern seen for Lucknow/Varanasi, but this was not confirmed tied specifically to a Bareilly document in this pass)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Welcome to Bareilly Nagar Nigam — Citizen Charter
source_url: https://nagarnigambareilly.com/citizen-charter.php
source_type: citizen_charter
source_organization: Bareilly Nagar Nigam

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: nagarnigambareilly.com is not a .gov.in/.nic.in domain and its footer/branding in one linked PDF search result referenced a third-party web-development vendor ("Pinnacle Web Solutions") — this raises a mild caution flag that the site, while presenting itself as and being widely linked-to as the Nagar Nigam's own portal, is vendor-hosted. It is treated as B (official-but-unconfirmed-independently) rather than downgraded to D, consistent with how other ULB-branded non-.gov.in domains (jalkalvaranasi.org, nnvns.org.in) were handled in this pass — but this domain in particular deserves a direct-fetch sanity check before production use, more so than the others.
```

---

## Coverage notes for Uttar Pradesh

- **Best-covered service:** Waste & Sanitation — consistent with the other
  states researched so far, this category has the most published material
  (dedicated PDFs for Bareilly's door-to-door collection and city
  sanitation plan, `data.gov.in` OGD datasets for Lucknow/Varanasi/
  Prayagraj/Kanpur waste-collection vehicles and efficiency).
- **Weakest-covered service:** Roads & Potholes for Lucknow specifically —
  the two most visible citizen-reporting channels found (Lucknow-One app,
  Lucknow 311) both route through third-party civic-tech vendors rather
  than a domain independently confirmed as government-operated, so this
  record could not be pushed past quality B/thin content. Streetlights
  remained the thinnest category state-wide otherwise, matching the
  expectation in `01_service_data_requirements.md`.
- **Water vs. general-civic jurisdiction split — a genuine, repeated
  finding**: both Lucknow (Jal Sansthan / Jal Kal Vibhag) and Varanasi
  (Jal Kal Vibhag, with its own separate PGR system at jalkalvaranasi.org)
  show water/sewerage being handled by a distinct sub-body with its own
  complaint channel, separate from the general Nagar Nigam grievance
  system — this matches the caution flagged in
  `01_service_data_requirements.md` and should be treated as confirmed
  for these two UP cities specifically (not assumed to extend to
  Bareilly, where this split was not surfaced).
- **Third city choice**: Bareilly was used instead of a larger city like
  Kanpur or Agra — Bareilly's own domain (nagarnigambareilly.com)
  surfaced a genuinely richer set of specific documents (citizen charter,
  door-to-door collection PDF, city sanitation plan PDF) than what came
  back for a comparable quick search on other UP Tier-2 cities, though
  the domain itself carries the caution noted in its record above.
- **State-wide layer**: Uttar Pradesh has a genuinely distinct two-tier
  state grievance-portal structure — e-NagarSewa UP (ULB/civic-service-
  specific, run by the Directorate of Local Bodies) versus Jansunwai-
  Samadhan (general state-department grievances, escalating up to the
  Chief Minister's Office) — both surfaced consistently across all three
  cities' searches and are logged as state-wide summary-table rows
  rather than duplicated into each city's full records.
- Nothing in this file should be read as confirming exact SLA numbers —
  every specific day-count claim found in this pass (e.g. "15 days" for
  e-NagarSewa escalation, Jansunwai's "specified time frame") traced back
  to either a mixed/ambiguous search-result attribution or a third-party
  aggregator, and is logged only in `notes` for context, never in the
  `sla`/`escalation_procedure` fields themselves.
