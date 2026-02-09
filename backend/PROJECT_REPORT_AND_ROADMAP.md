# GARUDA: Next-Gen Insider Threat Detection System
## Technical Whitepaper & Development Roadmap

**Version:** 1.0  
**Date:** February 2026  
**Status:** Alpha Prototype (Hackathon Release)

---

## 1. Executive Summary
Garuda is an automated security platform designed to detect, analyze, and neutralize **Insider Threats**—security risks that originate from within an organization. Unlike traditional firewalls that guard against external attacks, Garuda focuses on the user behaviors, device states, and data movements of authorized employees to identify malicious intent or negligence.

## 2. Problem Statement
Modern enterprises face significant risks from trusted users:
*   **Data Exfiltration**: Employees copying sensitive IP to personal drives/USBs.
*   **After-Hours Access**: Unauthorized logins during non-business hours.
*   **Compromised Devices**: Corporate devices infected with malware acting as beachheads.
*   **Lack of Visibility**: Security teams (SOC) often lack real-time correlation between endpoint status and user logs.

## 3. Current Solution Architecture (Prototype)
The current hackathon MVP demonstrates the core "Loop of Security": **Detect -> Analyze -> Respond**.

*   **Frontend**: HTML5/TailwindCSS Dashboard for visualization.
*   **Backend**: Python Flask Application for API logic and orchestration.
*   **Database**: SQLite for local transactional data (Users/Logs).
*   **Cloud Operations**: Firebase Realtime Database for instant command propagation (C2) and live alerts.
*   **Analysis Engine**: Heuristic-based logic to score anomalies (e.g., Time-of-day violations, Bytes transferred thresholds).

---

## 4. Road to Industry Standard (Production Roadmap)
To transition Garuda from a prototype to an Enterprise-Grade Security Product (SIEM/SOAR), the following architectural evolution is required.

### Phase 1: Robustness & Scale (Months 1-3)
*   **Database Migration**: Move from **SQLite** to **PostgreSQL**. This enables concurrent writes, better data integrity, and scalability for 1000+ users.
*   **Async Processing**: Introduce **Celery & Redis**. Currently, log analysis happens properly during the HTTP request. This will time out with large files. Processing must be moved to background job queues.
*   **Identity Management**: Replace simple session auth with **JWT (JSON Web Tokens)** and integrate **SSO (Single Sign-On)** support (e.g., 'Login with Google/Microsoft') using OAuth2. Enterprises mandate SSO.

### Phase 2: Advanced Detection (Months 4-6)
*   **Elasticsearch Integration (ELK Stack)**: Replace basic SQL log search with Elasticsearch. This allows searching millions of logs in milliseconds and creating complex visualizations with Kibana.
*   **Machine Learning**: Move beyond simple "If/Then" rules. Implement **Isolation Forests** (Unsupervised Learning) to detect anomalies that *don't* match known patterns (e.g., "User X usually types 40 words/min, now typing 120 words/min script injection").

### Phase 3: The "Real" Agent (Months 6-9)
*   **Endpoint Agent (Go/Rust)**: Determine the endpoint strategy. The current web simulation needs a real binary agent installed on laptops.
    *   *Action*: Build a lightweight agent using **Golang** that runs as a system service.
    *   *Tech*: Use **Osquery** to query operating system state (USB events, process tree) and forward to the server.
    *   *Protocol*: Switch from REST polling to **gRPC** or **WebSockets** for persistent, bidirectional communication.

### Phase 4: Compliance & Security (Continuous)
*   **Audit Trails**: Every action by an Admin (e.g., "Wipe Device") must be potentially logged to an immutable ledger for legal auditing.
*   **RBAC (Role-Based Access Control)**: Define strict roles: `L1 Analyst` (View Only), `L2 Responder` (Can Isolate), `Admin` (Can Wipe).
*   **Encryption**: Ensure all sensitive log data is encrypted at rest (AES-256).

---

## 5. Technology Stack Recommendations (Production)

| Component | Prototype Selection (Current) | Production Recommendation (Target) |
| :--- | :--- | :--- |
| **Language** | Python (Flask) | Python (FastAPI) or Go |
| **Database** | SQLite | PostgreSQL (Relational) + TimescaleDB (Time-series) |
| **Search** | SQL `LIKE` queries | Elasticsearch / OpenSearch |
| **Realtime** | Firebase | Redis Pub/Sub + WebSockets |
| **Frontend** | HTML Templates | React / Next.js (SPA) |
| **Deployment** | Local / Render | Docker + Kubernetes (AWS EKS / GKE) |

## 6. Conclusion
Garuda has successfully demonstrated the viability of integrating MDM controls with log analysis. By systematically upgrading the backend to handle asynchronous loads and replacing the simulation layer with real endpoint hooks (Osquery), Garuda can compete with entry-level commercial tools in the insider threat space.
