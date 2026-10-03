# NYC 311 FDE Lab

> A self-directed Forward Deployed AI Engineer (FDE) practice project using public NYC 311 operational data to identify workflow friction, validate root causes, and design an AI intervention only where the evidence supports it.

## Project Status

**Current phase:** Discovery / Operational Analysis  
**AI implementation status:** Not started intentionally  
**Primary objective:** Find a real, measurable operational friction point before deciding what to build

---

## 1. Project Goal

The purpose of this project is to practice the work of a Forward Deployed AI Engineer by treating NYC 311 as a real customer environment.

The goal is **not** to immediately build a chatbot, RAG application, or classifier.

The goal is to:

1. Understand the operational process.
2. Map stakeholders and handoffs.
3. Identify measurable friction.
4. Form and test hypotheses.
5. Distinguish symptoms from root causes.
6. Determine whether AI is actually justified.
7. Prototype the smallest useful intervention.
8. Evaluate whether it improves the workflow.
9. Iterate based on observed failure modes and user feedback.

---

## 2. Fictional FDE Engagement Brief

### Customer

**NYC311 Operations — simulated engagement**

### Problem Statement

NYC311 handles millions of public service requests across many city agencies.

The customer has asked:

> Where are service requests creating unnecessary operational work or poor resident outcomes, and could AI improve those workflows?

### Constraints

- Use only public information and public datasets.
- Do not assume AI is the correct solution.
- Do not automate high-impact operational decisions without human review.
- Recommendations must be measurable.
- Findings must distinguish evidence from hypotheses.
- Survey data must not be treated as representative of all NYC311 users without validation.

### Initial Success Criteria

A successful first phase should produce:

- A documented current-state workflow.
- A stakeholder map.
- A ranked list of operational friction hypotheses.
- Quantitative evidence for at least one friction point.
- Known limitations and unanswered questions.
- A proposed intervention tied to a measurable outcome.

---

## 3. Current-State Workflow

Initial workflow model:

```text
Resident
   ↓
NYC311 Intake
   ↓
Service Request Created
   ↓
Request Classified
   ↓
Responsible Agency Identified
   ↓
Request Routed
   ↓
Agency Investigates / Performs Work
   ↓
Agency Updates Request
   ↓
Request Closed
   ↓
Resolution Communicated
   ↓
Optional Resident Satisfaction Survey
```

### Important Question

A service request being marked **Closed** does not automatically prove that the underlying resident problem was fully resolved.

That distinction is one of the first areas this project will investigate.

---

## 4. Stakeholder Map

| Stakeholder | Primary Concern | Questions to Investigate |
|---|---|---|
| Resident | Getting the issue resolved | Why was my request closed? Do I need to submit another request? |
| NYC311 Call Taker | Accurate intake and routing | What information is frequently missing? |
| NYC311 Operations | Efficient request handling | Where are repeated contacts or unnecessary handoffs occurring? |
| Agency Dispatcher | Actionable work queue | Are requests correctly classified and complete? |
| Field Worker / Inspector | Enough context to act | What causes wasted visits or additional investigation? |
| Agency Supervisor | Throughput and service quality | Which requests miss service targets or reopen? |
| Data / Engineering | Reliable systems and integrations | What can be improved without replacing existing systems? |
| Security / Governance | Safe use of citizen and operational data | What should AI never receive or decide automatically? |
| Leadership | Better outcomes at sustainable cost | What operational metric should improve? |

---

## 5. Public Data Sources

### NYC 311 Service Requests from 2020 to Present

Primary operational dataset.

**Dataset:**  
https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9

Potentially useful fields include:

- `unique_key`
- `created_date`
- `closed_date`
- `agency`
- `agency_name`
- `complaint_type`
- `descriptor`
- `descriptor_2`
- `location_type`
- `incident_zip`
- `incident_address`
- `street_name`
- `cross_street_1`
- `cross_street_2`
- `borough`
- `status`
- `due_date`
- `resolution_description`
- `resolution_action_updated_date`
- `open_data_channel_type`
- `latitude`
- `longitude`

### NYC 311 Resolution Satisfaction Survey

Used to study resident-reported outcomes.

**Dataset:**  
https://data.cityofnewyork.us/d/5ijn-vbdv

Potential uses:

- Compare operational closure with resident satisfaction.
- Identify common dissatisfaction reasons.
- Explore whether specific complaint / agency combinations have poor outcomes.
- Analyze resolution language associated with poor satisfaction.

