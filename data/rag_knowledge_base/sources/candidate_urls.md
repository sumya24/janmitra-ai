# RAG Knowledge Base — Source Research Log

## Round 5, continued: Priority-2 partial-coverage sweep (2026-08-14, same session)

Follow-up pass at the 10 Priority-2 partial-coverage gaps flagged for this round. Time allowed a
real attempt at 6 of the 10; the other 4 (Bengaluru, Bhopal/Indore, Varanasi) were not reached this
pass. 1 city (Ahmedabad) produced 3 new records; the rest came up empty after a genuine attempt.

| City / Gap | Result | Notes |
|---|---|---|
| **Ahmedabad, Gujarat (Water/Drainage + Roads/Streetlights)** | **PROMOTED TO VERIFIED (3 records)** | **[PROMOTED TO VERIFIED — see knowledge_records/verified/gujarat/ahmedabad.json (GJ_AMC_AMCCRS_WATER_DRAINAGE_CHANNEL, GJ_AMC_AMCCRS_ROADS_CHANNEL, GJ_AMC_AMCCRS_STREETLIGHT_CHANNEL), sources/inventory.json. AMC's own AMCCRS portal (amccrs.com) — a genuinely different domain from the TLS-blocked ahmedabadcity.gov.in confirmed exhausted in round 4 — gave real, specific complaint categories for all 3 gap categories, plus a real 24x7 toll-free (155303), SMS shortcode (56767), email, and WhatsApp channel, all confirmed via direct fetch of the AMCCRS homepage itself (not just a WebSearch summary). No numeric SLA published. Closes Ahmedabad's Water gap entirely and its Roads/Streetlights gap (previously only Surat had these).]** |
| **Patna, Bihar (Water/Roads/Streetlights)** | **NO NEW RECORDS** | **[CHECKED — pmc.bihar.gov.in/drainage.aspx gives only the same general PMC office contact already recorded for Waste (0612-2223791), no drainage-specific content. Guessed URLs for a Water Board Details page and a Street Lights Installation page both returned empty content. The Citizen Charter landing page still does not link to an actual downloadable charter document. Patna's Water/Roads/Streetlights gaps remain open.]** |
| **Gurugram, Haryana (Water/Roads/Streetlights)** | **NO NEW RECORDS** | **[CHECKED — mcg.gov.in/GriMaster.aspx returns only a page title, no body content (same JS-rendering issue confirmed for mcg.gov.in generally in an earlier round). wssbilling.mcg.gov.in (a subdomain found via search) fails DNS resolution entirely (ENOTFOUND). A real LED-streetlight toll-free number (18001803580) was found only via a WebSearch-surfaced tweet from MCG's own account — not independently confirmed via a direct fetch of an official page, so NOT promoted per the primary-source-only rule. Gurugram's gaps remain open.]** |
| **Bengaluru, Karnataka (Roads/Streetlights)** | **NOT ATTEMPTED THIS PASS** | Per the round's own instructions, BBMP/GBA-domain retries were explicitly skipped (confirmed TLS-blocked across 2 prior rounds); no genuinely new non-karnataka.gov.in domain surfaced during this pass's other searches. Remains open. |
| **Bhopal & Indore, Madhya Pradesh (Water/Roads/Streetlights)** | **CONFIRMED DEAD END (Bhopal)** | **[CHECKED — bhopalmunicipal.com (the alternate domain suggested for this round) returns HTTP 403 Forbidden on direct fetch. bmconline.gov.in remains confirmed-empty from round 4. A real general phone/email (+91-755-2701222, commoffice@bmconline.gov.in) surfaced only via WebSearch, never independently confirmed via a direct fetch of an official page, so NOT promoted. Indore was not re-attempted this pass (imcindore.mp.gov.in already confirmed empty twice). Both remain open.]** |
| **Lucknow, Uttar Pradesh (Water/Roads/Streetlights)** | **NO NEW RECORDS** | **[CHECKED — the one specific PDF found via search (lmc.up.nic.in/ViewPDF.ashx?Id=506) was fetched and fully read via the Read-tool-on-saved-PDF workaround: it is a real LMC document, but a 2016 PPP tender notice for a housing scheme, completely unrelated to citizen complaint SLAs. It does confirm a real general LMC phone/fax (0522-2622440) and email (nnlko@up.nic.in), already redundant with what's likely available elsewhere. Lucknow's Water/Roads/Streetlights gaps remain open.]** |
| **Varanasi, Uttar Pradesh (Roads/Streetlights)** | **NOT ATTEMPTED THIS PASS** | Not reached due to time; remains open. |
| **Howrah, West Bengal (Waste/Water/Streetlights)** | **NO NEW RECORDS** | **[CHECKED — myhmc.in/grs/ (grievance system) and myhmc.in/departments-2/ both return HTTP 403 Forbidden on direct fetch (the domain appears to block automated/bot requests generally). A real toll-free number (1800 121 500 000) and support line (033-2638 3211) surfaced only via WebSearch, never independently confirmed via a direct fetch, so NOT promoted. Howrah's Waste/Water/Streetlights gaps remain open (only the state-wide WB PWD Roads record currently covers Howrah).]** |

### Net result of the Priority-2 pass

3 new VERIFIED records (Ahmedabad only). 5 of the remaining 9 gaps (Patna, Gurugram, Bhopal,
Lucknow, Howrah) were genuinely attempted and confirmed still-open with specific reasons logged.
4 (Delhi Streetlights, Bengaluru, Indore, Varanasi) were not reached this pass due to time —
flagged as remaining work for a follow-up round.

## Round 5 (2026-08-14, session 5): first pass at Priority-1 zero-coverage cities

Large push targeting the 10 cities that previously had ONLY synthetic placeholders (never
researched at all), plus a planned Priority-2 sweep of partial-coverage gaps. This entry covers
the Priority-1 portion completed this pass: 8 of 10 cities produced real, promotable VERIFIED
records (13 total); 2 (Jodhpur, and Vijayawada beyond what's noted) did not.

| City / State | Result | Notes |
|---|---|---|
| **Vijayawada, Andhra Pradesh** | **NO NEW RECORDS** | **[CHECKED — `vijayawada.cdma.ap.gov.in` (a real, working ULB-profile subdomain, distinct from the blocked `ourvmc.org`) was fetched directly: its Grievances Dashboard and Contact pages are both client-rendered shells with zero static content ("No category data available"). A follow-up lead via the 2003-era "Citizen's Charters of Select Departments of GoAP" compilation (cgg.gov.in) was fully read (25+ pages) -- it is real and does contain a generic Municipal Administration/Urban Local Bodies section with real day-based grievance times (garbage 1 day, drains 2 days, streetlights 5 days, road cuts 7 days) but is a **pre-2014 undivided-Andhra-Pradesh** state circular, not specific to Vijayawada or current-day AP -- attributing it to "Vijayawada" would misrepresent its actual scope, so NOT promoted. Vijayawada remains open.]** |
| **Gaya, Bihar** | **PROMOTED TO VERIFIED** | **[PROMOTED TO VERIFIED — see knowledge_records/verified/bihar/gaya.json (BR_GMC_GENERAL_GRIEVANCE_CHANNEL), sources/inventory.json. Real toll-free number (1800 121 8545) confirmed via direct fetch of gayamunicipal.net; general channel only, SLA NOT FOUND. Gaya's first-ever real record.]** |
| **New Delhi (NDMC)** | **PROMOTED TO VERIFIED (3 records)** | **[PROMOTED TO VERIFIED — see knowledge_records/verified/delhi/new_delhi.json (DL_NDMC_WATER_SLA, DL_NDMC_ROADS_SLA, DL_NDMC_GENERAL_GRIEVANCE_CHANNEL), sources/inventory.json. ndmc.gov.in/SLA.aspx gave real numeric SLAs (new water connection 35 days, tanker booking 1 day, manhole covers 2 days, road obstruction removal 1 day, road-cutting permission 7 days); ndmc.gov.in/complaints.aspx gave real general-channel contacts (1533, WhatsApp, NDMC 311 app) for waste/streetlights, SLA NOT FOUND for those two. NDMC is confirmed as a genuinely distinct civic authority from Delhi's MCD, already covered separately in delhi/delhi.json. NDMC's first-ever real records.]** |
| **Faridabad, Haryana** | **PROMOTED TO VERIFIED (thin)** | **[PROMOTED TO VERIFIED — see knowledge_records/verified/haryana/faridabad.json (HR_MCF_GENERAL_GRIEVANCE_CHANNEL), sources/inventory.json. The Solid Waste Bye-laws 2019 PDF flagged unreadable in round 3 was RE-FETCHED and successfully read in FULL this pass (25 pages) via the Read-tool-on-saved-PDF workaround -- confirmed genuinely real (Municipal Corporation Faridabad, effective 01-01-2021, signed by the Commissioner) but confirmed to contain NO complaint-SLA content at all; it is purely a generator-obligations/segregation-rules/fines-schedule document. Real general contact number (0129-2416464) confirmed instead via faridabad.nic.in. Faridabad's first-ever real record.]** |
| **Mysuru, Karnataka** | **PROMOTED TO VERIFIED (thin)** | **[PROMOTED TO VERIFIED — see knowledge_records/verified/karnataka/mysuru.json (KA_MCC_GENERAL_GRIEVANCE_CHANNEL), sources/inventory.json. MCC's own domain (mysurucity.mrc.gov.in) failed with ECONNREFUSED on 2 separate attempts -- a DIFFERENT failure class from the karnataka.gov.in/bbmp.gov.in TLS cert-chain issue confirmed in rounds 3-4, meaning this is not simply "the same Karnataka block" — genuinely a separate connectivity issue on MCC's own domain. Fell back to the district portal (mysore.nic.in) for a real, confirmed general contact (phone + email), SLA NOT FOUND. Mysuru's first-ever real record.]** |
| **Thiruvananthapuram, Kerala** | **PROMOTED TO VERIFIED (2 records)** | **[PROMOTED TO VERIFIED — see knowledge_records/verified/kerala/thiruvananthapuram.json (KL_TVM_WATER_SEPTAGE_CHANNEL, KL_TVM_STREETLIGHT_CHANNEL), sources/inventory.json. The Smart Trivandrum civic services portal (smarttvm.tmc.lsgkerala.gov.in) gave real, distinct 24x7 help-desk numbers for Water/Septage and Street Lights. No numeric complaint-SLA published (only an aggregate "92% within SLA" statistic and a 2-hour tanker-delivery window, which is a service window not a complaint SLA). A separate Citizen Charter page (tmc.lsgkerala.gov.in/en/citizen--charter) links to a PDF ("Pauravakasha Rekha.pdf") not yet mined -- flagged as a follow-up lead. Thiruvananthapuram's first-ever real records.]** |
| **Nagpur, Maharashtra** | **PROMOTED TO VERIFIED** | **[PROMOTED TO VERIFIED — see knowledge_records/verified/maharashtra/nagpur.json (MH_NMC_WATER_RTS_SLA), sources/inventory.json. NMC's own Right to Services (RTS) Act page (nmcnagpur.gov.in/nmc-rts) gave real numeric SLAs for water services (new connection 15 days, billing/no-dues 3 days, reconnection 15 days). The page does not cover roads/streetlights/waste specifically. NMC's /grievance and /grievance-redressal pages were also checked but had no numeric SLA or department contacts. Nagpur's first-ever real record.]** |
| **Jodhpur, Rajasthan** | **NO NEW RECORDS** | **[CHECKED — jodhpurmc.org's homepage returned empty content on direct fetch; no citizen charter, SLA, or department-contact page could be located via WebSearch either (only third-party aggregator/social-media mentions of a "Jodhpur-311" app). Jodhpur remains fully open -- worth a dedicated retry with different URL guesses in a future round.]** |
| **Chennai, Tamil Nadu** | **PROMOTED TO VERIFIED (3 records)** | **[PROMOTED TO VERIFIED — see knowledge_records/verified/tamil_nadu/chennai.json (TN_GCC_WASTE_ROADS_CLEANING_CONTACT, TN_GCC_STREETLIGHT_CONTACT, TN_GCC_ROADS_MAINTENANCE_CONTACT), sources/inventory.json. GCC's own complaints directory (chennaicorporation.gov.in/gcc/complaints/) gave a rich, real, named-officer directory with direct phone numbers for road/street cleaning, streetlight complaints, and road maintenance, including 15 zone-specific Executive Engineer numbers -- comparable richness to Jaipur's charter, though without numeric SLAs. Water supply/drainage was not listed on this specific page and remains open for Chennai. Chennai's first-ever real records (distinct from Coimbatore, already covered).]** |
| **Warangal, Telangana** | **PROMOTED TO VERIFIED (thin)** | **[PROMOTED TO VERIFIED — see knowledge_records/verified/telangana/warangal.json (TS_GWMC_GENERAL_GRIEVANCE_CHANNEL), sources/inventory.json. gwmc.gov.in -- flagged as a real quality-A lead in the ORIGINAL research pass but never independently fetched until now -- confirmed a real call center number and online grievance portal, but neither gwmc.gov.in/grievance_registration.aspx nor ContactUs_New.aspx published department-specific contacts or numeric SLA. Warangal's first-ever real record.]** |

### Net result of Round 5 (Priority-1 portion)

13 new VERIFIED records across 8 cities that previously had zero real coverage (Gaya, New Delhi/NDMC,
Faridabad, Mysuru, Thiruvananthapuram, Nagpur, Chennai, Warangal). 2 cities (Vijayawada, Jodhpur)
remain fully open after a genuine attempt each. The Priority-2 partial-coverage sweep (Patna, Delhi
streetlights, Ahmedabad, Gurugram, Bengaluru, Bhopal/Indore, Lucknow, Varanasi, Howrah) was not
reached this pass due to the scope of the Priority-1 work -- flagged as remaining work for a
follow-up round.

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


## Fresh research pass: 6 previously-unresearched states (2026-08-14)

Assam, Bihar, Delhi, Haryana, Madhya Pradesh, and Rajasthan had zero prior research (no
`02_source_inventory/` entry existed for any of them) -- WebFetch worked in this session (unlike
the environment that produced the original 10-state pass, where it was fully blocked), so these
were fetched and read directly rather than logged as leads only.

### Assam

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://gmc.assam.gov.in/resource/citizen-charter | Citizen's Charter | Guwahati Municipal Corporation (GMC) | HTML | B | Guwahati | All services (citizen charter) | **[CHECKED — page loads, but covers only certificate/license/permit processing timelines (birth/death certs, building NOC, trade license, property assessment), not civic complaint SLAs for garbage/water/road/streetlight. Not usable as a KnowledgeRecord.]** |
| https://gmc.assam.gov.in/portlets/dissatisfied-let-us-know | Dissatisfied? Let Us Know! (grievance page) | Guwahati Municipal Corporation (GMC) | HTML | A | Guwahati | Waste & Sanitation, Water & Drainage, Roads & Potholes, Streetlights | **[PROMOTED TO VERIFIED — see knowledge_records/verified/assam/guwahati.json, sources/inventory.json. Real named officers for water/general grievances, Swachhata App for waste; roads/streetlights only listed with no named contact on this page.]** |

### Bihar

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://www.pmc.bihar.gov.in/citizen-charter.aspx | Citizen Charter (landing page) | Patna Municipal Corporation (PMC) | HTML | B | Patna | Waste & Sanitation | **[PROMOTED TO VERIFIED (channel-only, SLA NOT FOUND) — see knowledge_records/verified/bihar/patna.json, sources/inventory.json. Links to a fuller Citizen Charter document not reached this pass.]** |
| Bihar Right to Public Services Act, 2011 (indiacode.nic.in / prsindia.org) | Bihar RTPS Act, 2011 | Government of Bihar | PDF/legislation | B | (state-wide) | All services (statutory framework, not yet checked for a municipal-complaint-specific SLA table) | **[NOT YET PURSUED — real act, exists, but no municipal civic-complaint SLA table located this pass. Worth a dedicated fetch of the Act's schedule/annexures.]** |

### Delhi

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://mcdonline.nic.in/portal/citizenCharter | Citizen Charter (Health Trade License) | Municipal Corporation of Delhi (MCD) | HTML | B | Delhi | (covers only trade licenses, birth/death certs, e-mutation, veterinary license — NOT garbage/water/drainage/roads/streetlights) | **[CHECKED — confirmed not usable for civic-complaint SLAs, not assumed.]** |
| https://mcdonline.nic.in/portal/downloadFile/pwm_byelaws_2024_240216075150250.pdf | Plastic Waste Management Bye-laws, 2024 | Municipal Corporation of Delhi (MCD) | PDF | B | Delhi | Waste & Sanitation (plastic-specific regulation, not general garbage-collection complaint SLA) | **[CHECKED — real, live, 5.9MB, dated 23 Jan 2024. Regulatory/prohibition content, not a citizen complaint-response SLA document. Not used as a KnowledgeRecord source for that reason.]** |
| https://mcdonline.nic.in/portal/mService | Services gateway | Municipal Corporation of Delhi (MCD) | HTML | A | Delhi | Waste & Sanitation (general channel) | **[PROMOTED TO VERIFIED (channel-only, SLA NOT FOUND) — see knowledge_records/verified/delhi/delhi.json, sources/inventory.json. Confirms Citizen's Call Center 155305 and MCD311 app.]** |
| https://delhijalboard.delhi.gov.in/jalboard/grievance-redressal-mechanism | Grievance Redressal Mechanism | Delhi Jal Board (DJB) | HTML | A | Delhi | Water & Drainage | **[PROMOTED TO VERIFIED — see knowledge_records/verified/delhi/delhi.json, sources/inventory.json. Real 3-level escalation, 21-day PGC auto-trigger, hotline 1916.]** |
| https://pwddelhi.gov.in/citizen-charter | Citizen Charter | Public Works Department (PWD), Delhi | HTML | B | Delhi | Roads & Potholes, Streetlights | **[PROMOTED TO VERIFIED — see knowledge_records/verified/delhi/delhi.json, sources/inventory.json. General (not category-specific) 24hr-attend/1wk-acknowledge/1mo-interim-reply commitment. Covers PWD-maintained roads only — Delhi's road network is split across PWD/MCD/NHAI by classification.]** |
| https://pwdsewa.pwddelhi.gov.in/Home/SubmitComplaint/ | PWD Sewa — Submit Complaint | Public Works Department (PWD), Delhi | Web app | B | Delhi | Roads & Potholes, Streetlights (complaint submission) | **[UNREACHABLE — DNS resolution failure (`getaddrinfo ENOTFOUND`) from this environment. Real subdomain referenced elsewhere on pwddelhi.gov.in; worth re-attempting.]** |

### Haryana

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://www.mcg.gov.in (homepage, ApplicationsSummary.aspx "Citizen Charter Dashboard") | Municipal Corporation Gurugram (MCG) site | Municipal Corporation Gurugram | HTML (JS-rendered) | — | Gurugram | All services | **[NOT USABLE — site renders via client-side JS; static fetch returns only the page header/title, no body content, across 3 separate attempts (homepage, dashboard page). Real phone numbers (toll-free 18001801817, grievance +911244753555, garbage-specific 18001025952) surfaced via WebSearch's own aggregated answer, but this project's own rule is that a fact must come from a directly-fetched primary source, not a search-engine summary that may itself be drawing from a third-party aggregator (complainthub.org and similar sites appeared in the same search) — so NOT promoted to VERIFIED. A real, worthwhile lead for a human to re-check with a JS-capable browser, or via the mcg.gov.in citizen-charter PDF if one can be located directly.]** |

### Madhya Pradesh

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://cmhelpline.mp.gov.in/About.aspx | About — CM Helpline (181) | Government of Madhya Pradesh | HTML | A | (state-wide) | Waste & Sanitation, Water & Drainage, Roads & Potholes, Streetlights (general channel) | **[PROMOTED TO VERIFIED (state-wide, channel-only, SLA NOT FOUND) — see knowledge_records/verified/madhya_pradesh/statewide.json, sources/inventory.json.]** |
| https://www.smartcityindore.org/citizen-charter/ | Citizen Charter | Smart City Indore (SPV) | HTML | B | Indore | (Smart City *project* complaint timelines — site/design/execution issue SLAs — not general civic-service complaint SLAs) | **[CHECKED — real page, but it's a Smart City Special Purpose Vehicle project-grievance charter, not a municipal civic-service charter. Not usable as a KnowledgeRecord for garbage/water/road/streetlight complaints.]** |
| https://imcindore.mp.gov.in/grievance | Grievance | Indore Municipal Corporation (IMC) | HTML (JS-rendered?) | — | Indore | All services | **[NOT USABLE — static fetch returned no page content. A WebSearch-aggregated answer claimed a 24-hour SLA / 10-working-day review timeline attributed to "IMC's citizen charter," but this could not be independently re-confirmed by directly fetching and quoting a primary page this pass, so it was NOT promoted to VERIFIED, consistent with this project's own sourcing rule. Worth a dedicated re-attempt.]** |

### Rajasthan

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| http://www.jaipurmc.org/PDF/Auction_MM_RTI_Act_Etc_PDF/CitiChar_SP.pdf | Citizen Charter for Different Urban Services and Utilities | Jaipur Municipal Corporation (JMC) | PDF | A | Jaipur | Waste & Sanitation, Water & Drainage, Roads & Potholes, Streetlights | **[PROMOTED TO VERIFIED — see knowledge_records/verified/rajasthan/jaipur.json, sources/inventory.json. The richest source found in this entire project to date: real per-activity min/max SLA tables across all 4 categories, named 3-level escalation chains, and a full page of real per-zone/per-designation phone numbers. 56.7KB, 11-page PDF; the built-in PDF-to-text path failed on this file's encoding (same failure mode as the earlier BBMP bye-law PDF) — worked around by reading the saved PDF directly with a page-rendering tool instead.]** |

## Follow-up leads surfaced by this pass, not yet pursued

- Surat's `NonWorkingStreetlights` page (https://www.suratmunicipal.gov.in/Departments/NonWorkingStreetlights) — fetched this pass. Real page, but contains only a historical monthly non-working-percentage table (Mar 2017 - Feb 2021), no complaint procedure/SLA. The general online complaint portal (`/OnlineServices/complaint/New`) is linked from the same site but wasn't itself fetched/checked this pass.
- Surat's drainage/water pages (`drainageintroduction`, `DrainageHowDoI`, `hydraulichome`) — already logged as quality-A leads in the Gujarat section above, still not fetched; would close Gujarat's Water/Drainage gap if promoted.
- Kolkata's `citizens_charter_water_supply_2016.pdf` (a differently-dated version of the water charter already used) — not compared against the version actually used; check for content drift if both are ever needed.
- MCD's own citizen-charter PDF for general (non-plastic) solid waste bye-laws — not located this pass; the Plastic Waste Management Bye-laws 2024 found instead are real but out of scope for general garbage-collection SLAs.
- Bihar's Right to Public Services Act, 2011 — real statutory framework, not yet checked for a municipal-complaint-specific SLA schedule.
- Haryana (MCG) and Madhya Pradesh (IMC Indore) — both had promising leads that returned no usable static content (JS-rendered sites); worth a re-attempt with a JS-capable fetch or by locating a direct PDF citizen charter instead of the HTML app shell.

## States still with zero verified coverage after this pass

Uttar Pradesh and Haryana. Uttar Pradesh was researched in the original 10-state pass and came
up empty (a genuine dead end, not "not yet started"). Haryana was attempted fresh this pass
(see above) — real leads exist (MCG) but nothing independently fetchable/quotable was found; a
JS-capable browser or a direct PDF citizen-charter search is the likely next step.


## Continued research pass (2026-08-14, session 2): Haryana retry, UP fresh attempt, category gaps

Follow-up to the "6 previously-unresearched states" pass above. This session: retried Haryana
with a different authority (GMDA instead of MCG), attempted UP fresh with real WebFetch (the
original 10-state pass never touched it beyond WebSearch), and filled category gaps in West
Bengal/Gujarat/Kerala/Karnataka/Maharashtra using already-logged candidate URLs plus new leads.

### Haryana (retry)

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://services.gmda.gov.in/ | Services Portal | Gurugram Metropolitan Development Authority (GMDA) | HTML | B | Gurugram | Waste & Sanitation (general channel) | **[PROMOTED TO VERIFIED — see knowledge_records/verified/haryana/gurugram.json, sources/inventory.json. GMDA is distinct from MCG; real toll-free 18001801817 independently confirmed via direct fetch this time (was previously only seen via an unconfirmed WebSearch summary).]** |
| https://ulbharyana.gov.in/Website/Faridabad/Images/c7f73535-d387-4b0d-8cac-a37a78605b0d.pdf | Solid Waste (Management & Handling) Bye-laws, 2019 | Faridabad Municipal Corporation, via Haryana ULB Directorate | PDF | A (real, unusable) | Faridabad | Waste & Sanitation | **[CHECKED — real, live, 6.5MB PDF. Scanned/image-based with no extractable text layer; this environment has no OCR/poppler available. Genuinely real bye-law, just unreadable by current tooling — worth re-attempting with OCR capability.]** |
| https://www.mcg.gov.in (retry, ApplicationsSummary.aspx) | Municipal Corporation Gurugram | MCG | HTML (JS-rendered) | — | Gurugram | All services | **[STILL NOT USABLE on retry — confirmed via direct fetch that mcg.gov.in genuinely is Municipal Corporation of *Gurugram* (not Ghaziabad, despite one ambiguous WebSearch result), but every page attempted returns only the header/title, no body content.]** |
| https://ulbharyana.gov.in/img/pdf/SWM%20Policy%20and%20Strategy%20on%20Solid%20Waste%20Management.pdf | SWM Policy and Strategy | Directorate of Urban Local Bodies, Haryana | PDF | — (dead) | (state-wide) | Waste & Sanitation | **[CHECKED — 404, page removed/moved. Appeared as a live search result but the URL is dead.]** |
| Gurugram Municipal Corporation Solid Waste Management Bylaws, 2025 (draft) | — | MCG | — | — | Gurugram | Waste & Sanitation | **[NOT YET ENACTED — reported via news sources as still awaiting state government approval; not a usable source until finalized and published.]** |

### Uttar Pradesh (fresh attempt with real WebFetch)

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://lmc.up.nic.in | Official Website | Lucknow Municipal Corporation (LMC) | HTML | B | Lucknow | Waste & Sanitation | **[PROMOTED TO VERIFIED — see knowledge_records/verified/uttar_pradesh/lucknow.json, sources/inventory.json. Real Mayor's Office helpline for garbage-overcharging complaints.]** |
| https://jn.upsdc.gov.in | UP Jal Nigam homepage | UP Jal Nigam | HTML | B | (state-wide) | Water & Drainage | **[CHECKED — real contact info (phone, named Web Information Manager) but no citizen charter/SLA on this page. Links to e-nagarsewaup.gov.in.]** |
| https://e-nagarsewaup.gov.in/ | e-Nagar Sewa UP (state ULB citizen services portal) | Government of Uttar Pradesh | HTML | B | (state-wide) | All services | **[NOT USABLE — page only returns a redirect message, no further content reachable this pass.]** |
| https://nnvns.org.in | Varanasi Nagar Nigam homepage | Varanasi Nagar Nigam (VNN) | HTML | A | Varanasi | Waste & Sanitation, Roads & Potholes, Streetlights (general channel + toll-free) | **[CHECKED, led to Citizen Charter page below.]** |
| https://nnvns.org.in/nnvns/index.php?option=com_content&view=article&id=224&lang=en&Itemid=238 | Citizen Charter | Varanasi Nagar Nigam (VNN) | HTML | A | Varanasi | Water & Drainage (real 15-day connection SLA), Waste & Sanitation, Roads & Potholes, Streetlights (general channel) | **[PROMOTED TO VERIFIED — see knowledge_records/verified/uttar_pradesh/varanasi.json, sources/inventory.json.]** |
| https://jalkalvaranasi.org (and /pgr) | Varanasi Jal Kal (water/sewerage board) | Jal Kal Vibhag, Varanasi | HTML | — | Varanasi | Water & Drainage | **[UNREACHABLE — connection refused, 2 separate attempts (base domain and /pgr path).]** |

### West Bengal (Roads gap)

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://pwd.wb.gov.in/general/login?module=grievance | Grievance Portal | Public Works Department, West Bengal | Web app | A | (state-wide, covers Kolkata) | Roads & Potholes | **[PROMOTED TO VERIFIED — see knowledge_records/verified/west_bengal/kolkata.json, sources/inventory.json. Closes the Roads gap left by KMC's own unusable Roads page (see earlier session's log). Real WhatsApp helpline 9073362000, explicitly covers roads/bridges/culverts damage and workmanship complaints.]** |

### Gujarat (Water/Drainage + Roads gaps)

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://www.suratmunicipal.gov.in/departments/hydraulichome | Water Supply (Hydraulic) — Home | Surat Municipal Corporation (SMC) | HTML | A (checked, thin) | Surat | Water & Drainage | **[CHECKED — real page, general complaint channels only (portal, apps), no SLA.]** |
| https://www.suratmunicipal.gov.in/departments/drainageintroduction | Drainage — Introduction | SMC | HTML | A (checked, thin) | Surat | Water & Drainage | **[CHECKED — functions description only, no SLA or contact details.]** |
| https://www.suratmunicipal.gov.in/Departments/DrainageHowDoI | Drainage — How Do I Get a Connection? | SMC | HTML | A | Surat | Water & Drainage | **[PROMOTED TO VERIFIED — see knowledge_records/verified/gujarat/surat.json, sources/inventory.json. Real 15-day connection-approval SLA.]** |
| https://www.suratmunicipal.gov.in/Home/TollFreeNumbers | Toll Free Numbers | SMC | HTML | A | Surat | Roads & Potholes (general channel), Waste & Sanitation (C&D/plastic-specific lines) | **[PROMOTED TO VERIFIED — see knowledge_records/verified/gujarat/surat.json, sources/inventory.json. Used as Surat's general Roads complaint channel (no roads-specific line published).]** |
| https://www.suratmunicipal.gov.in/Departments/RoadDevelopmentHome | Road Development Introduction/Projects | SMC | HTML | A (checked, thin) | Surat | Roads & Potholes | **[CHECKED — completed-project statistics table only, no complaint SLA.]** |
| https://ahmedabadcity.gov.in/portal/jsp/Static_pages/pi_RoadResurfacing.jsp | Road Resurfacing | Ahmedabad Municipal Corporation (AMC) | HTML | A (unreachable) | Ahmedabad | Roads & Potholes | **[UNREACHABLE — SSL certificate verification failure ("unable to verify the first certificate"), same failure class as tnurbantree.tn.gov.in from an earlier pass. Ahmedabad's own Water/Roads gaps remain open; AMC's Comprehensive Complaint Redressal System (155303, already logged elsewhere in this project's Ahmedabad waste record) plausibly covers roads too per a WebSearch summary, but this was not independently confirmed via a directly-fetched primary page, so not promoted.]** |

### Kerala (Waste/Roads/Streetlights gaps)

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://kochicorporation.lsgkerala.gov.in/en/solid-waste-management/368 | Solid Waste Management | Cochin Corporation | HTML | A (checked, thin) | Kochi | Waste & Sanitation | **[CHECKED — only navigation/header content returned, no substantive complaint procedure.]** |
| https://kochicorporation.lsgkerala.gov.in/en/form/public-grievance-cellnew | Public Grievance Cell | Cochin Corporation | Web form | A | Kochi | Waste & Sanitation, Roads & Potholes, Streetlights (general channel) | **[PROMOTED TO VERIFIED — see knowledge_records/verified/kerala/kochi.json, sources/inventory.json. 3 records (Waste/Roads/Streetlights), general channel, no category-specific SLA.]** |

### Karnataka (Water gap; Roads/Streetlights still open)

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://bwssb.karnataka.gov.in/page/Contact+Us/Contact+Info/en | Contact Info | Bangalore Water Supply and Sewerage Board (BWSSB) | HTML | A | Bengaluru | Water & Drainage | **[PROMOTED TO VERIFIED — see knowledge_records/verified/karnataka/bengaluru.json, sources/inventory.json. Real call center 1916, Safai Mitra 14420.]** |
| https://www.bwssb.karnataka.gov.in/all_complaint_details?info=1480 | Complaint details/procedure | BWSSB | HTML | — | Bengaluru | Water & Drainage | **[UNREACHABLE — TLSV1_ALERT_UNRECOGNIZED_NAME (SNI/TLS config issue).]** |
| https://bbmp.sahaaya.in | Sahaaya citizen grievance portal | BBMP | HTML | — | Bengaluru | Roads & Potholes, Streetlights | **[UNREACHABLE — certificate altname mismatch (cert covers *.nammabengaluru.org.in, not this hostname).]** |
| https://sahaaya.nammabengaluru.org.in | Sahaaya (alternate domain) | BBMP | HTML | — | Bengaluru | Roads & Potholes, Streetlights | **[UNREACHABLE — DNS resolution failure.]** |
| https://site.bbmp.gov.in | BBMP official site | BBMP | HTML | — | Bengaluru | Roads & Potholes, Streetlights | **[UNREACHABLE — connection refused.]** |
| BBMP control room 080-22660000, helpline 1533, BESCOM 1912 (streetlight electrical faults) | — | BBMP / BESCOM | — | D (secondary only) | Bengaluru | Roads & Potholes, Streetlights | **[NOT PROMOTED — these numbers surfaced only via WebSearch-aggregated answers citing third-party sites (godigit.com, thinkbangalore.com), never independently confirmed via a directly-fetched primary .gov.in page. Per this project's primary-source-only rule, logged here as an unconfirmed lead, not used as a KnowledgeRecord source. Karnataka's Roads/Streetlights gaps remain genuinely open.]** |

### Maharashtra (Water/Roads/Streetlights gaps + a stronger Waste source)

| URL | Source title | Authority | Format | Quality | Cities | Services |
|---|---|---|---|---|---|---|
| https://portal.mcgm.gov.in/... (Lodging Civic Complaints, Complaint Registration, ContactUs, Water Supply Project pages) | Various | Brihanmumbai Municipal Corporation (BMC/MCGM) | Legacy SAP NetWeaver portal | — | Mumbai | All services | **[SYSTEMATICALLY UNUSABLE — every page on portal.mcgm.gov.in returns only "Could not open iView. The iView is not compatible with your browser..." across 3 separate URLs attempted. This is BMC's primary complaint/contact portal and it is not fetchable by any static tool used this pass.]** |
| https://praja.org/praja_docs/praja_downloads/CITIZEN%20CHARTER.pdf | Citizens' Charter (June 1999) | Municipal Corporation of Greater Mumbai, with PRAJA Foundation | PDF (scanned) | A (real, dated) | Mumbai | Water & Drainage, Roads & Potholes, Streetlights, Waste & Sanitation (supplementary) | **[PROMOTED TO VERIFIED, explicitly flagged OUTDATED / VERIFY BEFORE PRODUCTION — see knowledge_records/verified/maharashtra/mumbai.json, sources/inventory.json. Genuinely MCGM's own signed 1999 charter (Mayor + Municipal Commissioner), hosted by the NGO co-publisher rather than mcgm.gov.in directly — same "real document, third-party-hosted" precedent as the Punjab Patiala charter (Azure blob storage) and BBMP bye-law (India Code) in earlier sessions. 26 years old: every record built from it carries an explicit staleness warning and the phone numbers/contact directory are NOT reproduced in the KnowledgeRecords themselves for that reason (only in this source's own inventory notes, pointing back to the original PDF).]** |

## Follow-up leads surfaced by this session, not yet pursued

- Faridabad's real, live Solid Waste Bye-laws 2019 PDF — needs OCR capability this environment doesn't have.
- Ahmedabad's Roads page and BWSSB's complaint-details page — both blocked by SSL/TLS issues from this environment; a human browser would likely succeed where automated fetch failed.
- BBMP's Sahaaya portal (Roads/Streetlights for Bengaluru) — 3 different hostnames all failed for different technical reasons (cert mismatch, DNS, connection refused); worth a dedicated retry.
- Ahmedabad's own Water/Drainage and Roads categories remain fully open (Surat's were closed this pass; Ahmedabad's were not attempted beyond the failed Roads fetch).
- Varanasi Jal Kal's own dedicated site (jalkalvaranasi.org) — connection refused twice; VNN's general charter was used instead and already covers water with a real SLA, but Jal Kal's own site might have richer detail if it becomes reachable later.

## Round 3 (2026-08-14, session 3): revisiting strongest remaining leads, not a full sweep

Targeted follow-ups on 7 specific leads flagged as strongest-remaining in the previous session, rather
than re-doing full state sweeps. 1 of 7 produced a real, promotable VERIFIED record; the other 6 are
confirmed dead ends (with the specific reason logged for each, per the project's honesty rule).

| URL / target | State | Result | Notes |
|---|---|---|---|
| `https://ulbharyana.gov.in/img/pdf/SWM%20Policy%20and%20Strategy%20on%20Solid%20Waste%20Management.pdf` | Haryana | **DEAD (404)** | **[CHECKED — the URL now returns a 404 error page, not the PDF. Whatever was live at this path in an earlier pass is no longer reachable. Haryana's Waste category remains covered only by GMDA's general-channel record (HR_GMDA_GENERAL_GRIEVANCE), unchanged.]** |
| `https://bbmp.gov.in`, `https://gba.karnataka.gov.in`, `https://support.bbmpgov.in/ehelpline`, `https://ahmedabadcity.gov.in/...` (multiple pages) | Karnataka, Gujarat | **UNREACHABLE (systemic)** | **[CHECKED — every single karnataka.gov.in / bbmp*.in and ahmedabadcity.gov.in URL attempted this round (5 total, both http:// and https://) failed with the identical "unable to verify the first certificate" TLS error, including the AMC PDF `.../PropertyTax_Citizens%20Charter_...pdf` found via search. This is consistent with the SSL cert-chain failures logged against these exact domain families in the previous round (AMC's RoadResurfacing page, BWSSB, BBMP's 3 hostnames) -- confirms this is a systemic TLS-trust-store issue in this environment for Gujarat/Karnataka .gov.in infrastructure specifically, not a URL-specific dead link. BBMP itself was confirmed (via WebSearch, not independently fetched) to have been dissolved 2025-09-02 and replaced by the Greater Bengaluru Authority (GBA) -- so even a working fetch would now need re-scoping to GBA-branded sources. Karnataka Roads/Streetlights and Ahmedabad Water/Drainage+Roads remain genuinely open.]** |
| `https://cdma.ap.gov.in/resources/service-sla`, `https://www.gvmc.gov.in`, `https://cdma.ap.gov.in/sites/default/files/Vijayawada.pdf` | Andhra Pradesh | **DEAD / EMPTY** | **[CHECKED — Vijayawada.pdf (cited by a WebSearch summary as a real SLA-bearing charter) returns HTTP 404. CDMA's own statewide "Service Level Agreements (SLAs)" page at /resources/service-sla is a real, live link but is a client-side-rendered search tool returning "No SLA items found matching your search criteria — Showing 0 of 0 SLA items" with no query applied and no way to browse all items via static fetch. GVMC's own site confirms a "Citizens Charter Rules & Procedures" menu entry exists but no direct URL/PDF for it could be resolved via WebSearch. AP's 4 categories remain covered only by GVMC's generic IVRS/PGRS channel, unchanged.]** |
| `imcindore.mp.gov.in` (both `www.` and bare) | Madhya Pradesh | **EMPTY** | **[CHECKED — page returns genuinely empty content both with and without the www subdomain, same result as the previous round. No citizen charter PDF for Indore Municipal Corporation was located via WebSearch either. The previously-flagged unconfirmed WebSearch claim of a "24hr/10-working-day SLA" for IMC could NOT be confirmed via any direct fetch this round either -- it is NOT promoted and should be treated as unconfirmed, not used. MP remains 1 record (state CM Helpline, channel-only).]** |
| `https://prsindia.org/files/bills_acts/acts_states/bihar/2011/2011Bihar4.pdf`, `https://rtps.bihar.gov.in/rtps/`, `https://pmc.bihar.gov.in/act-rules-policy.aspx` | Bihar | **CONFIRMED FRAMEWORK-ONLY** | **[CHECKED — the Bihar RTPS Act 2011 PDF itself was fetched and read directly; it establishes only the general procedural framework (Designated Public Servants, Appellate/Reviewing Authorities, stipulated time limits to be set by later notification) with no schedule/annexure of actual municipal-service SLAs in this document. The RTPS portal (rtps.bihar.gov.in) lists certificate-type services (caste/income/residence) with no Nagar Nigam/civic-service section. Patna Municipal Corporation's own Acts/Rules/Policy page lists 15 downloadable PDFs (building bylaws, property tax, fire tax, road-cutting regulations) -- none is a citizen-facing complaint-SLA document. Bihar remains 1 record (Patna, channel-only, no SLA).]** |
| `https://mcdonline.nic.in/portal/downloadFile/pwm_byelaws_2024_240216075150250.pdf` | Delhi | **OUT OF SCOPE (confirmed same as before)** | **[CHECKED — this is MCD's Plastic Waste Management bye-laws specifically (PWM = Plastic Waste Management), the same document already ruled out in the previous round as plastic-specific, not general solid-waste. No separate general MCD Solid Waste Management bye-law PDF was located via WebSearch or by fetching mcdonline.nic.in's homepage (which returned empty/JS-driven content).]** |
| `https://mcdonline.nic.in/portal/downloadFile/slb_final-converted_230110051610110.pdf` (MCD Swachh Bharat Mission — Service Level Benchmarking Handbook) | Delhi | **PROMOTED TO VERIFIED** | **[PROMOTED TO VERIFIED — see knowledge_records/verified/delhi/delhi.json (DL_MCD_SLB_TOILET_SANITATION_SLA), sources/inventory.json. WebFetch's own text extraction returned only garbled binary/font data (scanned-style PDF, same failure class as the Jaipur/Mumbai charters) -- worked around by pointing the Read tool at the locally-saved copy, which rendered the page content directly. Item 20 of the SLB monitoring guideline states: "Complaint registration and redressal mechanism is in place and functioning, all complaints, maintenance issues or incidents must be resolved within 24 hours" -- a real, numeric, primary-sourced SLA, but scoped specifically to community/public toilets (CTs/PTs), NOT general household garbage collection. The rest of the document (a %-based Service Level Benchmarking scorecard for water/sewerage/SWM) reports performance percentages, not time-bound complaint SLAs, so was not used for anything beyond the toilet-specific 24-hour figure. DL_MCD_WASTE_GRIEVANCE_CHANNEL (general garbage, SLA NOT FOUND) is left unchanged and NOT merged with this new record -- the two cover genuinely different services.]** |

### States/categories still genuinely open after Round 3

- Haryana: Waste category — only GMDA's general channel (no SLA).
- Karnataka: Roads & Streetlights for Bengaluru — fully open, blocked by systemic TLS issues.
- Gujarat: Ahmedabad's Water/Drainage and Roads — fully open, blocked by systemic TLS issues (Surat is done).
- Andhra Pradesh: all 4 categories still covered only via GVMC's generic IVRS/PGRS channel.
- Madhya Pradesh: still 1 record (state CM Helpline, channel-only).
- Bihar: still 1 record (Patna, channel-only, no SLA) — confirmed no stronger primary source exists via the RTPS Act angle.
- Delhi: general household garbage collection still SLA NOT FOUND (the new toilet-specific 24-hour SLA does not extend to it).

## Uttar Pradesh and Haryana coverage status update

Both states now have real VERIFIED coverage (UP: Lucknow + Varanasi, 3 records; Haryana: Gurugram/GMDA, 1 record) — the "0 verified" gap from the previous session's log is closed for both, though Haryana's coverage remains thin (1 general-channel record, no category-specific SLA) and UP's Waste/Roads/Streetlights (outside Varanasi's water SLA) remain channel-only too.

## Round 4 (2026-08-14, session 4): reaching blocked Karnataka/Gujarat content via alternate paths — zero survivors

Round 3 established that Karnataka's and Gujarat/Ahmedabad's dead ends all shared one root cause: a broken/unusual TLS
cert chain specific to the `karnataka.gov.in` and `ahmedabadcity.gov.in` domain families in this environment (other
`.gov.in` domains fetched fine in the same sessions). This round tested 5 specific ways to reach the same underlying
content through a different, working path, plus 2 alternate-city leads for AP and MP. Result: **0 of 5 leads
survived** — each failed for a distinct, confirmed reason, not from insufficient effort. This is a genuine, useful
negative result: it confirms these are real environment/infrastructure limitations, not a search-effort gap.

| Lead | Target | Result | Notes |
|---|---|---|---|
| Wayback Machine mirrors of blocked BBMP/AMC pages | Karnataka, Gujarat | **TOOL-BLOCKED (blanket)** | **[CHECKED — WebFetch refuses `web.archive.org` entirely: "Claude Code is unable to fetch from web.archive.org", confirmed with 3 different URL forms (a specific snapshot of `bbmp.gov.in`, a specific snapshot of AMC's Road Resurfacing page, and a raw CDX-style listing URL). This is a tool-level restriction, not a per-page or per-snapshot issue -- Wayback Machine is not a usable workaround path in this environment at all, for any domain, not just Karnataka/Gujarat.]** |
| `https://upload.indiacode.nic.in/showfile?...&filename=bbmp_rules_2021.pdf...` (BBMP Advertisement Rules 2021, via India Code's working cert chain) | Karnataka | **REAL BUT OFF-TOPIC** | **[CHECKED — fetched successfully (India Code's domain has no TLS issue, confirming the round-3 hypothesis that it's specific to karnataka.gov.in/bbmp.gov.in, not all Karnataka-related content). Read in full via the Read-tool-on-saved-PDF workaround: this is BBMP's Advertisement Rules 2021, entirely about outdoor hoarding/billboard licensing -- zero content about road repair or streetlight complaint SLAs. Confirms BBMP does publish real bye-laws through India Code (same channel as its existing VERIFIED waste bye-law), but this specific one isn't the right subject matter.]** |
| `https://www.indiacode.nic.in/bitstream/123456789/21664/1/36_of_2025_(e).pdf` (Greater Bengaluru Governance Act, 2024) | Karnataka | **BLOCKED (403)** | **[CHECKED — HTTP 403 Forbidden from indiacode.nic.in itself for this specific bitstream, unlike the showfile-pattern URL above which worked. Not retried a second time per the one-attempt rule; BBMP/GBA's Roads and Streetlights categories remain genuinely open for Bengaluru.]** |
| Gujarat (Right of Citizens to Public Services) Act, 2013 — SMC's own RCPS page, SUDA's page, and the actual 2016 gazette notification PDF (fetched via India Code's working cert chain and read in full via the Read-tool workaround) | Gujarat | **CONFIRMED NO SCHEDULE** | **[CHECKED — 3 fetches. SMC's and SUDA's own pages both link out to a PDF without displaying schedule content inline. The actual Gujarat Government Gazette notification (13-04-2016) under the Act was read in full: it only constitutes State Appellate Authorities per department (19 departments including "Urban Development and Urban Housing", each just assigned an Additional Chief Secretary/Principal Secretary/Secretary as appellate authority) -- no service-specific schedule of civic services with day limits anywhere in this document. Ahmedabad's Water/Drainage and Roads gaps remain open; this state-law angle is now confirmed exhausted, not just unexplored.]** |
| `ourvmc.org` (Vijayawada Municipal Corporation) — home page and a specific RTI Information Handbook PDF (`general/ria2018.pdf`), both via explicit `http://` | Andhra Pradesh | **UNREACHABLE (ECONNREFUSED)** | **[CHECKED — both attempts failed with `connect ECONNREFUSED` on port 443. WebFetch auto-upgrades any http:// URL to https://, and this domain appears to have no working TLS listener at all (a different failure class from Karnataka/Gujarat's broken cert chain, closer to `site.bbmp.gov.in`'s connection-refused failure from round 3). A WebSearch summary claims ourvmc.org hosts both a Citizen Charter and a genuine day-based SLA table, but this could not be independently confirmed by any direct fetch and is NOT promoted. AP's 4 categories remain covered only by GVMC's generic IVRS/PGRS channel.]** |
| `bmconline.gov.in` (Bhopal Municipal Corporation) | Madhya Pradesh | **EMPTY / NO PRIMARY SOURCE** | **[CHECKED — the domain resolves and loads but returns only a bare "App Title" placeholder (client-side-rendered shell), same failure class as `imcindore.mp.gov.in` and `mcdonline.nic.in`'s homepage. A WebSearch for Bhopal-specific grievance/charter content surfaced only a third-party aggregator (complainthub.org) -- explicitly disqualified as a source per this project's primary-source-only rule, not used. MP remains 1 record (state CM Helpline, channel-only).]** |

### Net result of Round 4

No new VERIFIED records this round -- all 5 primary leads (plus 2 sub-leads for BBMP specifically) were run down to a
confirmed, specific dead end rather than left ambiguous. Karnataka (Roads/Streetlights), Gujarat/Ahmedabad
(Water/Drainage + Roads), Andhra Pradesh (all 4 categories, generic-channel-only), Madhya Pradesh (1 record,
channel-only), and Bihar (1 record, channel-only, confirmed exhausted in Round 3) remain open. Given that Round 3
already confirmed Bihar's RTPS Act angle exhausted and this round confirmed Gujarat's RTS Act angle, Karnataka's
Wayback/India-Code angles, AP's ourvmc.org angle, and MP's Bhopal angle are ALL exhausted too, these 5 gaps should
now be treated as durable limitations of this research pipeline (primary-source-only + this environment's TLS/tooling
constraints) rather than leads still worth re-attempting without a genuinely new angle or a change in environment
capabilities (e.g. Wayback Machine access, or a working TLS path to karnataka.gov.in/ahmedabadcity.gov.in/ourvmc.org).
