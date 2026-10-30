# Hermetic Review-Gate: Zero-Trust AI Coding Adjudication
A sovereign, air-gapped verification pipeline designed to prevent autonomous coding agents from gaming test suites, weakening assertions, or stubbing core logic.

## The Problem
Traditional agent evaluation and execution loops rely on an "honor system." When unconstrained frontier models hit difficult logic walls, default reinforcement incentives push them to find the path of least resistance: rewriting conftest.py, softening test assertions, or mocking out database connections just to secure a green build.

## The Solution: Hermetic Zero-Trust Architecture
1. **SHA-256 Fixture Lock:** Cryptographically snapshots protected test fixtures before worker execution. Any tampering triggers an immediate breaker trip.
2. **Local Gemma Diff Adjudication:** Routes worker git diffs through local Gemma 12B (via LM Studio at temp 0.0) to flag assertion-weakening, hardcoded mocks, and test deletion.
3. **The Redemption Loop:** Feeds clinical rejection critique back into the worker model's context window for an honest retry under immutable constraints.

## Threat Model
- **In scope:** a worker agent with write access to the repo that edits or deletes protected fixtures, weakens assertions, stubs logic, or deletes tests.
- **Fail-closed:** any missing manifest, hash mismatch, unreachable adjudicator, timeout, or response without an explicit `VERDICT: PASS` blocks the build.
- **Out of scope:** an attacker who can modify the gate itself, the manifest, or the host. Keep `/opt/harness` and `.harness_lock.json` outside the worker's write access.

## Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Pass |
| 1 | Lock manifest missing |
| 2 | Protected fixture changed or missing |
| 3 | Adjudicator returned FAIL |
| 4 | Adjudicator unreachable, timed out, or gave no clear verdict |

## Quick Start
1. Run `python harness_lock.py` to create the baseline hash manifest.
2. Build the container: `docker build -t review-gate:latest .`
3. Run it with the repo mounted read-only:
   ```
   docker run --rm --add-host=host.docker.internal:host-gateway \
     -v "$PWD":/workspace:ro review-gate:latest
   ```
   The entrypoint runs `harness_lock.py verify` and then `adjudicate.py`. Set `LM_STUDIO_URL` and `ADJUDICATOR_MODEL` to override the defaults.

---

## Original Framework Overview

### Architecture Overview

A production-grade, scalable infrastructure for systematic Large Language Model evaluation. This framework implements modular benchmarking matrices, automated dataset ingestion pipelines, and comprehensive token-tracking schemas designed for enterprise model assessment workflows.

---

### Directory Structure