### Important Survey Limitation

Survey respondents are not necessarily representative of every resident who submits a 311 request.

Survey findings should therefore be described as:

> "Among survey respondents..."

and not:

> "Among all NYC311 users..."

unless additional evidence supports that conclusion.

---

## 6. Initial FDE Hypothesis

### Hypothesis H1

**"Closed" does not always mean "resolved from the resident's perspective."**

Possible operational loop:

```text
Problem Occurs
    ↓
Resident Submits 311 Request
    ↓
Agency Handles Request
    ↓
Request Closed
    ↓
Problem Still Exists
    ↓
Resident Submits Another Request
    ↓
Additional Operational Work
```

### Possible Consequences

These are hypotheses, not established findings:

- Repeat contacts
- Duplicate requests
- Repeat dispatches
- Reopened or recreated work
- Longer queues
- Resident frustration
- Misleading closure metrics
- Difficulty distinguishing recurring issues from failed resolutions

---

## 7. Alternative Explanations

Repeated requests at the same location may mean very different things.

```text
Repeated Request
       ↓
 ┌─────┼──────────────────────────────────────┐
 │     │          │          │               │
 ▼     ▼          ▼          ▼               ▼
Duplicate   Unresolved   Recurring     Multiple       Incorrect
Report      Problem      Condition     Residents      Classification
```

Before proposing automation, determine which explanation is most likely.

---

## 8. Discovery Questions

### Resident Experience

- Why do residents submit another request after closure?
- Are closure explanations understandable?
- Do residents know what next action to take?
- Are some complaint types especially confusing?

### Intake

- Which complaint types are frequently missing required information?
- Does intake quality differ by phone, mobile, web, or other channel?
- Which categories have ambiguous descriptions?
- Which fields appear optional but are operationally important?

### Routing

- Which complaint types map to multiple agencies?
- Where might classification errors create unnecessary handoffs?
- Are certain requests difficult to route because of incomplete information?

### Agency Operations

- Which complaint types have unusually long resolution times?
- Which categories frequently produce repeat requests?
- Do certain resolutions correlate with dissatisfaction?
- Are some issues inherently recurring rather than "one-and-done"?

### Field Operations

- What information would make a service request more actionable?
- Are technicians / inspectors receiving enough location detail?
- Can multiple nearby requests represent one larger incident?
- Are duplicate dispatches possible?

### Leadership

- Is closure time the correct metric?
- Should the target metric instead be:
  - First-contact resolution?
  - First-visit resolution?
  - Repeat-request rate?
  - Resident satisfaction?
  - Avoided dispatches?
  - Time to validated resolution?

---

## 9. Initial Analysis Window

Start with a manageable time range rather than all available historical data.

### Proposed Window

**July 1, 2026 through September 30, 2026**

Reason:

- Recent enough to reflect current operations.
- Large enough to reveal recurring patterns.
- Small enough for initial exploration and local analysis.

---

## 10. Analysis Plan

### A. Resolution Time

Calculate:

```text
resolution_time = closed_date - created_date
```

Group by:

- Agency
- Complaint type
- Descriptor
- Borough
- Intake channel

Questions:

- Which combinations have the longest median resolution time?
- Which have extreme tail latency?
- Are long resolution times expected for certain categories?

---

### B. Repeat-Location Requests

Identify similar requests occurring:

- At the same address
- Within a geographic radius
- Under the same complaint type
- Within:
  - 24 hours
  - 72 hours
  - 7 days

Candidate signal:

```text
Request A
   ↓
Closed
   ↓
Same / Similar Complaint
Same / Nearby Location
Short Time Window
   ↓
Request B
```

Important:

A repeated request is only a **signal**. It is not automatically a duplicate or failed resolution.

---

### C. Resolution Language

Analyze `resolution_description`.

Questions:

- What resolution descriptions are most common?
- Which language appears frequently among dissatisfied respondents?
- Which closure reasons imply:
  - No action taken
  - Unable to locate issue
  - Referred elsewhere
  - Already addressed
  - Insufficient information
  - Outside jurisdiction

---

### D. Satisfaction Analysis

Compare:

```text
Agency
+ Complaint Type
+ Descriptor
+ Resolution Description
→ Satisfaction / Dissatisfaction
```

Questions:

- Which operational categories have poor outcomes among survey respondents?
- What dissatisfaction reasons dominate?
- Does long resolution time correlate with dissatisfaction?
- Do some resolution messages appear especially confusing?

