# How This Motor Insurance Risk System Works

This document explains the **whole application** in plain language. You can read it even if you are new to programming. Where technical words appear, they are explained.

---

## 1. What is this system?

**Purpose:** Help estimate **how risky** a motor insurance policyholder might be for **future claims**, using:

- A **structured questionnaire** (the React frontend form).
- **Rules** in Python that turn answers into numbers.
- An optional **knowledge base** of past accident texts you store on disk, used to **adjust** scores when the applicant mentions places or phrases that show up often in those accidents.

**What it is not:** It does not pull criminal records or external databases. It only scores **what the user enters** and **statistics from your own uploaded `.txt` files** (if you have analysed them).

---

## 2. The big picture (read this first)

Think of three layers:

```text
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (React)                                           │
│  User fills a step-by-step form → sends JSON to the API     │
└───────────────────────────────┬─────────────────────────────┘
                                │ HTTP POST /api/assess
                                ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI / Python)                                  │
│  1) Turn form answers into numbers (“underwriting index”)    │
│  2) Turn checkboxes into “risk flags” → six risk dimensions │
│  3) Blend those two → one composite score (before KB)       │
│  4) Optionally adjust using knowledge-base statistics      │
│  5) Map score to a label: Low, Medium, High, …              │
└───────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│  KNOWLEDGE BASE (optional)                                   │
│  Folder backend/knowledge/*.txt + SQLite (kb.sqlite)         │
│  “How often does Mutare appear in our accident files?”       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Words you need (mini glossary)

| Term | Simple meaning |
|------|----------------|
| **API** | A program on the server that accepts requests and returns JSON. Here: `POST /api/assess` receives the form and returns scores. |
| **JSON** | Text format for structured data (like a Python dict or JavaScript object) sent between frontend and backend. |
| **Frontend / backend** | Frontend = browser UI (React). Backend = Python server (FastAPI). |
| **Dimension** | One “bucket” of risk: Behavioural, Environmental, Time, Vehicle, Location, Claims/Severity. Each gets a score 0–100. |
| **Legacy features / flags** | A dictionary of named signals (e.g. `drunk_driving`, `rain`) with values 0–1. The rules engine uses them to compute dimension scores. |
| **Gazette** | A list of phrases (CSV) that the NLP layer looks for in **short text** (city/placename fields). |
| **Knowledge base (KB)** | Your collection of accident `.txt` files plus saved statistics about how often words and categories appear. |
| **Calibration / lift** | Multiplying a dimension score slightly up or down based on how common that risk pattern is in your corpus. |

---

## 4. Frontend: what the user sees

**Tech:** React app (often run with `npm start` on port 3000).

**Behaviour:**

1. **Step-by-step wizard** (several screens) so the form is not one giant page.
2. Steps cover **driver profile**, **vehicle**, **usage and locations**, **behaviour & environment checkboxes**, **roads & time**, **past accident severity**.
3. On the **last step**, the user clicks **Run risk assessment**.
4. The app sends one **`POST`** request to the backend, for example:

   `http://127.0.0.1:8000/api/assess`

5. The body is **JSON** containing all fields: numbers (age, prior claims), dropdowns (vehicle type), booleans (checkboxes), and optional text for city/placenames.

**Important:** There is **no long free-text accident story** required for scoring. Optional placename text is only used to match phrases against your gazette and knowledge base.

---

## 5. Backend API: the main endpoint

**File:** `backend/app/api_main.py`

**Endpoint:** `POST /api/assess`

**Input:** A `PolicyholderAssessRequest` (defined in `backend/app/schemas.py`) — all the form fields.

**Rough order of operations:**

1. **Build a short string** from `primary_city_or_region` and `additional_place_keywords` only.
2. If that string is non-empty, run **`analyze_text`** on it (NLP). If empty, use empty NLP results.
3. Load **knowledge-base statistics** from SQLite (if you have run a corpus analysis).
4. Call **`calculate_policyholder_risk_score`** with the full form object + gazette matches from step 1.
5. Call **`classify_policyholder_risk`** to turn the final 0–100 number into **Low / Medium / High / Very High / Critical**.
6. Build **risk indicators** from the form-derived legacy flags + prior-claims hints.
7. Build a **human-readable explanation** (`build_policyholder_explanation`) for the UI “decision trace”.
8. Return **`PolicyholderAssessResponse`**: scores, class, indicators, KB metrics, explanation sections.