```
llm-evaluation-framework/
├── benchmarks/                 # Benchmark suite definitions & execution configs
│   ├── tasks/                  # Individual evaluation task implementations
│   │   ├── reasoning/          # Logical, mathematical, and code reasoning tests
│   │   ├── generation/         # Text generation quality assessments
│   │   ├── classification/     # Classification accuracy benchmarks
│   │   └── safety/             # Guardrails, alignment & safety evaluations
│   ├── configs/                # Task configuration files (YAML/JSON)
│   └── suites/                 # Pre-packaged benchmark collections
├── data/                       # Dataset management layer
│   ├── raw/                    # Raw ingested datasets
│   ├── processed/              # Cleaned & standardized evaluation sets
│   ├── splits/                 # Train/validation/test partitionings
│   └── loaders/                # Data ingestion utilities by source format
├── evaluators/                 # Core evaluation logic
│   ├── metrics/                # Metric computation implementations
│   │   ├── accuracy.py         # Exact match & classification accuracy
│   │   ├── similarity.py       # Semantic similarity (BERTScore, etc.)
│   │   └── custom/             # Domain-specific metric extensions
│   ├── judges/                 # Model-as-judge evaluators
│   ├── automated/              # Fully programmatic evaluation scripts
│   └── human_alignment/        # Human preference integration tools
├── token_tracker/              # Token usage monitoring & optimization
│   ├── schemas/                # Tracking schema definitions (JSON Schema)
│   ├── collectors/             # Real-time token consumption hooks
│   │   ├── per_request.py      # Granular request-level tracking
│   │   └── aggregate.py        # Batch/session-level aggregation
│   └── reports/                # Token usage analytics & visualization
├── pipelines/                  # Orchestration layer
│   ├── config.yaml             # Pipeline DAG definitions
│   ├── runners/                # Execution engines (batch/streaming)
│   └── callbacks/              # Event hooks for logging/alerting
├── results/                    # Experiment outputs & artifacts
│   ├── experiments/            # Individual run directories
│   │   ├── {uuid}/             # Versioned experiment folders
│   │   │   ├── config.yaml     # Immutable run configuration snapshot
│   │   │   ├── metrics.json    # Computed evaluation results
│   │   │   └── samples.csv     # Input/output sample traces
│   │   └── ...
│   ├── comparisons/            # Cross-model comparative analyses
│   └── dashboards/             # Visualization source files
├── models/                     # Model integration abstractions
│   ├── providers/              # Provider-specific adapters
│   │   ├── openai.py           # OpenAI API client wrapper
│   │   ├── anthropic.py        # Anthropic Claude adapter
│   │   ├── local.py            # Local/inference-server connectors
│   │   └── base.py             # Abstract provider interface
│   └── configs/                # Model parameter configurations
├── tests/                      # Framework test suites
│   ├── unit/                   # Component-level unit tests
│   ├── integration/            # End-to-end pipeline validation
│   └── fixtures/               # Shared test data & mocks
├── scripts/                    # Operational utilities
│   ├── run_benchmark.sh        # CLI entrypoint for benchmark execution
│   ├── export_results.py       # Results exportation helpers
│   └── cleanup_cache.py        # Artifact lifecycle management
├── docs/                       # Extended documentation
│   ├── architecture.md         # Deep-dive architectural specs
│   ├── contributing.md         # Contribution guidelines
│   └── api_reference.md        # Public interface documentation
├── .gitignore                  # Version control exclusions
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project metadata & build configuration
└── README.md                   # This file
```

---

### Core Components

### Benchmarking Matrices (`benchmarks/`)
- **Task Abstractions**: Self-contained evaluation units with standardized input/output contracts
- **Combinatorial Configs**: YAML-driven parameter matrices for systematic hyperparameter sweeps across models, prompts, and temperature settings
- **Suite Composition**: Pre-defined collections (e.g., "reasoning-battery", "production-readiness-check") for repeatable assessments

### Dataset Ingestion Pathways (`data/`)
- **Multi-format Loaders**: Native support for JSONL, CSV, Parquet, HF Datasets, and custom formats
- **Pipeline Stages**: Raw → Validated → Standardized → Partitioned transformation chain
- **Schema Enforcement**: JSON Schema validation at ingestion to guarantee data integrity

### Token-Tracking Schemas (`token_tracker/`)
- **Granular Instrumentation**: Per-request tracking of prompt tokens, completion tokens, latency, and cost
- **Aggregation Layers**: Batch-level summaries for throughput analysis and optimization
- **Export Formats**: CSV, JSON, and database-backed persistence for historical trend analysis

---

### Quick Start

```bash
# Clone and install dependencies
git clone https://github.com/dv8tion2u/llm-evaluation-framework.git
cd llm-evaluation-framework
pip install -r requirements.txt

# Run a sample benchmark suite
python scripts/run_benchmark.sh --suite reasoning-battery --model openai:gpt-4o
```

---

### Design Principles

1. **Modularity**: Each evaluation component operates as an isolated unit with well-defined interfaces
2. **Reproducibility**: Immutable experiment configs and versioned results ensure exact recreatability
3. **Scalability**: Horizontal pipeline execution supporting parallel model evaluations across distributed clusters
4. **Extensibility**: Plugin-style architecture for custom metrics, providers, and data loaders
5. **Observability**: Comprehensive logging at every stage from ingestion through result aggregation

---

### License & Contribution

This framework is maintained as open-source infrastructure. See `docs/contributing.md` for development guidelines.