---

### E. Information Completeness

Measure missingness for operationally useful fields.

Examples:

- Incident address
- Location type
- Descriptor
- Cross streets
- Latitude / longitude
- ZIP code

Questions:

- Are missing fields concentrated in certain channels?
- Does missing information correlate with longer resolution times?
- Does missing information correlate with repeat requests?

---

## 11. Hypothesis Tracker

| ID | Hypothesis | Evidence Needed | Status | Result |
|---|---|---|---|---|
| H1 | Closed requests sometimes generate new requests because the underlying issue remains | Same-location repeat requests after closure + resolution language + satisfaction | Open | TBD |
| H2 | Some complaint types arrive with insufficient information for efficient action | Field missingness + longer resolution / repeated contacts | Open | TBD |
| H3 | Duplicate requests create avoidable operational work | Spatial / temporal clustering + identical complaint features | Open | TBD |
| H4 | Certain closure descriptions are associated with poor resident satisfaction | Resolution text + survey responses | Open | TBD |
| H5 | Some incidents should be treated as area-level events rather than independent requests | Dense clusters of same complaint in short time window | Open | TBD |
| H6 | Intake channel affects information quality | Missingness / classification by channel | Open | TBD |
| H7 | Long closure time is not the only or best predictor of poor resident outcomes | Resolution time + satisfaction + repeat request rate | Open | TBD |

### Status Values

- `Open`
- `Testing`
- `Supported`
- `Rejected`
- `Inconclusive`

---

## 12. Findings Log

Use this section as discoveries are made.

### Finding F001

**Observation:**  
TBD

**Evidence:**  
TBD

**Operational implication:**  
TBD

**Possible root cause:**  
TBD

**Alternative explanation:**  
TBD

**What we still do not know:**  
TBD

**Potential intervention:**  
TBD

**Does this require AI?**  
TBD

---

## 13. FDE Decision Framework

Every proposed intervention should pass through:

```text
Observation
    ↓
Evidence
    ↓
Operational Friction
    ↓
Affected Stakeholders
    ↓
Root-Cause Hypotheses
    ↓
Missing Information
    ↓
Potential Intervention
    ↓
Can Simple Software / Process Fix It?
    ↓
If Not, Does AI Add Meaningful Value?
    ↓
Prototype
    ↓
Evaluate
```

### Rule

Do not use an LLM where:

- A form validation rule solves the problem.
- A deterministic lookup solves the problem.
- A database query solves the problem.
- Better workflow design solves the problem.
- A static decision tree is sufficient.

Use AI where ambiguity, language understanding, contextual reasoning, or unstructured information creates meaningful value.

---

## 14. Possible AI Interventions

These are **not yet approved project features**.

They are candidate interventions to consider only after discovery.

### Candidate A — Intake Completeness Assistant

Purpose:

Identify missing information before a request enters the operational queue.

Example:

```text
Resident:
"The street light by Walgreens keeps going out."

System:
"I can help route this correctly. Is the issue affecting one light
or several lights on the block?"
```

---

### Candidate B — Service Request Triage Copilot

Potential output:

```json
{
  "complaint_domain": "street_lighting",
  "issue_type": "intermittent_failure",
  "missing_information": [
    "exact_fixture_or_pole_location"
  ],
  "suggested_routing": "street_lighting_operations",
  "clarifying_question": "Is one streetlight affected or several?"
}
```

Human operator remains responsible for the final action.

---

### Candidate C — Duplicate / Related Incident Detection

Detect potential relationships between:

- Similar complaints
- Nearby locations
- Short time windows
- Shared infrastructure

Possible use:

```text
17 related reports detected within 100 meters.

Potential area-level incident.

Recommend supervisor review before independent dispatch.
```

---

### Candidate D — Resolution Quality Assistant

Before closing a request, flag resolution language that may be:

- Ambiguous
- Missing next steps
- Not resident-friendly
- Inconsistent with observed work

---

### Candidate E — Operations Copilot

Combine:

- Current request
- Related historical requests
- Location context
- Agency procedures
- Previous outcomes

Then recommend the next best operational action.

This would be a later-stage project, not V1.

---

## 15. Proposed System Architecture

Only relevant if discovery justifies AI.