---

## 6. How the score is calculated (the core idea)

The final number **`predicted_claim_risk_score`** is between **0 and 100**. It comes from **six dimensions**, each adjusted by the knowledge base, then combined with fixed **weights**.

### Step A — Underwriting index (from “core” form fields only)

**Function:** `score_structured_data()` in `backend/app/scoring/risk_engine.py`

This adds points for things like:

- Young or older driver age bands  
- Number of **prior claims**  
- Motorcycle / truck  
- Urban area / commercial usage  
- Older **vehicle age** (extra tiers)  
- Engine capacity bands  
- Vehicle value bands  
- Annual distance (km) bands  

The result is capped at **100** and is called **`structured_score`** here. Think of it as: **“traditional underwriting factors from the form.”**

### Step B — “Factor” scores from checkboxes (rule engine)

**Function:** `legacy_features_from_policy_form()`  

It reads all the **declared exposure** checkboxes and dropdowns (speeding, rain, night driving, past injury, etc.) and fills a dictionary of **legacy flags** (0.0 or 1.0, sometimes 0.55 for “fair” tyres).

**Function:** `calculate_risk_score(legacy)`  

This implements the **point tables** (speeding +25, DUI +40, rain +10, etc.) for each **dimension** (Behavioural, Environmental, Time, Vehicle, Location, Claims/Severity), including some **combinations** (e.g. drunk + speeding bonus).  

Output: six numbers **0–100** — one per dimension — plus an internal weighted sum.

So: **checkboxes → flags → dimension scores** (“factor_scores”).

### Step C — Blend underwriting index with factor dimensions

For **each** of the six dimensions separately:

```text
baseline[dimension] = 0.38 × structured_score + 0.62 × factor_score[dimension]
```

So the **same** underwriting index is mixed with **dimension-specific** rule scores. That way a person with high environmental exposure but low behavioural exposure does not get a single flat number for everything.

Then the code builds one **composite** `final_score` using the **same weights** as the risk formula:

| Dimension | Weight |
|-----------|--------|
| Behavioural | 0.35 |
| Environmental | 0.10 |
| Time | 0.10 |
| Vehicle | 0.15 |
| Location | 0.10 |
| Claims / severity | 0.20 |

So:

```text
composite = sum over dimensions of (weight × baseline[dimension])
```

That composite is **before** knowledge-base adjustment.

### Step D — Knowledge-base calibration (optional)

**Function:** `_adjust_nlp_with_kb()`

If you have **no** analysed corpus, this step does nothing useful (multipliers stay 1.0).

If you **do** have stats:

1. **Category lift:** For each dimension, how often does that dimension appear across your KB files? Slightly scale the score up or down.
2. **Term prevalence lift:** From the **gazette matches** on the applicant’s city/placename text: if a matched phrase (e.g. normalized “mutare”) appears in a **large share** of your accident files, that dimension gets an extra boost.

The output is **`predicted_claim_risk_score`** — the **final** 0–100 number after these multipliers.

### Step E — Risk class labels

**File:** `backend/app/scoring/classifier.py`

| Final score | Class |
|-------------|--------|
| 0–20 | Low |
| 21–40 | Medium |
| 41–60 | High |
| 61–80 | Very High |
| 81+ | Critical |

Plus a short **recommendation** string for underwriters.

---

## 7. NLP: what it does *now*

**Important change:** NLP is **not** used to score a long accident narrative for the policyholder.

**It is used for:**

- Taking **`primary_city_or_region`** and **`additional_place_keywords`** (combined and cleaned).
- Running **`analyze_text()`** (`backend/app/nlp/analysis.py`).

**Two paths inside `analyze_text`:**

1. **Preferred:** **spaCy** + **EntityRuler** loaded from your **gazette CSV** (`backend/gazette/large_spacy_gazetteer_insurance_nlp.csv`). It finds spans like place names and labels them.
2. **Fallback:** If spaCy/model is missing, a simpler **keyword** extractor runs on the same short text.

**Output used by scoring:** mainly **`gazette_matches`** (phrase + label + category) for KB term-prevalence lifts. Secondary: `matched_keywords`, `buckets`, `legacy_features` for that tiny text — **not** the main policyholder blend (the main blend is form-driven).

**Negation:** If you paste phrases like “no drunk driving”, helper logic in `backend/app/nlp/negation.py` tries not to treat negated phrases as positive risk. Most useful when the matched text is longer; placename fields are usually short.

