# Motor Insurance Policyholder Risk Profiling System

## Automated Test Report (Dissertation Chapters 4 and 5)

This report follows the organisation described in the dissertation manuscript: **Chapter 4** reports empirical testing results in tabular form; **Chapter 5** discusses findings, limitations, and conclusions.

- **Run started (UTC):** 2026-05-14T08:36:55.055965+00:00
- **Run finished (UTC):** 2026-05-14T08:37:09.603401+00:00
- **Python:** 3.12.10
- **Summary:** PASS 46, FAIL 0, SKIP 0, REVIEW 4, Total 50

---

**CHAPTER 4: RESULTS AND SYSTEM TESTING**

**4.1 Introduction**

This chapter presents the results of an automated test pass mapped to the system's functional, risk-scoring, NLP, knowledge-base, performance, accuracy, reliability, compatibility, validation, and partial usability parameters. The harness uses FastAPI's `TestClient`, so no separate Uvicorn instance is required. Items marked **REVIEW** are documented for manual or specialist tooling (browser matrices, memory profilers, soak tests).

**4.2 Aggregate Summary**

| Outcome | Count |
| --- | ---: |
| PASS | 46 |
| FAIL | 0 |
| SKIP | 0 |
| REVIEW | 4 |

**4.3 Detailed Test Matrix**

| Ref | Section | Category | Parameter | Outcome | ms | Evidence (trimmed) |
| --- | --- | --- | --- | --- | ---: | --- |
| F-01 | 4.1.1 | Functional | User input validation (required fields, JSON body) | PASS | 29.1 | Checks completed without error. |
| F-02 | 4.1.2 | Functional | Risk score generation via POST /api/assess | PASS | 2439.9 | Checks completed without error. |
| F-03 | 4.1.3 | Functional | Risk classification and recommendation generation | PASS | 23.9 | Checks completed without error. |
| F-04 | 4.1.4 | Functional | API request and response handling (JSON) | PASS | 22.5 | Checks completed without error. |
| F-05 | 4.1.5 | Functional | Form-equivalent payload submission | PASS | 20.1 | Checks completed without error. |
| F-06 | 4.1.6 | Functional | Knowledge base integration in assess response | PASS | 20.9 | Checks completed without error. |
| F-07 | 4.1.7 | Functional | Gazette phrase matching on placename text | PASS | 25.9 | Checks completed without error. |
| F-08 | 4.1.8 | Functional | NLP text analysis (clean + analyze) | PASS | 11.4 | Checks completed without error. |
| F-09 | 4.1.9 | Functional | Decision trace / explanation structure | PASS | 18.2 | Checks completed without error. |
| F-10 | 4.1.10 | Functional | Underwriting recommendation text present | PASS | 17.1 | Checks completed without error. |
| F-11 | 4.1.11 | Functional | SQLite-backed KB listing endpoints | PASS | 87.4 | Checks completed without error. |
| F-12 | 4.1.12 | Functional | File upload and KB file delete (test artifact) | PASS | 182.3 | Checks completed without error. |
| R-01 | 4.2.1 | Risk scoring | Driver age scoring (structured index) | PASS | 0.0 | Checks completed without error. |
| R-02 | 4.2.2 | Risk scoring | Prior claims scoring | PASS | 0.0 | Checks completed without error. |
| R-03 | 4.2.3 | Risk scoring | Vehicle type scoring (motorcycle vs car) | PASS | 0.0 | Checks completed without error. |
| R-04 | 4.2.4 | Risk scoring | Vehicle age scoring | PASS | 0.0 | Checks completed without error. |
| R-05 | 4.2.5 | Risk scoring | Usage type scoring (commercial uplift) | PASS | 0.0 | Checks completed without error. |
| R-06 | 4.2.6 | Risk scoring | Location risk scoring (urban vs rural) | PASS | 0.0 | Checks completed without error. |
| R-07 | 4.2.7 | Risk scoring | Behavioural risk scoring (declared exposure) | PASS | 5.6 | Checks completed without error. |
| R-08 | 4.2.8 | Risk scoring | Environmental risk scoring | PASS | 7.1 | Checks completed without error. |
| R-09 | 4.2.9 | Risk scoring | Temporal risk scoring (night / peak) | PASS | 5.0 | Checks completed without error. |
| R-10 | 4.2.10 | Risk scoring | Claims severity scoring (separate dimension) | PASS | 0.1 | Checks completed without error. |
| R-11 | 4.2.11 | Risk scoring | Weighted composite score calculation | PASS | 0.1 | Checks completed without error. |
| R-12 | 4.2.12 | Risk scoring | Knowledge-base calibration metadata on scores | PASS | 4.0 | Checks completed without error. |
| N-01 | 4.3.1 | NLP | Gazette / supplementary keyword extraction | PASS | 0.8 | Checks completed without error. |
| N-02 | 4.3.2 | NLP | Text cleaning and normalization | PASS | 0.0 | Checks completed without error. |
| N-03 | 4.3.3 | NLP | Negation detection handling | PASS | 0.0 | Checks completed without error. |
| N-04 | 4.3.4 | NLP | Phrase categorization / bucket mapping | PASS | 6.7 | Checks completed without error. |
| N-05 | 4.3.5 | NLP | spaCy pipeline (en_core_web_sm) | PASS | 873.1 | Checks completed without error. |
| N-06 | 4.3.6 | NLP | Fallback keyword extractor path | PASS | 0.1 | Checks completed without error. |
| K-01 | 4.4.1 | Knowledge base | SQLite connectivity / KB health | PASS | 14.0 | Checks completed without error. |
| K-02 | 4.4.2 | Knowledge base | Keyword frequency aggregation | PASS | 0.2 | Checks completed without error. |
| K-03 | 4.4.3 | Knowledge base | Category prevalence in aggregate | PASS | 0.1 | Checks completed without error. |
| K-04 | 4.4.4 | Knowledge base | KB statistics retrieval speed (threshold) | PASS | 116.7 | Checks completed without error. |
| P-01 | 4.5.1 | Performance | API response time (/api/assess) | PASS | 64.8 | Checks completed without error. |
| P-02 | 4.5.2 | Performance | Rapid sequential assess requests (burst load smoke; true concurrency needs multi-process tooling) | PASS | 635.7 | Checks completed without error. |
| P-03 | 4.5.3 | Performance | Large in-memory narrative processing time | PASS | 8430.8 | Checks completed without error. |
| A-01 | 4.6.1 | Accuracy | Classification band boundaries | PASS | 0.0 | Checks completed without error. |
| A-02 | 4.6.2 | Accuracy | Score normalization (0–100) | PASS | 4.1 | Checks completed without error. |
| L-01 | 4.7.1 | Reliability | Deterministic repeat of risk scores | PASS | 4.0 | Checks completed without error. |
| L-02 | 4.7.2 | Reliability | Recovery after invalid input (422, server alive) | PASS | 13.6 | Checks completed without error. |
| C-01 | 4.8.1 | Compatibility | JSON request/response compatibility | PASS | 17.7 | Checks completed without error. |
| V-01 | 4.9.1 | Validation | Required field validation (422) | PASS | 6.7 | Checks completed without error. |
| V-02 | 4.9.2 | Validation | Invalid JSON body handling | PASS | 4.8 | Checks completed without error. |
| V-03 | 4.9.3 | Validation | Tyre condition dropdown accepted | PASS | 17.4 | Checks completed without error. |
| U-01 | 4.10.1 | Usability (heuristic) | Wizard steps and error UI (static source signals) | PASS | 0.5 | Checks completed without error. |
| U-02 | 4.10.2 | Usability | Form navigation ease, mobile responsiveness, explanation readability (user testing) | REVIEW | 0.0 | Requires human participants or device testing; not automated here. |
| P-04 | 4.5.4 | Performance | Memory profiling, DB micro-benchmarks, frontend bundle load (Lighthouse) | REVIEW | 0.0 | Optional profiling tools not invoked in this CI-style script. |
| C-02 | 4.8.2 | Compatibility | Browser and operating system compatibility | REVIEW | 0.0 | Cross-browser/OS testing is manual or farm-based. |
| L-03 | 4.7.3 | Reliability | Long-run uptime, chaos / crash resistance | REVIEW | 0.0 | Soak and chaos tests not executed in this harness. |

