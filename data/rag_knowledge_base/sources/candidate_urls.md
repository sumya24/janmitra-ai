# RAG Knowledge Base — Source Research Log

Every government-data URL investigated for this project, logged so effort isn't repeated. Ordered
roughly chronologically. "Result" is the ground truth as of the date checked — government sites do
migrate, so re-verify before assuming a "dead end" entry is still dead.

| Date | URL / target | Result | Notes |
|---|---|---|---|
| 2026-08-09 | `https://data.gov.in/...` (any catalog page) | **BLOCKED** | `data.gov.in` returns HTTP 403 to automated fetching (WebFetch). Not usable as a source-fetch target at all, regardless of which dataset. |
| 2026-08-09 | `https://www.data.gov.in/catalog/solid-waste-management-bareilly` (as given in brief) | **DEAD** | This exact URL does not resolve to real content. |
| 2026-08-09 | `https://smartcities.data.gov.in/catalog/solid-waste-managementbareilly-2` (corrected subdomain, found via WebSearch) | **DEAD (empty catalog entry)** | The dataset has migrated to `smartcities.data.gov.in`, confirming govt data has partially moved subdomains — but this specific catalog page shows "No Result Found... Published on Data Portal: NA". No usable structured content, even though the page itself loads. |
| 2026-08-09 | data.gov.in street-light dataset for Tumakuru (as given in brief) | **NOT FOUND** | WebSearch could not locate this dataset at any indexed URL. Likely never existed at the referenced location, or was removed/never indexed. |
| 2026-08-09 | `https://www.tnurbantree.tn.gov.in/melur/citizen-charter/` | **UNREACHABLE** | First attempt (WebFetch): SSL certificate validation failure (`unable to verify the first certificate`). Second attempt on a different TN municipality (Virudhunagar), same domain: same SSL failure. Third attempt via `curl -k` (skip cert validation) with `-v`: TCP connection succeeds, TLS handshake is sent, then the connection hangs and times out after 15s with 0 bytes received (`Operation timed out after 15003 milliseconds with 0 bytes received`). This is not just a cert problem — the server is not completing the TLS handshake / responding at all from this environment. Confirmed unreachable via 3 independent method attempts (WebFetch x2, curl -k x1). **Conclusion: `tnurbantree.tn.gov.in` is not usable as a source domain from this environment.** A human using a normal browser may still be able to reach it (browsers are far more permissive about legacy/misconfigured TLS than curl/requests) — worth re-attempting manually outside this pipeline if TN coverage becomes a priority later. |
| 2026-08-09/10 | `https://urban.odisha.gov.in/sites/default/files/2021-05/Draft%20Citizen%20Charter_HUD_Final.pdf` (Housing & Urban Development Dept, Govt of Odisha — "Citizen's Charter (Draft)") | **VERIFIED — SUCCESS** | Fetched successfully (805KB PDF, 36 pages). `Read` tool's page-render failed (`pdftoppm is not installed`, no poppler on this Windows machine) — worked around with `pypdf.PdfReader` (pure-Python, already installed) to extract full text directly. Re-checked live with `curl -s -o /dev/null -w "%{http_code}"` on 2026-08-10: **HTTP 200**. Contains a real, detailed services table (26 services with process time/fees/designated officer/appellate/revisional authority) covering, among others, solid waste lifting, water/sewer pipeline repair, tube-well repair, street light replacement, road cutting permission, and road restoration — plus a state-wide, ULB-type-differentiated grievance escalation matrix (4 levels, response times 7/7/15/30 days for Corporations; 7/7/7/15 days for Councils/NACs) and a citation of the Odisha Right to Public Services (ORTPS) Act 2012's statutory appeal windows (30-90 days to Appellate Authority, 30 days for Appellate Authority to dispose; 30-90 days to Revisional Authority, no statutory disposal deadline). Used as the pilot verified source — see `knowledge_records/verified/odisha/statewide.json`. **Caveat carried into `SourceRecord.notes`:** the document is explicitly a *draft* and states "The next review of the citizen charter is scheduled on July 2016" — i.e. it may be dated/superseded; treated as verified because the PDF itself is real, live, and government-published, not because its content is guaranteed current. |