```text
                      NYC311 Request Data
                              │
                              ▼
                    ┌───────────────────┐
                    │ Ingestion Layer   │
                    └─────────┬─────────┘
                              │
                   ┌──────────┴──────────┐
                   │                     │
                   ▼                     ▼
             Structured Data       Unstructured Text
                   │                     │
                   └──────────┬──────────┘
                              ▼
                    Operational Context
                              │
                              ▼
                    Rules / Policy Layer
                              │
                              ▼
                         AI Component
                              │
                              ▼
                      Proposed Action
                              │
                              ▼
                        Human Review
                              │
                              ▼
                       Outcome Capture
                              │
                              ▼
                         Evaluation
```

---

## 16. Evaluation Plan

Do not judge success by whether the AI produces plausible text.

Measure operational performance.

Potential metrics:

| Metric | Meaning |
|---|---|
| Classification accuracy | Correct complaint / issue category |
| Routing accuracy | Correct operational team |
| Missing-information recall | Finds information required before action |
| Duplicate precision | Flagged requests actually refer to the same issue |
| Duplicate recall | Related requests are successfully identified |
| Human acceptance rate | Operator agrees with recommendation |
| Human override rate | Operator selects a different action |
| Unsafe recommendation rate | AI recommends an action outside policy |
| Unsupported recommendation rate | Recommendation lacks evidence |
| Resolution time | Time from creation to closure |
| Repeat-request rate | Similar request appears after closure |
| First-action usefulness | First recommended action moves case forward |
| Resident satisfaction | Survey response where available |
| Cost per request | Model + infrastructure cost |
| Latency | Time to produce recommendation |

---

## 17. Human-in-the-Loop Requirements

Initial AI recommendations should be advisory.

The system should not autonomously:

- Close resident requests.
- Issue violations.
- Dispatch personnel.
- Change agency ownership.
- Determine legal or regulatory outcomes.
- Override agency procedures.
- Infer sensitive facts about residents.

Recommended interaction:

```text
AI Recommendation
       ↓
Operator Review
       ↓
Accept / Modify / Reject
       ↓
Actual Action
       ↓
Outcome
       ↓
Evaluation Dataset
```

---

## 18. Feedback Schema

Future prototype feedback options:

```text
[ Helpful ]
[ Incorrect ]
[ Missing Context ]
[ Wrong Routing ]
[ Potential Duplicate ]
[ Unsafe / Not Allowed ]
[ Different Action Taken ]
```

Store:

```text
Request Context
AI Recommendation
Human Decision
Actual Action
Outcome
Feedback
Model Version
Prompt Version
Policy Version
```

---

## 19. Technical Stack

### Phase 1 — Analysis

- Python
- Pandas or Polars
- Jupyter
- NYC Open Data / Socrata API
- DuckDB or PostgreSQL
- GeoPandas if spatial analysis becomes useful

### Phase 2 — Prototype

- FastAPI
- PostgreSQL
- pgvector if semantic retrieval is justified
- React / Next.js
- Gemini API
- Docker

### Phase 3 — Production-Like Practice

Possible additions:

- OpenTelemetry
- Langfuse or another LLM observability tool
- GitHub Actions
- Cloud Run
- Terraform
- Authentication / RBAC
- Feature flags
- Evaluation pipelines

### Deliberately Not Starting With

- Kubernetes
- Multi-agent orchestration
- Fine-tuning
- Autonomous agents
- Complex vector infrastructure

The project should earn complexity.

---

## 20. Repository Structure

```text
nyc311-fde-lab/
│
├── README.md
│
├── docs/
│   ├── 01-engagement-brief.md
│   ├── 02-current-workflow.md
│   ├── 03-stakeholder-map.md
│   ├── 04-friction-hypotheses.md
│   ├── 05-discovery-findings.md
│   ├── 06-solution-design.md
│   └── 07-evaluation-results.md
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
│
├── notebooks/
│   ├── 01-data-profile.ipynb
│   ├── 02-resolution-time.ipynb
│   ├── 03-repeat-requests.ipynb
│   ├── 04-resolution-language.ipynb
│   └── 05-satisfaction-analysis.ipynb
│
├── src/
│   ├── ingestion/
│   ├── analysis/
│   ├── api/
│   ├── ai/
│   └── policies/
│
├── evals/
│   ├── datasets/
│   ├── scorers/
│   └── reports/
│
├── tests/
│
├── scripts/
│
└── .github/
    └── workflows/
```

---

## 21. Project Milestones

### Milestone 0 — Repository Setup

- [ ] Create GitHub repository
- [ ] Add README
- [ ] Add `.gitignore`
- [ ] Add Python environment
- [ ] Create directory structure
- [ ] Document public data sources
- [ ] Add license if appropriate

