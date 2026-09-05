# FinSpectra — Autonomous Multi-Agent AML & Financial Crime Investigation Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0%2B-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Task--Driven-orange.svg)](https://www.langchain.com/langgraph)
[![Database](https://img.shields.io/badge/Database-Neon%20PostgreSQL-cyan.svg)](https://neon.tech/)
[![Groq LLM](https://img.shields.io/badge/LLM-Groq%20%2F%20Llama%203.3%2070B-purple.svg)](https://groq.com/)

**FinSpectra** is an autonomous, task-driven **Multi-Agent Anti-Money Laundering (AML) & Financial Crime Investigation Engine**. Built on **FastAPI**, **LangGraph**, **SQLAlchemy**, **Neon PostgreSQL**, and **Groq LLM (Llama 3.3 70B)**, it automates deep forensic investigations of financial crime alerts, performs multi-agent evidence gathering, calculates statistical risk scores, and generates regulatory Suspicious Activity Report (SAR) dossiers.

---

## 🌟 Key Features

* ⚡ **Atomic Alert Lifecycle Management**: Implements strict status state machine transitions (`OPEN` $\rightarrow$ `UNDER_INVESTIGATION` $\rightarrow$ `CLOSED` / `FAILED`) synchronized across Neon PostgreSQL database tables.
* 🤖 **Task-Driven LangGraph Orchestration**: Dynamically generates, routes, executes, and validates multi-agent forensic tasks based on money laundering typologies.
* 🔍 **Specialized Forensic Agent Nodes**:
  * **Evidence Retrieval Agent**: Gathers context on accounts, transactions, counterparties, and device associations.
  * **Behavior Analyzer Agent**: Calculates statistical velocity Z-scores ($\mu$, $\sigma$), transaction volume surges, and pass-through ratios.
  * **Graph Analyst Agent**: Computes 2-hop graph topological network metrics (beneficiary dispersion, device sharing, self-transfers).
  * **KYC Verifier Agent**: Cross-evaluates customer risk tiers, account age, and occupation against activity.
* 🎯 **Strict Typology Classifier**: Classifies patterns against an enforced, validated schema (`STRUCTURING`, `LAYERING`, `MULE_ACCOUNT`, `FAN_IN`, `FAN_OUT`, `UNKNOWN`) with automated schema validation and offline fallback.
* ⚖️ **Composite Risk Scoring Engine**: Calculates weighted risk scores ($0.35 \times \text{Prior} + 0.25 \times \text{Behavior} + 0.25 \times \text{Graph} + 0.15 \times \text{KYC}$) to make actionable decisions: `ALLOW`, `REVIEW`, or `BLOCK`.
* 📝 **Strictly Grounded Case Assembler**: Generates audit-ready SAR narrative dossiers strictly grounded in observed evidence facts without hallucinating unsupported details.
* 🛡️ **Hardened Reliability & Mock Fallback**: Includes auto-retries, timeouts, configurable token limits, production mock guards, and seamless offline development mock modes.
* 🎭 **Safe Showcase & Live Execution Modes**: Includes a demonstration CLI (`run_investigation_demo.py`) supporting 100% read-only safe mode execution and live database mutation mode.

---

## 🏗️ Architecture & Workflow

```mermaid
flowchart TD
    DB[(Neon PostgreSQL\nalerts Table)] -->|Claim Alert\nOPEN -> UNDER_INVESTIGATION| Repo[AlertRepository]
    Repo --> State[InvestigationState Initialization]

    subgraph Multi-Agent LangGraph Pipeline
        State --> TaskPlanner[Task Planner Node]
        TaskPlanner --> TaskRouter{Dynamic Task Router}

        TaskRouter -->|FETCH_EVIDENCE| EvidenceAgent[Evidence Retrieval Agent]
        TaskRouter -->|VERIFY_KYC| KYCAgent[KYC Verifier Agent]
        TaskRouter -->|ANALYZE_BEHAVIOR| BehaviorAgent[Behavior Analyzer Agent]
        TaskRouter -->|ANALYZE_GRAPH| GraphAgent[Graph Analyst Agent]

        EvidenceAgent --> TaskRouter
        KYCAgent --> TaskRouter
        BehaviorAgent --> TaskRouter
        GraphAgent --> TaskRouter

        TaskRouter -->|Tasks Complete| PlanChecker[Plan Satisfaction Checker]
        PlanChecker -->|Missing Evidence / Loop < 2| TaskPlanner
        PlanChecker -->|Plan Satisfied / Max Loops| TypologyNode[Typology Classifier Node]

        TypologyNode --> ScoringNode[Weighted Risk Scoring Node]
        ScoringNode --> CaseAssembler[Case Assembler & SAR Dossier Generator]
    end

    CaseAssembler -->|Persist InvestigationCase\nstatus = CLOSED| CaseDB[(investigation_cases Table)]
    CaseDB -->|Complete Alert\nalerts.status = CLOSED| Repo
```

---

## 📁 Repository Structure

```
Fin-Spectra/
├── app/
│   ├── agents/
│   │   ├── nodes/                   # Specialized Forensic Agent Nodes
│   │   │   ├── behavior_analyzer.py # Velocity Z-Scores & baseline metrics
│   │   │   ├── case_assembler.py    # Grounded SAR dossier generator
│   │   │   ├── evidence_retrieval.py# Database context aggregator
│   │   │   ├── graph_analyst.py     # Topological network & dispersion analyzer
│   │   │   ├── kyc_verifier.py      # Customer profile & risk verifier
│   │   │   ├── plan_checker.py      # Plan satisfaction & task completeness validator
│   │   │   ├── scoring_node.py      # Composite weighted risk scoring engine
│   │   │   ├── task_planner.py      # Dynamic task list planner
│   │   │   └── typology_classifier.py # Enforced typology classification node
│   │   ├── graph.py                 # LangGraph StateGraph & dynamic routers
│   │   ├── llm_client.py            # Hardened Groq client with mock fallback
│   │   └── state.py                 # InvestigationState TypedDict definition
│   ├── api/
│   │   └── routes_investigations.py # REST API endpoints
│   ├── models/
│   │   └── schema.py                # SQLAlchemy ORM models & Pydantic schemas
│   ├── repositories/
│   │   └── alert_repository.py      # Atomic Neon DB alert claim & lifecycle methods
│   ├── config.py                    # Pydantic environment configuration
│   ├── database.py                  # Database connection engine & sessionmaker
│   └── main.py                      # FastAPI application entrypoint
├── run_investigation_demo.py        # CLI Showcase Runner (Safe Mode & Live Mode)
├── test_alert_lifecycle.py          # Alert lifecycle synchronization unit test suite
├── test_case_assembler_grounding.py # Dossier grounding & payload pruning test suite
├── test_llm_client_reliability.py   # LLM client reliability & production guard test suite
├── test_neon_langgraph_pipeline.py  # End-to-End Neon DB to LangGraph integration test suite
├── test_typology_classifier_validation.py # Typology schema validation test suite
├── .env.example                     # Environment variables template
├── requirements.txt                 # Clean, minimal direct dependencies
└── README.md                        # Documentation
```

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.10+** (Python 3.14 fully supported)
* **PostgreSQL Database** (e.g. Neon PostgreSQL or local PostgreSQL)

### 1. Clone & Setup Virtual Environment

```bash
# Clone the repository
git clone https://github.com/vulcansmith-dev/Fin-Spectra.git
cd Fin-Spectra

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configure your credentials in `.env`:

```env
# Groq LLM API Key (https://console.groq.com/keys)
GROQ_API_KEY="gsk_your_actual_groq_key_here"

# Model Selection
GROQ_MODEL="llama-3.3-70b-versatile"

# Mock Mode (Set to true to bypass Groq API for offline testing)
MOCK_LLM_MODE="false"

# Neon PostgreSQL Connection URL
DATABASE_URL="postgresql://user:pass@ep-host.neon.tech/neondb?sslmode=require"
```

---

## 💻 Usage & Demonstration

### 1. Run Safe Showcase Runner (Read-Only Mode - Default)
Runs the complete multi-agent pipeline on an alert without claiming or modifying any database records:

```bash
python run_investigation_demo.py
```

### 2. Display Generated SAR Dossier Output
Runs in safe mode and outputs the formatted markdown Suspicious Activity Report (SAR) narrative:

```bash
python run_investigation_demo.py --show-dossier
```

### 3. Target a Specific Alert ID
Target a specific alert ID for investigation:

```bash
python run_investigation_demo.py --alert-id SYN_AL001
```

### 4. Live Persisted Pipeline Execution
Claims an alert (`OPEN` $\rightarrow$ `UNDER_INVESTIGATION`), executes the graph, persists the `InvestigationCase`, and marks the alert `CLOSED`:

```bash
python run_investigation_demo.py --live
```

---

## 🌐 FastAPI REST API Server

Start the FastAPI application server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

* **API Server**: `http://localhost:8000`
* **Swagger Interactive Docs**: `http://localhost:8000/docs`
* **ReDoc Documentation**: `http://localhost:8000/redoc`

### Key API Endpoints
* `POST /api/investigations/run` — Triggers a multi-agent investigation for a Phase-1 alert payload.
* `GET /api/investigations/cases` — Lists all persisted investigation cases.
* `GET /api/investigations/cases/{case_id}` — Retrieves state snapshot for a specific case.

---

## 🧪 Comprehensive Test Suite

Run the full suite of automated unit and integration tests using `pytest`:

```bash
python -m pytest
```

### Individual Test Suites
* **Alert & Case Lifecycle Tests**:
  ```bash
  python test_alert_lifecycle.py
  ```
* **End-to-End Neon DB Pipeline Integration**:
  ```bash
  python test_neon_langgraph_pipeline.py
  ```
* **Typology Classifier Schema Validation**:
  ```bash
  python test_typology_classifier_validation.py
  ```
* **Case Assembler Grounding & Payload Pruning**:
  ```bash
  python test_case_assembler_grounding.py
  ```
* **LLM Client Reliability & Production Guard**:
  ```bash
  python test_llm_client_reliability.py
  ```

---

## 📜 License

Distributed under the MIT License.