| 2026-08-10 | `https://e-nigam.punjab.gov.in/MCData/Mohali/CITIZENCHARTER.pdf` (Municipal Corporation, S.A.S. Nagar/Mohali, Punjab) | **VERIFIED — SUCCESS** | Found via WebSearch. Confirmed live (HTTP 200), downloaded (632KB, 17 pages), text extracted via pypdf. Genuinely city-specific (not state-wide like Odisha's), with named officers, personal mobile numbers, toll-free complaint line (1800-137-0007, since Dec 2013), a mobile complaint app ("MC CRAMAT"), a Punjab Right to Service Act 2011 statutory-SLA table, and a full 4-level internal grievance escalation ladder (Table 3) with per-day time norms per level. Used for 4 KnowledgeRecords -- see `knowledge_records/verified/punjab/mohali.json`. |
| 2026-08-10 | `https://enigambackuprestore.blob.core.windows.net/securefilestructure/MC/Patiala/MCSubMenu/pdf/linkpdf_2_20_2025_45_862.CITIZEN%20CHARTER%20MCP.pdf` (Municipal Corporation Patiala, Punjab) | **VERIFIED — SUCCESS** | Found via WebSearch, hosted on the Punjab e-Governance backup/CDN blob storage (not the primary domain, but still an official government-published artifact for the same department, same pattern as `smartcities.data.gov.in` being a legitimate alternate subdomain). Confirmed live (HTTP 200), downloaded (843KB, 22 pages), text extracted via pypdf. References a newer Right to Service Act (2018, vs. Mohali's 2011) whose table covers a *different* set of services (no solid-waste/street-light/roads entries) -- confirmed by reading the actual table rather than assumed to match Mohali's. No multi-level escalation ladder present (unlike Mohali) -- only nodal-officer contacts and general Secretary-level oversight are stated; recorded as such rather than invented. Used for 4 KnowledgeRecords -- see `knowledge_records/verified/punjab/patiala.json`. |
| 2026-08-10 | `http://mcchandigarh.gov.in/?q=citizen-charter` (Municipal Corporation Chandigarh) | **PARTIAL / NOT USED** | Page loads and confirms real complaint-channel details (toll-free 14420, 8 AM-8 PM; phone 0172-2787200; online portal `egov.chandigarhsmartcity.in`; Municipal Commissioner named) but the actual citizen-charter document with per-service SLAs was not present in the fetched page content -- only linked deeper in the site navigation, not yet located as a directly fetchable PDF/page. Not used as a KnowledgeRecord source this pass since no verifiable per-service figures were obtained; flagged as a lead worth revisiting (the toll-free number and portal alone are real and could support a lighter-weight record if a fuller charter document is found later). |

## Leads not yet pursued (future work, not fabricated, not yet checked)

- Other states' Housing/Urban Development or Municipal Administration department citizen charters,
  by analogy to Odisha's (search pattern: `"citizen charter" "<department name>" <state> filetype:pdf`
  or the department's own `.gov.in` site — many states publish an equivalent document).
  `smartcities.data.gov.in` (the corrected subdomain) for OTHER cities' solid-waste/streetlight
  datasets, since the Bareilly-specific page was dead but the subdomain itself loads — an
  as-yet-unconfirmed lead, not verified either way.
- CPGRAMS / PGPortal (`pgportal.gov.in`) as a possible source for a *national*-scope, genuinely
  official escalation reference — not yet attempted.
- Individual large-city municipal corporation websites (BMC, Pune Municipal Corporation, GHMC,
  etc.) sometimes publish citizen charters or SLA documents directly — not yet attempted.

## 2026-08-09/10 batch — 9-state + Maharashtra WebSearch-only candidate pass

The following URLs were found via **WebSearch only** — this environment's WebFetch was completely blocked (tested against government sites, Wikipedia, and even anthropic.com; see `research/rag-knowledge-base/02_source_inventory/*.md` in this repo for the full per-record detail, methodology note, and per-state coverage analysis this batch produced). None of these were independently fetched/read — they are real, currently-indexed URLs (confirmed to exist via search-engine indexing) but their content was not directly confirmed the way this log's earlier VERIFIED entries were (HTTP-200-checked, downloaded, text-extracted). **Do not promote any of these to `VERIFIED` without an actual fetch-and-read pass** — that's the whole reason they're logged here rather than in `knowledge_records/verified/`. A quality rating (A/B/C, per this project's rubric: A = official + specific to the service/location, B = official + general, C = official structured dataset) is given as a rough sourcing-priority signal for whoever picks this up next, not a verification claim.


### Andhra Pradesh

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://www.gvmc.gov.in/static_content/Grievances.jsp | Modes Of Registering Grievances By The Citizens / IVRS | Greater Visakhapatnam Municipal Corporation (GVMC) | HTML | A | Visakhapatnam | All services (grievance mechanism) | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://www.gvmc.gov.in/ | Smart Vizag (GVMC's citizen app) | GVMC | HTML | A | Visakhapatnam | All services (app channel) |
| https://www.data.gov.in/catalog/solid-waste-management-visakhapatnam | Solid Waste Management : Visakhapatnam (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | Dataset (catalog) | C | Visakhapatnam | Waste & Sanitation |
| https://services.india.gov.in/service/detail/grievances-for-vijayawada-municipal-corporation-commissioner-andhra-pradesh | Grievances for Vijayawada Municipal Corporation Commissioner | services.india.gov.in (National Government Services Portal, Govt. of India) | HTML | B | Vijayawada | All services (grievance mechanism) |
| https://services.india.gov.in/service/detail/check-status-of-complaints-against-vijayawada-municipal-corporation-1 | Check status of complaints against Vijayawada Municipal Corporation | services.india.gov.in | HTML | B | Vijayawada | All services (status check) |
| https://vijayawada.cdma.ap.gov.in/services | Vijayawada Municipal Corporation — Online Services | Vijayawada Municipal Corporation, via CDMA AP State Portal | HTML | A | Vijayawada | All services (ULB portal) |
| http://www.ourvmc.org/jnnurm/ch414.pdf | Vijayawada City Development Plan — Ch.4.14 (JNNURM) | Vijayawada Municipal Corporation (via ourvmc.org, VMC's own legacy domain) | PDF | B | Vijayawada | Water & Drainage |
| https://www.cdma.ap.gov.in/others/portal-info/citizen-charter/ | Citizen Charter | CDMA — Commissioner & Director of Municipal Administration, Govt. of Andhra Pradesh | HTML | B | (state-wide, applies to both cities) | All services |
| https://cdma.ap.gov.in/services/grievances/ | Grievances | CDMA, Govt. of Andhra Pradesh | HTML | B | (state-wide) | All services |
| https://cdma.ap.gov.in/initiatives/puramithra/ | Puramithra Initiative | CDMA, Govt. of Andhra Pradesh | HTML | B | (state-wide) | All services |
| https://pgrs.ap.gov.in/Dashboard/OfficerDashboard | Public Grievance Redressal System (PGRS) | Government of Andhra Pradesh | Web app | B | (state-wide) | All services |

### Gujarat

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://ahmedabadcity.gov.in/portal/jsp/Static_pages/pi_ccharter.jsp | Citizen Charter :: Ahmedabad Municipal Corporation | Ahmedabad Municipal Corporation (AMC) | HTML | A | Ahmedabad | All services (Citizen Charter) | **[CHECKED — 404, page no longer exists. Not usable, not re-tried.]** |
| https://ahmedabadcity.gov.in/StaticPage/solid_waste_mgmt | Solid Waste Management — AMC | AMC | HTML | A | Ahmedabad | Waste & Sanitation |
| https://ahmedabadcity.gov.in/Images/_SWM%20Dept_SWM%20BREIF%20NOTE%20IN%20ENGLISH.pdf | SWM Dept — Brief Note (PDF) | AMC | PDF | A | Ahmedabad | Waste & Sanitation | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://amccrs.apphost.in/AMCPortal | AMCCRS — Comprehensive Complaint Redressal System | AMC | Web app | B | Ahmedabad | All services (complaint portal) |
| https://www.suratmunicipal.gov.in/Downloads/CitizenCharter | Citizen Charter | Surat Municipal Corporation (SMC) | HTML | A | Surat | All services (Citizen Charter) | **[CHECKED — page loads, but it's a generic index linking to dept-specific charters (Watch & Ward, Fire, Town Planning, Shops & Establishments, Law, etc.) with NO SWM/Water/Roads/Streetlight-specific PDF among them. Not usable as-is. The actual targets for our 4 categories are the separate department pages already listed above (rows 63-67: solidwastemanagementhome, drainageintroduction, DrainageHowDoI, hydraulichome, StreetLightsHome) — try those instead.]** |
| https://www.suratmunicipal.gov.in/departments/solidwastemanagementhome | Solid Waste Management Home | SMC | HTML | A | Surat | Waste & Sanitation | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://www.suratmunicipal.gov.in/departments/drainageintroduction | Drainage — Introduction | SMC | HTML | A | Surat | Water & Drainage |
| https://www.suratmunicipal.gov.in/Departments/DrainageHowDoI | Drainage — How Do I Get a Connection? | SMC | HTML | A | Surat | Water & Drainage |
| https://www.suratmunicipal.gov.in/departments/hydraulichome | Water Supply (Hydraulic) — Home | SMC | HTML | A | Surat | Water & Drainage |
| https://www.suratmunicipal.gov.in/Departments/StreetLightsHome | Streetlight — Home | SMC | HTML | A | Surat | Streetlights | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json. Follow-up candidate surfaced by this page's own nav: https://www.suratmunicipal.gov.in/Departments/NonWorkingStreetlights (not yet fetched) likely has the actual complaint procedure.]**
| https://www.data.gov.in/catalog/solid-waste-management-surat | Solid Waste Management : Surat (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | Dataset (catalog) | C | Surat | Waste & Sanitation |
| https://vmc.gov.in/PublicService.aspx | Public Service — VMC | Vadodara Municipal Corporation (VMC) | HTML | A | Vadodara | All services (public service portal) |
| https://vmc.gov.in/Department_SWM_Approach.aspx | Department — Solid Waste Management Approach | VMC | HTML | A | Vadodara | Waste & Sanitation |
| https://vmc.gov.in/StreetLight.aspx | Street Light — VMC | VMC | HTML | A | Vadodara | Streetlights |
| https://smartcities.data.gov.in/catalog/solid-waste-generated-collected-processed-data-vadodara | Solid Waste Generated/Collected/Processed Data : Vadodara (dataset) | MoHUA Smart Cities Mission, via Smart Cities Mission Data Portal | Dataset | C | Vadodara | Waste & Sanitation |
| https://gwssb.gujarat.gov.in/helpline | Gujarat Water Supply & Sewerage Board (GWSSB) — Helpline | Gujarat Water Supply & Sewerage Board | HTML | B | (state-wide) | Water & Drainage (context/jurisdiction) |
| https://udd.gujarat.gov.in/ | Urban Development & Urban Housing Department | Government of Gujarat | HTML | B | (state-wide) | All services |
| https://enagar.gujarat.gov.in/enagar/login.jsp | eNagar / DigiGOV | Government of Gujarat, Urban Development & Urban Housing Dept. | Web app | B | (state-wide) | All services |
| https://karnataka.data.gov.in/catalog/solid-waste-management-basic-ahmedabad | Solid Waste Management Basic : Ahmedabad | data.gov.in OGD, mirrored under a karnataka.data.gov.in subdomain (domain oddity — see notes) | Dataset (catalog) | C | Ahmedabad (reference, odd domain) | (structured, quality caveat) |

### Karnataka

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://upload.indiacode.nic.in/showfile?actid=AC_KA_71_402_00007_14_1552388734165&type=rule&filename=bbmp_swm.pdf | Bruhat Bengaluru Mahanagara Palike Solid Waste Management Rules (bye-law) | BBMP, via India Code (Govt. of India legislative repository) | PDF | A | Bengaluru | Waste & Sanitation | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://site.bbmp.gov.in/departmentwebsites/BBMPIT/fms.html | Fix My Street / Sahaaya complaint system | BBMP (Information Technology Dept.) | HTML | B | Bengaluru | Waste & Sanitation |
| https://site.bbmp.gov.in/departmentwebsites/BBMPIT/Pothole%20Fix.html | Pothole Fix / Fix My Street app | BBMP (Information Technology Dept.) | HTML | B | Bengaluru | Roads & Potholes |
| https://bwssb.karnataka.gov.in/english | BWSSB — Bangalore Water Supply and Sewerage Board (official site) | BWSSB (state statutory board, NOT BBMP) | HTML | B | Bengaluru | Water & Drainage |
| https://cms.bwssb.gov.in/ | BWSSB citizen/customer portal | BWSSB | Web app | B | Bengaluru | Water & Drainage |
| https://site.bbmp.gov.in/departmentwebsites/PRO/objectives.html | Public Relation Office — BBMP | BBMP | HTML | B | Bengaluru | Streetlights |
| https://ipgrs.karnataka.gov.in/ | Public Grievance Redressal System (iPGRS) | Government of Karnataka, Centre for e-Governance | Web app | B | Bengaluru | All services (grievance escalation) |
| https://www.data.gov.in/catalog/solid-waste-management-bengaluru | Solid Waste Management : Bengaluru (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in / smartcities.data.gov.in | Dataset (catalog) | C | Bengaluru | Waste & Sanitation |
| https://www.data.gov.in/resource/solid-waste-collection-revenue-data-bengaluru-01-01-2019 | Solid Waste Collection Revenue Data Bengaluru as on 01-01-2019 | data.gov.in OGD Platform India | Dataset | C | Bengaluru | Waste & Sanitation |
| http://www.mysurucity.mrc.gov.in/en/citizen-services | Citizen Services — Mysuru City Corporation | Mysuru City Corporation (MCC) | HTML | B | Mysuru | All services |
| https://services.india.gov.in/service/detail/lodge-your-grievance-with-municipal-corporations-of-karnataka | Lodge your grievance with municipal corporations of Karnataka | National Government Services Portal (Govt. of India) | HTML | B | Mysuru | All services (state grievance channel) |
| http://mangalurucity.mrc.gov.in/en/citizen-charter | Citizen Charter — Mangaluru City Corporation | Mangaluru City Corporation (MCC) | HTML | B | Mangaluru | Waste & Sanitation / all services |
| https://www.data.gov.in/keywords/solid-waste-management (Mangaluru catalog entry referenced in search summary; distinct catalog URL not independently confirmed) | Solid Waste Management : Mangaluru (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in | Dataset (catalog) | C | Mangaluru | Waste & Sanitation |
| https://www.1touchmangaluru.com/ | OneTouch Mangaluru Smartcity | Mangaluru Smart City Ltd. (state/city-govt SPV; non-.gov.in domain) | Web app | B | Mangaluru | All services (Smart City ICCC-style portal) |

### Kerala

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://kochicorporation.lsgkerala.gov.in/en/form/public-grievance-cellnew | Public Grievance Cell | Cochin Corporation (LSGD Kerala) | HTML | B | Kochi | All services (grievance cell) |
| https://mykochi.lsgkerala.gov.in/index/complaint | My Kochi — Complaints | Cochin Corporation (LSGD Kerala) | Web app | B | Kochi | All services (app/portal) |
| https://mykochi.lsgkerala.gov.in/index/complaintstatus | My Kochi — All Complaints / Complaint Status | Cochin Corporation (LSGD Kerala) | Web app | B | Kochi | All services (status check) |
| https://kochicorporation.lsgkerala.gov.in/en/solid-waste-management/368 | Solid Waste Management | Cochin Corporation (LSGD Kerala) | HTML | A | Kochi | Waste & Sanitation |
| https://kochicorporation.lsgkerala.gov.in/en/list-empanelment-agencies-solid-waste-management/491 | List of Empanelment Agencies for Solid Waste Management | Cochin Corporation (LSGD Kerala) | HTML | A | Kochi | Waste & Sanitation |
| https://kochicorporation.lsgkerala.gov.in/system/files/2022-02/Septage_management_bylaw.pdf | Septage Management Byelaw (Draft) | Cochin Corporation (LSGD Kerala) | PDF | A | Kochi | Water & Drainage (sewerage) | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://kochicorporation.lsgkerala.gov.in/en/engineering | Engineering | Cochin Corporation (LSGD Kerala) | HTML | B | Kochi | Roads & Potholes / Streetlights |
| https://tmc.lsgkerala.gov.in/en/grievances-redressal-mechanism/1749 | Grievances Redressal Mechanism | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | HTML | B | Thiruvananthapuram | All services (grievance mechanism) |
| https://tmc.lsgkerala.gov.in/en/public-grievance-cell | Public Grievance Cell | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | HTML | B | Thiruvananthapuram | All services (grievance cell) |
| https://tmc.lsgkerala.gov.in/en/organisational-structure | Organisational Structure | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | HTML | B | Thiruvananthapuram | All services (organisational structure) |
| https://tmc.lsgkerala.gov.in/en/solid-waste-management | Solid Waste Management | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | HTML | A | Thiruvananthapuram | Waste & Sanitation |
| https://tmc.lsgkerala.gov.in/en/kharamaalainaya-nairamaarajajanam | Solid Waste Disposal | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | HTML | A | Thiruvananthapuram | Waste & Sanitation |
| https://tmc.lsgkerala.gov.in/en/english | Capital city, Clean city — waste collection centres and calendar | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | HTML | A | Thiruvananthapuram | Waste & Sanitation |
| https://tmc.lsgkerala.gov.in/en/engineering | Engineering | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | HTML | A | Thiruvananthapuram | Roads & Potholes / Streetlights |
| https://smarttvm.tmc.lsgkerala.gov.in/ | Smart Trivandrum — Civic Services Portal | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | Web app | A | Thiruvananthapuram | All services (integrated portal) |
| https://smarttvm.tmc.lsgkerala.gov.in/complaint/report | Smart Trivandrum — Report a Complaint | Thiruvananthapuram Municipal Corporation (LSGD Kerala) | Web app | A | Thiruvananthapuram | All services (complaint intake) |
| https://kwa.kerala.gov.in/en/consumer-grievances/ | Consumer Grievances | Kerala Water Authority (KWA) | HTML | A | Kochi + Thiruvananthapuram | Water & Drainage |
| https://kwa.kerala.gov.in/en/contact-us/ | Contact Us — KWA | Kerala Water Authority (KWA) | HTML | B | Kochi + Thiruvananthapuram | Water & Drainage |
| https://kwa.kerala.gov.in/en/citizen-corner/ | Consumers Corner | Kerala Water Authority (KWA) | HTML | B | Kochi + Thiruvananthapuram | Water & Drainage |
| https://aqualoom.kwa.kerala.gov.in/ | Aqualoom — KWA online complaint system | Kerala Water Authority (KWA) | Web app | A | Kochi + Thiruvananthapuram | Water & Drainage |
| https://lsgkerala.gov.in/en/resources/citizen-charter | Citizen Charter | Local Self Government Department (LSGD), Govt. of Kerala | HTML | B | (state-wide) | All services (citizen charter) |
| https://lsgd.kerala.gov.in/en/waste-management/solid-waste-management/policy-guidelines/ | Policy & Guidelines — Solid Waste Management | Local Self Government Department (LSGD), Govt. of Kerala | HTML | B | (state-wide) | Waste & Sanitation |
| https://lsgkerala.gov.in/index.php/en/public-grievance-redressal-mechanism | Public Grievance Redressal Mechanism | Local Self Government Department (LSGD), Govt. of Kerala | HTML | B | (state-wide) | All services (grievance mechanism, general) |
| (referenced via search summary of Kochi Corporation grievance escalation; no independently confirmed CMPGRC URL surfaced in this pass) | Chief Minister's Public Grievance Redressal Cell (CMPGRC) reference | Government of Kerala | — | B | Kochi | All services (state appellate escalation) |
| https://play.google.com/store/apps/details?id=com.iroads.pwd.pwd4u&hl=en_IN | PWD4U app listing | Public Works Department, Govt. of Kerala (per Play Store listing description) | App store listing | B | Roads (state-wide, jurisdiction-split reference) | Roads & Potholes |
| https://kerala.data.gov.in/ | kerala.data.gov.in OGD portal | Open Government Data (OGD) Platform India — Kerala instance | Dataset portal | C | (national, indexes Kerala datasets) | Waste & Sanitation |

### Maharashtra

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://www.pmc.gov.in/en/grievance-redressal | GRIEVANCE REDRESSAL MECHANISM | Pune Municipal Corporation | HTML | B | Pune | All services (grievance mechanism) |
| https://complaint.pmc.gov.in/ | तक्रार :मुख्यपृष्ठ (Complaint Portal) | Pune Municipal Corporation | Web app | B | Pune | All services (complaint portal) |
| https://www.pmc.gov.in/en/b/pmc-apps-store | PMC Apps Store — PMC Road Mitra | Pune Municipal Corporation | HTML | B | Pune | Roads & Potholes |
| https://services.india.gov.in/service/detail/check-complaint-status-for-pune-municipal-corporation-maharashtra | Check Complaint Status for PMC | National Government Services Portal (Govt. of India) | HTML | B | Pune | All services |
| https://dm.mcgm.gov.in/central-complaint-registration-system | Central Complaint Registration System | BMC / Disaster Management, MCGM | HTML | B | Mumbai | All services |
| https://portal.mcgm.gov.in/irj/portal/anonymous/qlcomplaintreg?guest_user=english | Lodging Civic Complaints / Complaint Registration | BMC (MCGM) | Web form | B | Mumbai | All services |
| https://www.mcgm.gov.in/irj/go/km/docs/documents/MCGM%20Department%20List/ChiefEngineerSolidWasteManagement/RTI%20Manuals/CESWM_RTI_E02.pdf | Solid Waste Management dept RTI Manual (Sec 4(1)(b)) | BMC — Chief Engineer, Solid Waste Management | PDF | A | Mumbai | Waste & Sanitation | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://portal.mcgm.gov.in/irj/portal/anonymous/qltendersswm_new | Solid Waste Management (portal section) | BMC (MCGM) | HTML | B | Mumbai | Waste & Sanitation |
| https://portal.mcgm.gov.in/irj/portal/anonymous/qlwardc?guest_user=english | WardC — MyBMC | BMC (MCGM) | HTML | B | Mumbai | All services (ward-level) |
| https://www.nmcnagpur.gov.in/grievance/ | Grievance Redressal System — NMC | Nagpur Municipal Corporation | HTML | B | Nagpur | All services |
| https://nmcnagpur.gov.in/grievance/complaint_form.php | New Complaint Registration | Nagpur Municipal Corporation | Web form | B | Nagpur | All services |
| https://grievanceigr.maharashtra.gov.in/home/contactus | Grievance Redressal System (IGR) | Government of Maharashtra | HTML | B | (state-wide) | All services |
| https://www.data.gov.in/catalog/solid-waste-managementpune | Solid Waste Management: Pune (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | Dataset (catalog) | C | Pune | Waste & Sanitation |
| https://www.data.gov.in/resource/solid-waste-management-efficiency-thane-2021 | Solid Waste Management Efficiency in Thane : 2021 | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | Dataset | C | Thane | Waste & Sanitation |
| https://www.data.gov.in/resource/d19-solidwastedisposal | D19-SolidWasteDisposal | data.gov.in OGD Platform India | Dataset | C | (national, indexes all states) | Waste & Sanitation |

### Odisha

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://www.bmc.gov.in/services/sanitation-services | Sanitation Services — BMC | Bhubaneswar Municipal Corporation (BMC) | HTML | B | Bhubaneswar | Waste & Sanitation |
| https://www.bmc.gov.in/services/street-lighting | Street Lighting — BMC | Bhubaneswar Municipal Corporation | HTML | B | Bhubaneswar | Streetlights |
| https://www.bmc.gov.in/services/water-supply-services | Water Supply Services — BMC | Bhubaneswar Municipal Corporation (references PHED as actual supplier) | HTML | B | Bhubaneswar | Water & Drainage |
| https://pheoodisha.gov.in/view-portal-services/2 | Public Health Engineering Organization (PHEO), Odisha — Services | PHED/PHEO Odisha — state department, NOT BMC | HTML | B | Bhubaneswar | Water & Drainage |
| https://pheoodisha.gov.in/portal-contact-us/8 | Contact Us — PHEO Odisha | PHED/PHEO Odisha | HTML | B | Bhubaneswar | Water & Drainage |
| https://citizenservices.bhubaneswar.me/grievance/complaint-registration/grievance | State e-Services Portal — Bhubaneswar Me (grievance) | Bhubaneswar Municipal Corporation, Bhubaneswar Smart City Ltd (BSCL), Bhubaneswar Development Authority (BDA), Capital Region Urban Transport (CRUT) — unified helpline | Web app | B | Bhubaneswar | All services (unified grievance) |
| https://sujog.odisha.gov.in/Deshboard/images/Citizen%20Charter_HUD_Final.pdf | CITIZEN'S CHARTER (Draft) — Housing & Urban Development Department | Government of Odisha — Housing & Urban Development (H&UD) Department, via SUJOG | PDF | A | Bhubaneswar / state-wide | All services (Housing & Urban Development Dept. citizen charter) |
| https://sujog.odisha.gov.in/ | SUJOG — Sustainable Urban Services in a Jiffy | Government of Odisha, H&UD Department | Web app | B | (state-wide) | All services (SUJOG e-governance platform) |
| https://sujog.odisha.gov.in/wns | Services / Water & Sewerage — SUJOG | Government of Odisha, H&UD Department | Web app | B | (state-wide) | Water & Drainage (SUJOG module) |
| https://sujog.odisha.gov.in/pgr | Public Grievance Redressal — SUJOG | Government of Odisha, H&UD Department | Web app | B | (state-wide) | All services (public grievance escalation) |
| https://health.odisha.gov.in/sites/default/files/2024-08/23017%2006082024%20Notification%20formal%20platform%20for%20grievance%20%28E%29.pdf | Notification — formal platform for grievance redressal | Government of Odisha — General Administration & Public Grievance Department | PDF | B | (state-wide, general grievance system, not urban-specific) | All services (escalation levels) |
| https://sujogportal.odisha.gov.in/cuttack/service/complaints/ | Public Grievance Redressal — Cuttack Municipal Corporation | Cuttack Municipal Corporation (CMC), via SUJOG | Web app | B | Cuttack | All services (grievance) |
| https://cmccuttack.odisha.gov.in/index.php/2559-2/ | Grievance — Cuttack Municipal Corporation | Cuttack Municipal Corporation | HTML | B | Cuttack | All services (grievance, CMC own site) |
| https://sujogportal.odisha.gov.in/cuttack/service/water-tax/ | Water & Sewerage — Cuttack, SUJOG | Cuttack Municipal Corporation, via SUJOG | Web app | B | Cuttack | Water & Drainage |
| https://sujogportal.odisha.gov.in/rourkela/service/complaints/ | Public Grievance Redressal — Rourkela Municipal Corporation | Rourkela Municipal Corporation (RMC), via SUJOG | Web app | B | Rourkela | All services (grievance) |
| https://rmc.nic.in/eservices.html | e-Services — Rourkela Municipal Corporation | Rourkela Municipal Corporation | HTML | B | Rourkela | All services (RMC own site) |

### Tamil Nadu

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://chennaicorporation.gov.in/gcc/complaints/ | Public Grievance and Redressal System (PGR) | Greater Chennai Corporation (GCC) | HTML | B | Chennai | All services (complaint portal) |
| https://erp.chennaicorporation.gov.in/pgr/citizen/BeforeReg.do | GCC Public Grievance Redressal — citizen registration | Greater Chennai Corporation | Web form | B | Chennai | All services (PGR web app) |
| https://chennaicorporation.gov.in/gcc/department/storm-water/ | Integrated Storm Water Drain — GCC department page | Greater Chennai Corporation | HTML | B | Chennai | Roads & Potholes / Drainage |
| https://cmwssb.tn.gov.in/complaints-grievance | Complaints and Grievance — CMWSSB | Chennai Metropolitan Water Supply and Sewerage Board (CMWSSB), NOT GCC | HTML | B | Chennai | Water & Drainage |
| https://cmwssb.tn.gov.in/citizencharter | Citizen's Charter — CMWSSB | Chennai Metropolitan Water Supply and Sewerage Board | HTML | B | Chennai | Water & Drainage |
| https://cmwssb.tn.gov.in/complaint-redressal | Complaint Redressal — CMWSSB | Chennai Metropolitan Water Supply and Sewerage Board | HTML | B | Chennai | Water & Drainage |
| https://tn.data.gov.in/catalog/solid-waste-management-chennai-6 | Solid Waste Management : Chennai (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via tn.data.gov.in | Dataset (catalog) | C | Chennai | Waste & Sanitation |
| https://www.data.gov.in/catalog/vehicles-and-land-used-solid-waste-management | Vehicles and Land used for Solid Waste Management | data.gov.in OGD Platform India | Dataset | C | (state-wide, applies to all ULBs) | Waste & Sanitation |
| https://www.tnurbantree.tn.gov.in/ | tnurbantree.tn.gov.in — Urban e-Governance / Government Orders | Directorate of Municipal Administration, Tamil Nadu (covers all municipalities/corporations except Chennai) | HTML | B | (state-wide) | All services (Directorate of Municipal Administration) |
| https://ccmc.gov.in/img/upload/CitizensCharterEnglish1.pdf | Coimbatore City Municipal Corporation Citizen's Charter (PDF) | Coimbatore City Municipal Corporation (CCMC) | PDF | A | Coimbatore | All services (citizen charter) | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://ccmc.gov.in/index.php/administration/citizen-charter | Citizen Charter — Coimbatore City Municipal Corporation | CCMC | HTML | A | Coimbatore | All services (citizen charter, HTML) |
| https://payment.ccmc.gov.in/frmGrievancesRegistration.asp | Grievance Registration — CCMC | CCMC | Web form | B | Coimbatore | All services (grievance registration) |
| https://www.data.gov.in/catalog/solid-waste-management-coimbatore | Solid Waste Management : Coimbatore (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in | Dataset (catalog) | C | Coimbatore | Waste & Sanitation |
| https://www.tnurbantree.tn.gov.in/madurai/citizen-charter/ | Citizen Charter — Madurai Corporation | Madurai City Municipal Corporation, hosted via tnurbantree.tn.gov.in (Directorate of Municipal Administration) | HTML | B | Madurai | All services (citizen charter) |
| https://madurai.nic.in/service/how-to-lodge-a-grievance/ | How to lodge your Grievance — Madurai District | District Administration, Madurai (Government of Tamil Nadu, NIC) | HTML | B | Madurai | All services (grievance channel, district) |
| https://www.data.gov.in/catalog/solid-waste-management-madurai | Solid Waste Management : Madurai (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in | Dataset (catalog) | C | Madurai | Waste & Sanitation |
| https://tnega.tn.gov.in/projects/e-sevai | Tamil Nadu e-Sevai Portal (TNeGA) | Tamil Nadu e-Governance Agency | HTML | B | (state-wide) | All services (state escalation) |

### Telangana

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://www.ghmc.gov.in/CitizenCharter/CitizenCharter-19.06.pdf | Citizen's Charter — Hyderabad | Greater Hyderabad Municipal Corporation (GHMC) | PDF | A | Hyderabad | All services (Citizen's Charter) | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://igs.ghmc.gov.in/ | Grievances — Integrated Grievance System (IGS) | GHMC | Web app | A | Hyderabad | All services (grievance system) |
| https://ghmconlinegrievance.cgg.gov.in/ | GHMC Online Grievance | GHMC, hosted via Centre for Good Governance (cgg.gov.in) | Web app | B | Hyderabad | All services (grievance system, alt.) |
| https://www.hyderabadwater.gov.in/application/files/7417/3185/0800/updated_citizen_charter.pdf | Citizen's Charter of HMWSSB | Hyderabad Metropolitan Water Supply & Sewerage Board (HMWSSB) — separate statutory board, NOT GHMC | PDF | A | Hyderabad | Water & Drainage | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://www.hyderabadwater.gov.in/en/index.php/contact-us | Contact Us — HMWSSB | HMWSSB | HTML | A | Hyderabad | Water & Drainage |
| https://gwmc.gov.in/grievance_registration.aspx | Grievance Registration — GWMC | Greater Warangal Municipal Corporation (GWMC) | Web form | A | Warangal | All services (grievance mechanism) |
| https://gwmc.gov.in/ContactUs_New.aspx | Contact Us — GWMC | GWMC | HTML | A | Warangal | All services (contact) |
| https://emunicipal.telangana.gov.in/Grievance_Redressal | Grievance Redressal — CDMA / MA&UD | Commissioner and Director of Municipal Administration (CDMA), MA&UD Dept., Govt. of Telangana | HTML | B | (state-wide) | All services |
| https://www.telangana.gov.in/departments/municipal-administration-urban-development/ | Municipal Administration & Urban Development | Telangana State Portal | HTML | B | (state-wide) | All services |
| https://www.data.gov.in/catalog/solid-waste-disposal-warangal | Solid Waste Disposal : Warangal (dataset) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | Dataset (catalog) | C | Warangal | Waste & Sanitation |
| https://smartcities.data.gov.in/resources/solid-waste-collection-vehicle-warangal-2019 | Solid Waste Collection Vehicle : Warangal 2019 | MoHUA Smart Cities Mission, via Smart Cities Mission Data Portal | Dataset | C | Warangal | Waste & Sanitation |

### Uttar Pradesh

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://lmc.up.nic.in/ | Official website | Lucknow Municipal Corporation (LMC) | HTML | B | Lucknow | All services, Waste & Sanitation |
| https://services.india.gov.in/service/detail/grievances-for-lucknow-municipal-corporation-uttar-pradesh-1 | Grievances for Lucknow Municipal Corporation | National Government Services Portal (Govt. of India) | HTML | B | Lucknow | All services (grievance mechanism) |
| https://e-nagarsewaup.gov.in/ | e-NagarSewa UP — ULB Integrations / Online Complaint | Directorate of Local Bodies, Govt. of Uttar Pradesh | Web portal | B | (state-wide, applies to Lucknow/Varanasi/Bareilly ULBs) | All services |
| http://e-nagarsewaup.gov.in/ulbapps/Grievance/onlineComplaint.jsp | e-NagarSewa Online Complaint form | Directorate of Local Bodies, Govt. of Uttar Pradesh | Web form | B | (state-wide) | All services |
| http://www.jklmc.in/ (referenced; not independently opened) | Lucknow Jal Sansthan online complaint system | Lucknow Jal Sansthan / Jal Kal Vibhag | Web app | B | Lucknow | Water & Drainage |
| https://jn.upsdc.gov.in/ | Official Website of Jal Nigam, Uttar Pradesh | Uttar Pradesh Jal Nigam (Urban) | HTML | B | Lucknow | Water & Drainage (state utility, general) |
| https://iccc.smartcities.gov.in/icc/city-details/8b0afddce19abe9d79637044539da127 | Integrated Command and Control Centre (ICCC) — Lucknow | Smart Cities Mission, Govt. of India | HTML | B | Lucknow | Streetlight / Smart City |
| https://lucknowsmartcity.com/ | Lucknow Smart City Portal | Lucknow Smart City Ltd. / Lucknow Municipal Corporation | HTML | B | Lucknow | Streetlight / Smart City |
| https://nnvns.org.in/ | Home — Varanasi Nagar Nigam | Varanasi Nagar Nigam (NNVNS) | HTML | B | Varanasi | All services |
| https://nnvns.org.in:449/nnvns/index.php?option=com_content&view=article&id=57&Itemid=396&lang=en | Departments — Varanasi Nagar Nigam | Varanasi Nagar Nigam (NNVNS) | HTML | B | Varanasi | All services (departments) |
| http://www.jalkalvaranasi.org/pgr/comlaint1.php | Jalkal Varanasi Public Grievance and Redressal System (PGR) | Jal Kal Vibhag, Varanasi Nagar Nigam | Web app | B | Varanasi | Water & Drainage |
| https://varanasi.nic.in/service/how-to-lodge-a-grievance/ | How to lodge a Grievance? | District Varanasi, Government of Uttar Pradesh | HTML | B | Varanasi | All services (grievance escalation) | **[CHECKED — 404, page no longer exists. Not usable, not re-tried. Uttar Pradesh remains 0 verified.]** |
| https://nagarnigambareilly.com/citizen-charter.php | Citizen Charter — Nagar Nigam Bareilly | Bareilly Nagar Nigam | HTML | B | Bareilly | All services (citizen charter) |
| https://nagarnigambareilly.com/addcomplaint.php | Grievances Redressal System — Nagar Nigam Bareilly | Bareilly Nagar Nigam | Web form | B | Bareilly | All services (grievance) |
| https://nagarnigambareilly.com/Download/DOOR_TO_DOOR_COLLECTION.pdf | Door to Door Collection (MSW) — official PDF | Bareilly Nagar Nigam | PDF | B | Bareilly | Waste & Sanitation |
| https://nagarnigambareilly.com/Download/CITY_SANITATION_PLAN.pdf | City Sanitation Plan for Bareilly | Bareilly Nagar Nigam | PDF | B | Bareilly | Waste & Sanitation |
| https://services.india.gov.in/service/detail/grievances-for-bareilly-municipal-corporation-uttar-pradesh-1 | Grievances for Bareilly Municipal Corporation | National Government Services Portal (Govt. of India) | HTML | B | Bareilly | All services (grievance) |
| https://www.data.gov.in/resource/waste-collection-vehicle-data-lucknow2019 | Waste Collection Vehicle Data: Lucknow: 2019 | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | Dataset | C | Lucknow | Waste & Sanitation |
| https://www.data.gov.in/resource/solid-waste-management-efficiency-prayagraj-2018 | Solid Waste Management-Efficiency: Prayagraj: 2018 | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | Dataset | C | Prayagraj | Waste & Sanitation |
| https://www.data.gov.in/resource/solid-waste-disposal-varanasi-2018 | Solid Waste Disposal in Varanasi: 2018 | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | Dataset | C | Varanasi | Waste & Sanitation |
| https://www.data.gov.in/catalog/solid-waste-management-kanpur-nagar | Solid Waste Management: Kanpur Nagar (catalog) | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | Dataset (catalog) | C | Kanpur Nagar | Waste & Sanitation |

### West Bengal

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://www.kmcgov.in/KMCPortal/jsp/ComplaintProcedure.jsp | Complaint Procedure — Official Website of KMC | Kolkata Municipal Corporation | HTML | B | Kolkata | All services (complaint procedure) |
| https://www.kmcgov.in/KMCPortal/ComplaintFormAction.do | KMC Common Complaint e-Form | Kolkata Municipal Corporation | Web form | B | Kolkata | All services (complaint form) |
| https://www.kmcgov.in/KMCPortal/jsp/CitizenCharter.jsp | Citizen Charter — Official Website of KMC | Kolkata Municipal Corporation | HTML | B | Kolkata | All services (citizen charter) |
| https://www.kmcgov.in/KMCPortal/jsp/Solid_Waste_Services.html | Solid Waste Management Services | Kolkata Municipal Corporation | HTML | A | Kolkata | Waste & Sanitation | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://www.kmcgov.in/KMCPortal/jsp/SolidWasteFAQs.jsp | Solid Waste FAQs | Kolkata Municipal Corporation | HTML | A | Kolkata | Waste & Sanitation |
| https://www.kmcgov.in/KMCPortal/jsp/Water_Supply.html | Water Supply Department page | Kolkata Municipal Corporation | HTML | A | Kolkata | Water & Drainage (water supply) |
| https://www.kmcgov.in/KMCPortal/downloads/citizens_charter_water_supply.pdf | Citizens' Charter — Water Supply Department | Kolkata Municipal Corporation | PDF | A | Kolkata | Water & Drainage (water supply — citizen charter) | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://www.kmcgov.in/KMCPortal/downloads/citizens_charter_water_supply_2016.pdf | Citizen's Charter of Water Supply Department (2016) | Kolkata Municipal Corporation | PDF | A | Kolkata | Water & Drainage (water supply — citizen charter, dated version) |
| https://www.kmcgov.in/KMCPortal/jsp/WaterConnection.jsp | How to get Water Connection in Your New House? | Kolkata Municipal Corporation | HTML | B | Kolkata | Water & Drainage (new connection) |
| https://www.kmcgov.in/KMCPortal/jsp/SewerageAndDrainageServices.jsp | Sewerage and Drainage Services | Kolkata Municipal Corporation | HTML | A | Kolkata | Water & Drainage (sewerage/drainage) |
| https://www.kmcgov.in/KMCPortal/jsp/Manholes.jsp | Manholes — report to Control Room/Borough Office | Kolkata Municipal Corporation | HTML | A | Kolkata | Water & Drainage (manholes) |
| https://www.kmcgov.in/KMCPortal/jsp/Roads.jsp | Roads Dept. — Official Website of KMC | Kolkata Municipal Corporation | HTML | A | Kolkata | Roads & Potholes | **[CHECKED — page loads, but content is only a table of completed civil-works project statistics (km resurfaced, cost, by year) with no complaint procedure, SLA, or contact info for a citizen reporting a pothole. Not usable as a KnowledgeRecord; downgraded to reference-only.]** |
| https://www.kmcgov.in/KMCPortal/jsp/RoadsContact.jsp | Roads Dept. Contact | Kolkata Municipal Corporation | HTML | A | Kolkata | Roads & Potholes (contact) |
| https://www.kmcgov.in/KMCPortal/jsp/KMCRoadDevelopmentDetails.jsp | List of KMC Road Development Scheme | Kolkata Municipal Corporation | HTML | B | Kolkata | Roads & Potholes (development scheme) |
| https://www.kmcgov.in/KMCPortal/jsp/KMCStreetLight.jsp | Street Lighting — Official Website of KMC | Kolkata Municipal Corporation | HTML | A | Kolkata | Streetlights | **[PROMOTED TO VERIFIED — see knowledge_records/verified/, sources/inventory.json]**
| https://www.kmcgov.in/KMCPortal/jsp/Lighting.html | Lighting Services | Kolkata Municipal Corporation | HTML | A | Kolkata | Streetlights |
| https://www.myhmc.in/contacts/ | Contacts — Howrah Municipal Corporation | Howrah Municipal Corporation (HMC) | HTML | B | Howrah | All services |
| https://www.myhmc.in/grs/ | HMC-GRS — Complaint Submission | Howrah Municipal Corporation | Web form | B | Howrah | All services (complaint submission) |
| https://www.myhmc.in/grs/viewgrsticket.php | View Complaint Status — HMC-GRS | Howrah Municipal Corporation | Web app | B | Howrah | All services (status check) |
| https://howrah.gov.in/service/hmc-related-services/ | HMC related services | District Howrah, Government of West Bengal | HTML | B | Howrah | All services (district portal reference) |
| https://cmo.wb.gov.in/default1.aspx | Our Vision — CMO Grievance Cell (Public Grievance Monitoring System, PGMS) | Government of West Bengal, Chief Minister's Office | HTML | B | (state-wide) | All services (escalation) |
| https://pwd.wb.gov.in/general/login?module=grievance | PWD West Bengal grievance login | Public Works Department, West Bengal | Web app | B | (state-wide) | Roads & Potholes (state PWD, jurisdiction-split reference) |
| https://udma.wb.gov.in/ | Department of Urban Development & Municipal Affairs | Government of West Bengal | HTML | B | (state-wide) | Urban Development (department) |
| https://www.data.gov.in/catalog/solid-waste-managementnewtownkolkata | Solid Waste Management_NewTown_Kolkata | Ministry of Housing & Urban Affairs — Smart Cities Mission, via data.gov.in OGD | Dataset (catalog) | C | New Town, Kolkata | Waste & Sanitation |