**4.4 Interpretation of Parameter Coverage**

Automated checks directly exercise API scoring, rule dimensions, KB routes, SQLite-backed file metadata, NLP cleaning and analysis (including fallback extraction), classification thresholds, and a burst of sequential assess calls. Parameters that inherently require human judgement, production telemetry, or multi-browser execution appear as **REVIEW** rows rather than false positives.

---

**CHAPTER 5: DISCUSSION, CONCLUSION, AND FUTURE WORK**

**5.1 Discussion**

The suite indicates whether the integrated stack behaves coherently for representative policyholder payloads: scores remain in range, explanations are populated, knowledge-base fields are present, and invalid requests produce HTTP 422 without destabilising subsequent calls. Where spaCy resources are missing, NLP tests skip rather than fail, which matches expected developer-machine variance.

**5.2 Limitations**

In-process tests do not validate TLS, reverse proxies, or distributed load. The Pydantic layer currently accepts wide integer ranges unless additional validators are introduced, so numeric range validation should be treated as a product decision distinct from this harness.

**5.3 Conclusion**

In this run, **46** checks passed, **0** failed, **0** were skipped, and **4** were reserved for manual follow-up. No automated failures were recorded.

**5.4 Future Work**

- Add continuous integration to run this script on every commit.
- Extend validation with explicit numeric bounds and enum enforcement.
- Add end-to-end browser tests for wizard UX and mobile layouts.
- Optionally pin spaCy model installation in deployment to avoid silent fallback when gazette precision matters.