---

## 8. Gazette: CSV vs Python “rules”

| Piece | Role |
|-------|------|
| **CSV (`large_spacy_gazetteer_insurance_nlp.csv`)** | List of **phrases** + **label** + **category** so spaCy can **find** them in text. |
| **Python (`gazette_mapping.py`)** | Defines **what happens when a phrase matches**: which legacy flags and bucket weights to set for **scoring**. |

So: **CSV = what to detect**, **Python = how it affects numbers** (unless the label is something like jargon that intentionally does not move the score).

Form **checkboxes** bypass the gazette for those factors: they go straight into **`legacy_features_from_policy_form`**.

---

## 9. Knowledge base: folders and database

**Paths** (`backend/app/kb/paths.py`):

- **`backend/knowledge/`** — primary folder for `.txt` accident reports (and optionally a second scan path under the repo root — see code).
- **`backend/data/kb.sqlite`** — SQLite database listing files and storing aggregate NLP stats.

**Typical workflow:**

1. Put `.txt` files in `knowledge/`.
2. Call the KB API (e.g. **analyse all**) from the admin UI or WebSocket — see `backend/app/kb/router.py` and `kb/service.py`.
3. The service runs **`analyze_text`** on each file, aggregates keyword counts and bucket averages, saves stats.
4. Next time someone submits **Mutare** in the placename field, if **Mutare** is common in your corpus, **location** (and related) lifts can increase.

---

## 10. Explanation API payload (decision trace)

**File:** `backend/app/scoring/explanation.py`

Builds **sections** for the UI: what drove the score, structured index, place-keyword matches, KB influence, example like **Mutare**, final outcome.  

The frontend shows this under **Decision trace** when the API returns `risk_decision_explanation`.

---

## 11. Project layout (where to look)

```text
backend/
  app/
    api_main.py          # FastAPI app, /api/assess
    schemas.py           # Request/response shapes
    scoring/
      risk_engine.py     # Main formulas, blend, KB adjustment
      classifier.py      # Low / Medium / High …
      explanation.py     # Text trace for UI
      kb_dimensions.py   # Map gazette labels to B/E/T/V/L/C for KB lifts
    nlp/
      analysis.py        # analyze_text entry
      text_cleaner.py
      gazette_loader.py  # Reads CSV
      gazette_mapping.py # Phrase → flags / buckets
      spacy_pipeline.py  # spaCy path
      negation.py        # Negation / denial helpers
      feature_extractor.py # Fallback keywords
    kb/
      paths.py           # KNOWLEDGE_DIR, DB path
      router.py          # /api/kb/* routes
      service.py         # Analyse folder, aggregates
    db/
      store.py           # SQLite: files + NLP runs + stats
  gazette/
    large_spacy_gazetteer_insurance_nlp.csv
  knowledge/             # Your accident .txt corpus (you create)
frontend/
  src/
    App.js               # Wizard form, calls /api/assess
```

---

## 12. How to run (typical dev setup)

1. **Backend:** From `backend/`, activate venv, install deps, run:

   `uvicorn app.api_main:app --reload --host 0.0.0.0 --port 8000`

2. **Frontend:** From `frontend/`, `npm install`, then `npm start` (often port 3000).

3. **spaCy (optional but recommended):** Install `spacy` and `en_core_web_sm` so gazette matching uses EntityRuler; otherwise fallback keywords are used.

---

## 13. Mental model summary

1. **Form numbers + dropdowns** → **underwriting index** (`structured_score`).  
2. **Form checkboxes** → **flags** → **rule-based dimension scores** (`calculate_risk_score`).  
3. **Per dimension:** blend **38% underwriting + 62% rules** → six baselines.  
4. **Weighted sum** → one **composite** (0–100).  
5. **Optional KB** → multiply dimensions using **your** accident corpus stats + **placename gazette matches**.  
6. **Classifier** → **Low … Critical** + recommendation text.  
7. **UI** shows breakdown, indicators, and explanation.

---

## 14. Limitations (honest)

- Scores reflect **declared** behaviour and **your** data quality — not ground truth from courts or telematics.
- Short placename text rarely triggers negation logic meaningfully.
- Gazette and rules must be **maintained** as products and wording evolve.

---

*This document describes the codebase architecture and behaviour as implemented; numeric constants (weights, lifts) live in Python and may change as you tune the product.*