---

### Milestone 1 — Data Ingestion

- [ ] Connect to NYC Open Data / Socrata API
- [ ] Pull July 1–September 30, 2026 service requests
- [ ] Save raw extract
- [ ] Validate schema
- [ ] Parse timestamps
- [ ] Profile missing values
- [ ] Document row count
- [ ] Document data limitations
- [ ] Create repeatable ingestion script

**Deliverable:** Reproducible dataset ingestion.

---

### Milestone 2 — Current-State Analysis

- [ ] Calculate resolution times
- [ ] Break down by agency
- [ ] Break down by complaint type
- [ ] Break down by borough
- [ ] Break down by intake channel
- [ ] Analyze missing operational fields
- [ ] Identify high-volume categories
- [ ] Identify extreme resolution-time categories

**Deliverable:** Current-state operations profile.

---

### Milestone 3 — Repeat Request Analysis

- [ ] Define "same location"
- [ ] Define "nearby location"
- [ ] Define "similar complaint"
- [ ] Test 24-hour window
- [ ] Test 72-hour window
- [ ] Test 7-day window
- [ ] Separate likely duplicates from recurring issues
- [ ] Review example clusters manually
- [ ] Document false positives

**Deliverable:** Repeat-request friction report.

---

### Milestone 4 — Satisfaction Analysis

- [ ] Load satisfaction survey
- [ ] Understand join / comparison limitations
- [ ] Analyze satisfaction by agency
- [ ] Analyze satisfaction by complaint type
- [ ] Analyze dissatisfaction reasons
- [ ] Analyze resolution descriptions
- [ ] Compare operational signals with survey outcomes
- [ ] Document selection bias

**Deliverable:** Resident-outcome analysis.

---

### Milestone 5 — Friction Selection

Select **one** friction point.

Selection criteria:

- [ ] Supported by data
- [ ] Operationally meaningful
- [ ] Affected stakeholder is identifiable
- [ ] Root cause is partially understood
- [ ] Outcome can be measured
- [ ] AI may provide real value
- [ ] Human review can be retained
- [ ] Public data is sufficient for a prototype

**Deliverable:** FDE Friction Discovery Memo.

---

### Milestone 6 — Baseline

Before building AI:

- [ ] Create deterministic baseline
- [ ] Measure baseline performance
- [ ] Document baseline errors
- [ ] Define acceptance criteria for AI

Potential baselines:

- Keyword routing
- Rule-based missing-field detection
- Geographic clustering
- Exact / fuzzy duplicate matching
- Static decision tree

**Deliverable:** Baseline evaluation report.

---

### Milestone 7 — AI Prototype

Only after Milestones 1–6.

- [ ] Define narrow AI responsibility
- [ ] Create structured output schema
- [ ] Add evidence / reasoning inputs
- [ ] Add policy guardrails
- [ ] Add human approval
- [ ] Log model version
- [ ] Log prompt version
- [ ] Capture operator feedback
- [ ] Build basic UI

**Deliverable:** Working prototype.

---

### Milestone 8 — Evaluation

- [ ] Create test dataset
- [ ] Define scoring rubric
- [ ] Compare AI vs baseline
- [ ] Measure false positives
- [ ] Measure false negatives
- [ ] Measure human overrides
- [ ] Measure latency
- [ ] Measure cost
- [ ] Test edge cases
- [ ] Test unsafe / unsupported recommendations
- [ ] Document failure modes

**Deliverable:** Evaluation report.

---

### Milestone 9 — FDE Iteration

Simulate stakeholder feedback.

Examples:

> "Operators don't trust the recommendation."

Response:
- Add supporting evidence.
- Add confidence / uncertainty.
- Surface related historical requests.

> "Too many duplicates are being flagged."

Response:
- Improve clustering logic.
- Add human confirmation.
- Tune threshold.

> "The model recommends actions that our workflow does not allow."

Response:
- Strengthen policy layer.
- Separate model reasoning from allowed actions.

> "Leadership can't tell if this saves work."

Response:
- Build operational metrics dashboard.

**Deliverable:** V2 based on stakeholder feedback.

---

## 22. FDE Skills Being Practiced

### Customer / Operational Discovery

- Workflow mapping
- Stakeholder interviews
- Requirement discovery
- Root-cause analysis
- Identifying hidden constraints

### Software Engineering

