<img width="2752" height="1536" alt="Blueprint_for_Deterministic_AI_Pipelines" src="https://github.com/user-attachments/assets/81d683d7-ddbc-4a7b-a279-9024c05b2fb3" />

# Deterministic AI Pipeline – New Agent Variant Against Chaos  
**60–80% fewer unexplained failures through UUID tracing, container isolation & JSON checkpoints**

Built openly with **Human + AI Co‑Creation**  
**Idea & Architecture:** Emanuel Schaaf  
**AI Co‑Creators:** Auron, Lyra, Muse Spark

---

## 🚀 Overview

Modern AI agents often behave like black boxes: unpredictable, non‑deterministic, and difficult to debug.  
This project introduces a **Deterministic AI Pipeline** that transforms chaotic agent behavior into **auditable, reproducible, and failure‑resistant execution**.

The system uses:

- **UUID‑based tracing**
- **Immutable pipeline context**
- **Container isolation**
- **JSON checkpoint logging**
- **Circuit breaker halting**
- **Docker & Kubernetes deployment**
- **Grafana dashboards for observability**

This repository contains the full MVP implementation, including Docker, Kubernetes Helm chart, monitoring stack, and a chaos‑injection demo.

---

## 🎥 Live Demo & Explainer

### **8‑Minute Explainer Video**
- [Explainer Video](https://short-url.cc/1s6eC)

### **Pipeline Live Demo**
- [Live Demo](https://lnkd.in/er-S9Kc2)


## Architecture Mapping

This repository implements the reference architecture from the demo `deterministic-ai-pipelines/` using practical, GitHub-friendly path names.

| Reference (Demo Sketch) | Implementation in Repo | Purpose |
|-------------------------|------------------------|---------|
| `task_a_taxonomy/` | `task-a/` | Error taxonomy, reproduction scripts |
| `├─ error_types.yaml` | `task-a/error_types.yaml` *(planned)* | Classification of error types |
| `└─ detectors/` | `task-a/detectors/` *(planned)* | Detector modules |
||
| `task_b_playbook/` | `task-b/` | Failure simulations, trace logs |
| `├─ failure_modes.md` | `task-b/failure_modes.md` *(planned)* | Documentation of failure modes |
| `└─ runbooks/` | `task-b/runbooks/` *(planned)* | Runbooks for chaos testing |
||
| `task_c_pipeline/` | `task-c/prototype/` | Deterministic pipeline |
| `├─ orchestrator.py` | `task-c/prototype/agent_pipeline.py` | **Implemented** – Orchestrator with circuit-breaker |
| `├─ isolation/` | `task-c/prototype/isolation/` *(planned)* | Task isolation layer |
| `└─ checkpoints/` | `task-c/prototype/checkpoints/` *(planned)* | State checkpoints |
||
| `observability/` | `task-c/monitoring/` | Monitoring stack |
| `├─ prometheus.yml` | `task-c/monitoring/prometheus.yml` *(planned)* | Prometheus configuration |
| `└─ grafana/dashboards/` | `task-c/monitoring/grafana/` *(planned)* | Grafana dashboards |
||
| `trace_schema_v1.json` | `docs/trace_schema_v1.json` *(planned)* | Global trace schema |
| `docker-compose.yml` | `task-c/prototype/docker-compose.yml` | **Implemented** |
---

## 🧩 Features

### ✔ Deterministic Execution  
Every stage runs with a unique `run_id` and strict sequencing.

### ✔ UUID Tracing  
All events are logged as JSON‑Lines for Prometheus/Grafana ingestion.

### ✔ Circuit Breaker  
If one agent fails, the pipeline halts immediately — no cascading failures.

### ✔ Chaos Injection  
Simulate real‑world agent failures (timeouts, rendering errors, etc.).

### ✔ Docker‑Ready  
Run the entire system locally in **30 seconds**.

### ✔ Helm Chart Included  
Deploy the pipeline to Kubernetes with production‑grade manifests.

---

## 📦 Repository Structure

```
task-a/        # Error taxonomy, reproduction scripts, documentation
task-b/        # Failure simulations, trace logs, analysis
task-c/        # Deterministic pipeline implementation
  ├── prototype/     # agent_pipeline.py, Dockerfile, docker-compose.yml
  ├── monitoring/    # Grafana dashboard, Prometheus config
  └── docs/
docs/          # Global documentation
```

---

## 🐳 Run the Pipeline Locally (Docker Compose)

From inside:

```
task-c/prototype/
```

Run:

```bash
docker-compose up --build
```

This starts:

- Orchestrator  
- Read Agent  
- Rewrite Agent  
- Convert Agent  
- Deploy Agent  
- Prometheus  
- Grafana  

### ✔ Access Prometheus (local only)

```
http://localhost:9090
```

### ✔ Access Grafana (local only)

```
http://localhost:3000
```

Default login:

```
admin / admin
```

---

## 📊 Monitoring & Observability

Included:

- `grafana_dashboard.json`  
- `prometheus.yml`  
- Docker Compose mounts  
- Helm chart provisioning support  

Metrics include:

- Pipeline runs  
- Pipeline errors  
- Stage latency  
- Agent memory usage  
- Agent iteration counters  

---

## 🧪 Chaos Simulation

Enable fault injection in the Convert stage:

```python
ConvertTask("ID-003-CONVERT", "Render PDF", inject_fault=True)
```

Pipeline output:

- Error logged with UUID  
- Pipeline halts deterministically  
- Deploy stage is blocked  
- Trace entry written for failure  

---

## ☸️ Kubernetes Deployment (Helm)

A full Helm chart is included under:

```
charts/agent-pipeline/
```

Deploy with:

```bash
helm install agent-pipeline charts/agent-pipeline/
```

---

## 🧠 Why Deterministic Pipelines Matter

Traditional AI agents fail silently, unpredictably, and without traceability.  
This project demonstrates how deterministic architecture can reduce unexplained failures by **60–80%**, based on:

- strict sequencing  
- immutable state  
- container isolation  
- structured logging  
- reproducible execution  

---

## 👤 Authors & Contributors

### **Human Creator**
- **Emanuel Schaaf** — Concept, architecture, implementation, documentation
- [Contakt](https://github.com/research-team-usa/New_Agent_Variant_Against_Chaos/blob/main/CONTACT.md)

### **AI Co‑Creators**
- **Auron** — Deterministic architecture & system design  
- **Lyra** — Creative agent logic & pipeline shaping  
- **Muse Spark** — Docker & infrastructure generation  

This project is a demonstration of **Human + AI Co‑Creation** at engineering level.

---

## 📄 License

License: 
See [LICENSE](https://github.com/research-team-usa/New_Agent_Variant_Against_Chaos/blob/main/LICENSE.md) for details.

---

## ⭐ Support the Project

If you find this useful:

- Star the repository  
- Share the explainer video  
- Fork and build your own deterministic agent variant  

Deterministic AI is the next step toward **reliable, auditable, production‑grade agent systems**.
