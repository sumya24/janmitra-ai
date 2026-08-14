# Karnataka — Official Source Inventory

**Cities researched:** Bengaluru (BBMP), Mysuru (MCC), Mangaluru (MCC)
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
| Karnataka | Bengaluru | Waste & Sanitation | Bruhat Bengaluru Mahanagara Palike Solid Waste Management Rules (bye-law) | BBMP, via India Code (Govt. of India legislative repository) | https://upload.indiacode.nic.in/showfile?actid=AC_KA_71_402_00007_14_1552388734165&type=rule&filename=bbmp_swm.pdf | PDF | Bye-law text: segregation duty, collection frequency, fines | RAG | A |
| Karnataka | Bengaluru | Waste & Sanitation | Fix My Street / Sahaaya complaint system | BBMP (Information Technology Dept.) | https://site.bbmp.gov.in/departmentwebsites/BBMPIT/fms.html | HTML | Channel, procedure | RAG | B |
| Karnataka | Bengaluru | Roads & Potholes | Pothole Fix / Fix My Street app | BBMP (Information Technology Dept.) | https://site.bbmp.gov.in/departmentwebsites/BBMPIT/Pothole%20Fix.html | HTML | Channel, procedure | RAG | B |
| Karnataka | Bengaluru | Water & Drainage | BWSSB — Bangalore Water Supply and Sewerage Board (official site) | BWSSB (state statutory board, NOT BBMP) | https://bwssb.karnataka.gov.in/english | HTML | Jurisdiction, channel, escalation levels | RAG | B |
| Karnataka | Bengaluru | Water & Drainage | BWSSB citizen/customer portal | BWSSB | https://cms.bwssb.gov.in/ | Web app | Channel (Jala Doota app, online complaint) | RAG | B |
| Karnataka | Bengaluru | Streetlights | Public Relation Office — BBMP | BBMP | https://site.bbmp.gov.in/departmentwebsites/PRO/objectives.html | HTML | General complaint-channel reference (thin) | RAG | B |
| Karnataka | Bengaluru | All services (grievance escalation) | Public Grievance Redressal System (iPGRS) | Government of Karnataka, Centre for e-Governance | https://ipgrs.karnataka.gov.in/ | Web app | Escalation levels (L1–L3) | RAG | B |
| Karnataka | Bengaluru | Waste & Sanitation | Solid Waste Management : Bengaluru (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in / smartcities.data.gov.in | https://www.data.gov.in/catalog/solid-waste-management-bengaluru | Dataset (catalog) | Source segregation, D2D efficiency, bin placement, vehicle capacity, revenue | Structured/SQL | C |
| Karnataka | Bengaluru | Waste & Sanitation | Solid Waste Collection Revenue Data Bengaluru as on 01-01-2019 | data.gov.in OGD Platform India | https://www.data.gov.in/resource/solid-waste-collection-revenue-data-bengaluru-01-01-2019 | Dataset | Waste collection revenue | Structured/SQL | C |
| Karnataka | Mysuru | All services | Citizen Services — Mysuru City Corporation | Mysuru City Corporation (MCC) | http://www.mysurucity.mrc.gov.in/en/citizen-services | HTML | Procedure, channels | RAG | B |
| Karnataka | Mysuru | All services (state grievance channel) | Lodge your grievance with municipal corporations of Karnataka | National Government Services Portal (Govt. of India) | https://services.india.gov.in/service/detail/lodge-your-grievance-with-municipal-corporations-of-karnataka | HTML | Channel (iPGRS) | RAG | B |
| Karnataka | Mangaluru | Waste & Sanitation / all services | Citizen Charter — Mangaluru City Corporation | Mangaluru City Corporation (MCC) | http://mangalurucity.mrc.gov.in/en/citizen-charter | HTML | Charter existence confirmed; content not extracted | RAG | B |
| Karnataka | Mangaluru | Waste & Sanitation | Solid Waste Management : Mangaluru (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in | https://www.data.gov.in/keywords/solid-waste-management (Mangaluru catalog entry referenced in search summary; distinct catalog URL not independently confirmed) | Dataset (catalog) | Source segregation, D2D efficiency, bin placement, vehicle capacity | Structured/SQL | C |
| Karnataka | Mangaluru | All services (Smart City ICCC-style portal) | OneTouch Mangaluru Smartcity | Mangaluru Smart City Ltd. (state/city-govt SPV; non-.gov.in domain) | https://www.1touchmangaluru.com/ | Web app | Channel (grievance/feedback) | RAG | B |
| Karnataka | (state-wide) | (reference only, not verified fact source) | complainthub.org — BBMP complaint guide | Third-party (not government) | https://complainthub.org/bbmp-bengaluru/ | HTML | Aggregated complaint-channel info, unverifiable SLA/day-count claims | reference only | D |
| Karnataka | Mangaluru | (reference only, not verified fact source) | Daijiworld.com — MCC waste SLA news coverage | Third-party news site (not government) | https://www.daijiworld.com/news/newsDisplay.aspx?newsID=755979 | HTML | Reported 24hr/72hr SLA claim, unverified against an official MCC page | reference only | D |
| Karnataka | Bengaluru | (reference only, not verified fact source) | Deccan Herald — BBMP streetlight/pothole reporting | Third-party news site (not government) | https://www.deccanherald.com/india/karnataka/bengaluru/bbmp-lavishes-more-funds-on-streetlights-but-complaints-surge-3180698 | HTML | Contextual reporting on streetlight complaint volumes; not a procedural source | reference only | D |

---

## Full records

### Record: Karnataka-Bengaluru-Waste-SWMByelaws
```
service_id: ka-bengaluru-waste-swm-byelaws
service_name: Waste & Public Sanitation
sub_service: Solid waste segregation, collection, and bye-law penalties
problem_type: garbage_collection

state: Karnataka
district: Bengaluru Urban
city: Bengaluru
municipality: Bruhat Bengaluru Mahanagara Palike (BBMP)
zone: NOT FOUND IN OFFICIAL SOURCE (BBMP operates multiple zones; not tied to this specific document in search results)
ward: NOT FOUND IN OFFICIAL SOURCE

department: Solid Waste Management (SWM) wing, BBMP
authority: Bruhat Bengaluru Mahanagara Palike
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: BBMP's Solid Waste Management bye-law/rules (a formal legal instrument hosted on the Government of India's own legislative code repository, India Code) mandates source segregation of waste into wet, dry, and domestic hazardous streams, sets collection-frequency expectations (wet waste + sanitary waste daily; dry waste at least 2-3 times weekly per necessity), and prescribes a Schedule of Fines for waste generators who deliver mixed/unsegregated waste.
procedure: Waste generators must segregate waste and hand it over at appointed times to BBMP or its Notified Service Provider, per the bye-law; mixed waste constitutes a bye-law breach subject to a fine.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND (the bye-law specifies collection *frequency*, not a complaint-to-resolution SLA)
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: NOT FOUND IN OFFICIAL SOURCE (this specific document does not itself describe a complaint channel; see Sahaaya/Fix My Street record for that)
contact_information: NOT FOUND IN OFFICIAL SOURCE

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: Segregate waste into wet, dry, and domestic hazardous (incl. sanitary) streams; deposit in correct receptacles at appointed collection times; non-compliance is a fineable bye-law breach.

source_title: BRUHAT BENGALURU MAHANAGARA PALIKE (BBMP) — Solid Waste Management Rules/Bye-law
source_url: https://upload.indiacode.nic.in/showfile?actid=AC_KA_71_402_00007_14_1552388734165&type=rule&filename=bbmp_swm.pdf
source_type: official_pdf
source_organization: Bruhat Bengaluru Mahanagara Palike, hosted via India Code (Government of India legislative repository)

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: A
geographic_scope: city
notes: Rated A because this is a formal legal bye-law document hosted on India Code (a Government of India statutory-instrument repository) — the most authoritative document type found in this pass for any of the 3 states researched. However, the PDF's full body text was not read, only its existence, title, and search-summarized content confirmed — re-verify exact fine amounts and clause numbers before citing directly. This document governs waste-generator *duties*, not BBMP's own complaint-response SLA, which remains unfound.
```

### Record: Karnataka-Bengaluru-Waste-SahaayaComplaint
```
service_id: ka-bengaluru-waste-sahaaya
service_name: Waste & Public Sanitation
sub_service: Garbage collection missed / bin overflow / illegal dumping
problem_type: garbage_collection

state: Karnataka
district: Bengaluru Urban
city: Bengaluru
municipality: Bruhat Bengaluru Mahanagara Palike (BBMP)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (Solid Waste Management wing, inferred; not confirmed as the exact department name behind Sahaaya)
authority: Bruhat Bengaluru Mahanagara Palike
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: BBMP's Sahaaya complaint system (versions 2.0/3.0 per search results) and the "Fix My Street" app accept civic complaints including missed garbage collection, bin overflow, and illegal dumping, with photo/GPS-tagged submissions and a trackable reference number. A separate WhatsApp number specifically for waste-related issues was also reported.
procedure: Submit complaint with photo via Fix My Street app / Sahaaya portal, or send photo via WhatsApp to the waste-specific number; complaint number issued for tracking.
required_information: Photo, GPS location (auto-captured), landmark
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: BBMP helpline 1533 (24x7), WhatsApp 9480685700 (general) / 9448197197 (reported for waste specifically, not independently confirmed on an official page), landline 22660000 for waste/pothole/streetlight/encroachment/tree complaints (complaint number issued immediately per search summary), Fix My Street / Sahaaya app
contact_information: 1533 (24x7 helpline), 22660000

escalation_procedure: If not resolved within the Citizen Charter's specified timeline, escalate to BBMP's Public Grievance Officer or higher authority (Commissioner/Public Relation Officer); citizens may also lodge a grievance with the state's iPGRS portal.
escalation_authority: BBMP Public Grievance Officer → Commissioner / Public Relation Officer; state escalation via iPGRS (ipgrs.karnataka.gov.in)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Information Technology Department — BBMP (Fix My Street)
source_url: https://site.bbmp.gov.in/departmentwebsites/BBMPIT/fms.html
source_type: govt_portal
source_organization: Bruhat Bengaluru Mahanagara Palike

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Reference to a Citizen Charter with a "specified timeline" was found (mentioned on a services.india.gov.in-style summary), but the actual day-counts were not surfaced — flag for direct-fetch follow-up on BBMP's own citizen charter document, which was not located by URL in this pass.
```

### Record: Karnataka-Bengaluru-Roads-Potholes
```
service_id: ka-bengaluru-roads-potholes
service_name: Roads & Potholes
sub_service: Pothole reporting
problem_type: potholes

state: Karnataka
district: Bengaluru Urban
city: Bengaluru
municipality: Bruhat Bengaluru Mahanagara Palike (BBMP)
zone: Routed to zonal Executive Engineer, Road Infrastructure (per search summary of BBMP's own organizational reporting, not a document read directly)
ward: Each of BBMP's 198 wards has a nodal officer (reported to include IAS/IFS officers, chief engineers, zonal joint commissioners per news search summary — not an official org-chart document)

department: Road Infrastructure (RI) division, BBMP — headed by a Chief Engineer per news reporting (name not treated as durable fact here)
authority: Bruhat Bengaluru Mahanagara Palike
officer_designation: Executive Engineer (Road Infrastructure), per-zone — reported via news search summary, not an official BBMP org document; treat as unverified until fetched.

description: "Pothole Fix" / "Fix My Street" is BBMP's dedicated app for reporting potholes and road-damage issues with photo and GPS-tagged location; also usable for streetlight and garbage issues.
procedure: Submit photo + auto-captured GPS location via the app; complaint routed to the relevant zone's road infrastructure engineering staff.
required_information: Photo, GPS location (auto-captured), landmark (per general Fix My Street description)
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Pothole Fix / Fix My Street mobile app (Android), BBMP helpline 22660000
contact_information: 22660000

escalation_procedure: ESCALATION INFORMATION NOT FOUND (not surfaced specifically for potholes; see general iPGRS escalation record for the state-level channel)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Pothole Fix — BBMP
source_url: https://site.bbmp.gov.in/departmentwebsites/BBMPIT/Pothole%20Fix.html
source_type: govt_portal
source_organization: Bruhat Bengaluru Mahanagara Palike

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: App's existence and BBMP ownership confirmed via bbmp.gov.in's own domain (site.bbmp.gov.in). Organizational routing detail (nodal officers, Executive Engineer per zone) came from Deccan Herald news reporting, not an official BBMP document — do not upgrade to A without direct confirmation.
```

### Record: Karnataka-Bengaluru-Water-BWSSB
```
service_id: ka-bengaluru-water-bwssb
service_name: Water & Drainage
sub_service: Water supply, billing, illegal connections, sewer problems
problem_type: no_low_water_supply

state: Karnataka
district: Bengaluru Urban
city: Bengaluru
municipality: Bruhat Bengaluru Mahanagara Palike (BBMP) — but water supply & sewerage is NOT handled by BBMP; see notes
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Bangalore Water Supply and Sewerage Board (BWSSB) — a separate state statutory board, not a BBMP department
authority: Bangalore Water Supply and Sewerage Board (BWSSB)
officer_designation: Engineer-in-Chief / Chairman, BWSSB (named as the final escalation point per search summary — specific individual not confirmed)

description: BWSSB is the dedicated state board responsible for water supply and sewerage across Bengaluru — a clear jurisdiction split from BBMP (the municipal corporation), consistent with the pattern flagged in 01_service_data_requirements.md. Complaints cover water supply, billing, illegal connections, and sewer problems.
procedure: Register complaint at Level 1 (BWSSB control room / online / app); if unresolved, escalate to Level 2 (divisional office); if still unresolved, escalate to Level 3 (Engineer-in-Chief or Chairman of the Board).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — search results did not surface specific day-count SLAs on an official BWSSB page in this pass.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Toll-free 1916 (24x7 helpline), 1902 (complaints), 080-22238888 (water supply complaints specifically), WhatsApp 8762228888, BWSSB Jala Doota mobile app ("Customer Services" section), in-person at nearest BWSSB office
contact_information: Toll-free 1916 / 1902; water-supply-specific 080-22238888; WhatsApp 8762228888

escalation_procedure: 3-level escalation — Level 1: BWSSB (water supply, billing, illegal connections, sewer problems); Level 2: divisional office if unresolved; Level 3: Engineer-in-Chief or Chairman of the Board.
escalation_authority: BWSSB (L1) → Divisional Office (L2) → Engineer-in-Chief / Chairman, BWSSB (L3)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Bengaluru Water Supply and Sewerage Board — Index
source_url: https://bwssb.karnataka.gov.in/english
source_type: govt_portal
source_organization: Bangalore Water Supply and Sewerage Board

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: **Important jurisdiction-split finding**: for Bengaluru, water supply and sewerage is handled by BWSSB, a separate state statutory board — NOT by BBMP (the municipal corporation that handles waste/roads/streetlights). Any JanMitra routing logic for Bengaluru water complaints must point to BWSSB channels, not BBMP's Sahaaya/Fix My Street system. The 3-level escalation structure is more explicit than anything found for BBMP's own (non-water) categories in this pass.
```

### Record: Karnataka-Bengaluru-Streetlight
```
service_id: ka-bengaluru-streetlight
service_name: Streetlights
sub_service: Non-functioning streetlight, LED conversion complaints
problem_type: streetlight_not_working

state: Karnataka
district: Bengaluru Urban
city: Bengaluru
municipality: Bruhat Bengaluru Mahanagara Palike (BBMP)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: BBMP Electrical division (name inferred from "electrical division" reference in a Deccan Herald article about Sahaaya complaint volumes; not an official department-name document)
authority: Bruhat Bengaluru Mahanagara Palike
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Streetlight-fault complaints (non-burning lights, damaged poles) are filed via the same general-purpose channels as other BBMP civic complaints (Sahaaya, Fix My Street, helpline 22660000). News reporting indicates a large share of Sahaaya complaints are streetlight-related, directed to BBMP's electrical division — but no dedicated streetlight-specific official portal/page (distinct from BBMP's general complaint channels) was located in this pass.
procedure: File via BBMP helpline 22660000, Fix My Street app, or Sahaaya portal.
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: BBMP helpline 22660000, Fix My Street app, Sahaaya portal
contact_information: 22660000

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Public Relation Office — BBMP
source_url: https://site.bbmp.gov.in/departmentwebsites/PRO/objectives.html
source_type: govt_portal
source_organization: Bruhat Bengaluru Mahanagara Palike

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Thinnest of Bengaluru's 4 service records, consistent with 01_service_data_requirements.md's expectation that streetlights rarely get a discrete SLA or dedicated official channel. Worth a targeted follow-up search on whether BBMP's ICCC/Smart City system has a dedicated streetlight module — not located in this pass.
```

### Record: Karnataka-Bengaluru-AllServices-iPGRS
```
service_id: ka-bengaluru-all-ipgrs
service_name: (cross-cutting — grievance escalation covers all 4 categories, state-level)
sub_service: Public grievance escalation
problem_type: multiple

state: Karnataka
district: Bengaluru Urban (state-wide system, applies to all districts)
city: Bengaluru
municipality: N/A (state-level portal, used as BBMP's own escalation route per its Citizen Charter reference)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: Centre for e-Governance, Government of Karnataka
authority: Government of Karnataka — Integrated Public Grievance Redressal System (iPGRS)
officer_designation: Programme Director – iPGRS, Centre for e-Governance (per search summary contact reference — not independently confirmed)

description: iPGRS (also referenced as "Janaspandana-iPGRS") is Karnataka's state-wide grievance redressal platform, usable as an escalation route when a department/ULB (e.g. BBMP) fails to resolve a complaint within its own Citizen Charter timeline.
procedure: Register grievance online at ipgrs.karnataka.gov.in or by calling 1902; grievances move from L1 to L3 if unresolved or if resolution feedback is unsatisfactory (citizens can escalate up to twice).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND (no specific day-count found for L1→L2→L3 transitions)
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: Online portal (ipgrs.karnataka.gov.in), phone 1902
contact_information: 1902

escalation_procedure: 3-level system — L1 (originating department) → L2 → L3, triggered by non-resolution or unsatisfactory feedback (citizen can escalate up to 2 times); in case of inaction, a system-generated show-cause notice is issued to the defaulting officer. A state-level review committee (chaired by the Chief Secretary) and district-level review committees (chaired by district commissioners) monitor redressal quality.
escalation_authority: L1 department → L2 → L3; oversight via state-level review committee (Chief Secretary) and district-level review committees (District Commissioners)

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: About Us — PGRS | Government of Karnataka
source_url: https://ipgrs.karnataka.gov.in/Home/About
source_type: grievance_portal
source_organization: Government of Karnataka — Centre for e-Governance

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: state
notes: This is a state-level cross-department escalation channel, not specific to any one civic-service category or city — logged as a general fallback escalation route applicable when BBMP/MCC/other-ULB channels fail. The 3-level (L1-L3) structure with a show-cause-notice mechanism is the most concrete escalation detail found for Karnataka in this pass; worth prioritizing for direct-fetch confirmation of exact day-count thresholds.
```

### Record: Karnataka-Mysuru-AllServices
```
service_id: ka-mysuru-all-services
service_name: (cross-cutting — general civic complaint channel)
sub_service: General civic grievance registration
problem_type: multiple

state: Karnataka
district: Mysuru
city: Mysuru
municipality: Mysuru City Corporation (MCC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Mysuru City Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: MCC's Citizen Services page lists channels for civic complaints; the state's iPGRS system (1902) is also usable to lodge grievances against Karnataka's municipal corporations generally, per the National Government Services Portal's own service listing.
procedure: File via MCC's toll-free helpline, iPGRS (1902), or in-person at MCC's office (New Sayyaji Road, Near Banumaiah College, Mysuru–570004).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: MCC toll-free helpline 1800-200-5822, iPGRS 1902, MCC landlines 0821-2418800 / 2440890 / 2418816 / 2431112, email ka.mysuru.cc@gmail.com
contact_information: Toll-free 1800-200-5822; iPGRS 1902

escalation_procedure: ESCALATION INFORMATION NOT FOUND (MCC-specific escalation chain not surfaced; general iPGRS L1-L3 structure applies as the state-level fallback — see Bengaluru iPGRS record)
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen Services — Mysuru City Corporation
source_url: http://www.mysurucity.mrc.gov.in/en/citizen-services
source_type: govt_portal
source_organization: Mysuru City Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: No service-specific (waste/water/roads) breakdown surfaced for Mysuru beyond a general complaint channel and a separate streetlight control-room number (see next record) — thinner coverage than Bengaluru, consistent with expectation that the state capital has richer documentation.
```

### Record: Karnataka-Mysuru-Streetlight
```
service_id: ka-mysuru-streetlight
service_name: Streetlights
sub_service: Faulty streetlight / bulb complaint
problem_type: streetlight_not_working

state: Karnataka
district: Mysuru
city: Mysuru
municipality: Mysuru City Corporation (MCC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE (MCC Electrical/Control Room, name not confirmed as official department title)
authority: Mysuru City Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: MCC operates a dedicated Control Room toll-free number for streetlight complaints; a mobile app allowing citizens to register faulty-bulb complaints and track status was also referenced, but its name/official URL was not confirmed in this pass. Approx. 68,178 LED streetlights have reportedly replaced mercury lamps city-wide (per search summary — not confirmed on an official MCC page).
procedure: Call the MCC Control Room toll-free number to register a complaint; complaint is verified and an electrician assigned "within a few days" per a general Karnataka-wide description (not MCC-specific, not a confirmed SLA).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — "a few days" appeared only in a general (non-Mysuru-specific, non-official) search summary, not an official MCC document.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: MCC Control Room toll-free 18004255925
contact_information: 18004255925

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Electricity — District Mysuru, Government of Karnataka (search-summarized; MCC's own page not directly located)
source_url: https://mysore.nic.in/en/public-utility-category/electricity/
source_type: govt_portal
source_organization: District Mysuru administration / Mysuru City Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: Toll-free control-room number is specific and plausible for Mysuru, but the source page is the district NIC portal (mysore.nic.in), not MCC's own site directly — flag for re-confirmation. LED conversion figure is unsourced to any URL and should not be treated as fact.
```

### Record: Karnataka-Mangaluru-Waste-Citizen-Charter
```
service_id: ka-mangaluru-waste-citizen-charter
service_name: Waste & Public Sanitation
sub_service: Solid waste collection (door-to-door), dustbin clearance
problem_type: garbage_collection

state: Karnataka
district: Dakshina Kannada
city: Mangaluru
municipality: Mangaluru City Corporation (MCC)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Mangaluru City Corporation
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: MCC is responsible for collection, segregation, transportation, dumping, and processing of city waste door-to-door. MCC's own website has a dedicated Citizen Charter page (existence confirmed via URL; content not extracted in this pass).
procedure: NOT FOUND IN OFFICIAL SOURCE — this pass could not confirm MCC's own official waste-complaint channel/procedure text (see notes on the SMS-complaint claim below, which is third-party-sourced).
required_information: NOT FOUND IN OFFICIAL SOURCE
required_documents: NOT FOUND IN OFFICIAL SOURCE

sla: SLA NOT FOUND — a "24-hour (dustbin clearance) / 72-hour (other issues)" SLA figure appeared only in a Daijiworld.com news article (third-party, court-case coverage), not confirmed on an official mangalurucity.mrc.gov.in page in this pass. Do not treat as verified; see notes.
response_time: SLA NOT FOUND
resolution_time: SLA NOT FOUND

complaint_channel: NOT FOUND IN OFFICIAL SOURCE — an SMS complaint number (81236 66266) was reported in the same third-party news article referenced above, not independently confirmed on an official MCC page.
contact_information: MCC help line 080 23108108 / WhatsApp 8277777728 (per search result attributed to mangalurucity.mrc.gov.in's own listing) — not specific to waste, general MCC contact.

escalation_procedure: ESCALATION INFORMATION NOT FOUND
escalation_authority: NOT FOUND IN OFFICIAL SOURCE

faq: NOT FOUND IN OFFICIAL SOURCE
citizen_guidance: NOT FOUND IN OFFICIAL SOURCE

source_title: Citizen Charter — Mangaluru City Corporation
source_url: http://mangalurucity.mrc.gov.in/en/citizen-charter
source_type: citizen_charter
source_organization: Mangaluru City Corporation

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: B
geographic_scope: city
notes: This record deliberately keeps `sla` and `complaint_channel` at their NOT FOUND sentinels even though a specific-sounding 24hr/72hr SLA and an SMS number were found, because both traced only to daijiworld.com (a news site), not to MCC's own domain — per the environment-note rule at the top of this file, do not enter third-party-sourced day-counts into real fields. If MCC's own Citizen Charter PDF is directly fetched later and confirms the same figures, this record should be upgraded.
```

### Record: Karnataka-Bengaluru-Waste-OGDDataset
```
service_id: ka-bengaluru-waste-ogd-dataset
service_name: Waste & Public Sanitation
sub_service: Solid waste management operational data
problem_type: garbage_collection

state: Karnataka
district: Bengaluru Urban
city: Bengaluru
municipality: Bruhat Bengaluru Mahanagara Palike (BBMP)
zone: NOT FOUND IN OFFICIAL SOURCE
ward: NOT FOUND IN OFFICIAL SOURCE

department: NOT FOUND IN OFFICIAL SOURCE
authority: Ministry of Housing & Urban Affairs — Smart Cities Mission (dataset publisher), sourced from BBMP operations
officer_designation: NOT FOUND IN OFFICIAL SOURCE

description: Structured dataset covering source segregation practices, door-to-door (D2D) collection efficiency, bin placement/sizes, collection vehicle counts/capacity, waste processing types, and disposal options for Bengaluru, published via the Smart Cities Mission Data Portal and mirrored on data.gov.in.
procedure: N/A (dataset, not a citizen-facing procedure)
required_information: N/A
required_documents: N/A

sla: SLA NOT FOUND (not applicable — this is operational/analytics data, not a citizen SLA)
response_time: N/A
resolution_time: N/A

complaint_channel: N/A
contact_information: N/A

escalation_procedure: N/A
escalation_authority: N/A

faq: N/A
citizen_guidance: N/A

source_title: Solid Waste Management : Bengaluru
source_url: https://www.data.gov.in/catalog/solid-waste-management-bengaluru
source_type: ogd_dataset
source_organization: Ministry of Housing & Urban Affairs — Smart Cities Mission, via Open Government Data (OGD) Platform India

publication_date: NOT FOUND IN OFFICIAL SOURCE
last_updated: NOT FOUND IN OFFICIAL SOURCE
retrieved_at: 2026-08-09 (via WebSearch only)

verification_status: NOT INDEPENDENTLY FETCHED — confirm before production use
source_quality: C
geographic_scope: city
notes: Structured/SQL-suitable data source, useful for analytics rather than citizen-facing procedural RAG content, per the quality-C definition in 00_README.md. A companion "Solid Waste Collection Revenue Data Bengaluru as on 01-01-2019" resource was also found at https://www.data.gov.in/resource/solid-waste-collection-revenue-data-bengaluru-01-01-2019.
```

---

## Coverage notes for Karnataka

- **Best-covered service:** Water & Drainage for Bengaluru specifically —
  the BWSSB jurisdiction split (a separate statutory board handling water
  supply/sewerage instead of BBMP) came with a genuinely explicit 3-level
  escalation chain (L1 BWSSB → L2 divisional office → L3 Engineer-in-Chief/
  Chairman), the most concrete escalation detail found for the state.
  Waste & Sanitation is close behind, thanks to the BBMP SWM bye-law being
  a genuine India Code legal instrument (quality A) plus two `data.gov.in`
  OGD datasets.
- **Weakest-covered service:** Streetlights — as anticipated in
  `01_service_data_requirements.md`, no dedicated department name, SLA,
  or escalation path was found for Bengaluru or Mysuru; Mangaluru's
  streetlight coverage was thinner still (only a Corporator's complaint
  about LED luminosity surfaced, not a citizen procedure).
- **Jurisdiction-split finding (important):** Bengaluru's water supply and
  sewerage is run by BWSSB, a separate state statutory board — **not**
  BBMP. This must be reflected in any future JanMitra routing logic for
  Bengaluru water/drainage complaints; BBMP's Sahaaya/Fix My Street
  channels are not the right destination for those.
- **Third-city choice:** Mangaluru was used (per the assignment's
  suggested list) instead of another candidate — its city corporation has
  a genuine `.mrc.gov.in` domain with a Citizen Charter page, but this
  pass could not extract specific SLA/procedure content from it directly;
  the only specific-sounding SLA figures found (24hr/72hr) traced to a
  news article, not MCC's own site, and were deliberately excluded from
  the real `sla` field per the sentinel-value rule.
- Nothing in this file should be read as confirming exact SLA numbers for
  Karnataka's civic services — the one genuinely official-legal-document
  SLA-adjacent content found (BBMP's SWM bye-law) describes collection
  *frequency*, not complaint-response time; every complaint-response
  day-count claim found in this pass traced back to a third-party
  aggregator or news site, and is logged only in `notes` for context.