- APIs
- Data pipelines
- Backend services
- Database design
- Frontend integration
- Deployment

### AI Engineering

- Structured model outputs
- Retrieval
- Evaluation
- Guardrails
- Human-in-the-loop systems
- Observability
- Prompt / model versioning

### Data Engineering

- Large public datasets
- Data quality
- Missing values
- Geographic data
- Temporal analysis

### Product Judgment

- Deciding when AI is useful
- Choosing narrow intervention points
- Measuring operational value
- Avoiding unnecessary complexity

### Communication

- Explaining findings to technical and non-technical stakeholders
- Distinguishing facts from hypotheses
- Documenting tradeoffs
- Presenting limitations
- Incorporating conflicting stakeholder requirements

---

## 23. FDE Engagement Journal

Use this after every work session.

### Session Template

**Date:** YYYY-MM-DD

**What I investigated:**  
TBD

**What I expected to find:**  
TBD

**What I actually found:**  
TBD

**Evidence:**  
TBD

**What surprised me:**  
TBD

**Hypothesis updated:**  
TBD

**New questions:**  
TBD

**Decision made:**  
TBD

**Next action:**  
TBD

---

## 24. Decision Log

### ADR-001 — Do Not Start With AI

**Decision:**  
The project will begin with operational analysis instead of an LLM prototype.

**Reason:**  
The intervention should be driven by demonstrated friction rather than by a predetermined technology.

**Status:** Accepted

---

### ADR-002 — Maintain Human Review

**Decision:**  
Initial AI recommendations will remain advisory.

**Reason:**  
The project involves operational routing and public-service workflows. Human validation provides safer evaluation and generates valuable feedback data.

**Status:** Accepted

---

### ADR-003 — Start With a Recent Data Window

**Decision:**  
Initial exploration will focus on July 1–September 30, 2026.

**Reason:**  
This provides a recent but manageable slice of operational data for rapid iteration.

**Status:** Accepted

---

## 25. Questions the Project Must Eventually Answer

By the end of the project, I should be able to answer:

1. What operational process did I study?
2. Who are the stakeholders?
3. Where did I initially think friction existed?
4. What did the data actually show?
5. Which hypotheses were rejected?
6. What was the root cause of the selected friction?
7. Why was AI appropriate?
8. What non-AI baseline did I compare against?
9. What did the AI system do?
10. What was the AI explicitly not allowed to do?
11. How did humans interact with it?
12. How did I evaluate it?
13. Where did it fail?
14. What stakeholder feedback changed the implementation?
15. What measurable operational outcome improved?
16. What would be required to deploy it in a real organization?

---

## 26. Portfolio Narrative

The finished project should support a story similar to:

> I treated NYC311 as a simulated forward-deployed engineering engagement. Rather than deciding upfront to build an AI application, I first mapped the service-request workflow, identified the stakeholders involved, and analyzed public operational and satisfaction data to find measurable friction.
>
> I formed several hypotheses around repeat requests, request completeness, routing, and resolution quality. I then tested those hypotheses against a recent operating window and selected one problem based on evidence.
>
> Before introducing an LLM, I created a deterministic baseline. I then built a narrowly scoped AI intervention with structured outputs, policy constraints, human review, feedback capture, and an evaluation suite.
>
> The most important lesson was that the hard part was not prompting the model. It was understanding the operational process well enough to determine what should be automated, what should remain deterministic, what humans needed to control, and how to measure whether the system actually improved the workflow.

---

## 27. Current Next Steps

### Immediate

- [ ] Create repository
- [ ] Commit this README
- [ ] Create project folders
- [ ] Build NYC311 Socrata ingestion script
- [ ] Pull July–September 2026 sample
- [ ] Run initial schema / missingness profile

### Do Not Do Yet

- [ ] ~~Build chatbot~~
- [ ] ~~Add vector database~~
- [ ] ~~Build multi-agent system~~
- [ ] ~~Fine-tune a model~~
- [ ] ~~Deploy Kubernetes~~
- [ ] ~~Choose final AI solution~~

First find the friction.

---

## 28. Disclaimer

This is an independent educational portfolio project using public NYC Open Data.

It is not affiliated with, endorsed by, or deployed by the City of New York or NYC311.

The project is designed to practice Forward Deployed AI Engineering, operational discovery, data analysis, AI system design, evaluation, and human-in-the-loop workflows.

---

## License

Choose a license before public release.

A common option for an educational software portfolio project is the MIT License.
