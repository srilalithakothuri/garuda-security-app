# Garuda Security System
*Detecting the Threat Within — Insider Threat Detection from System Logs*

## Project Overview
Garuda is an automated Insider Threat Detection and Response platform designed to identify malicious or negligent behavior from within an organization's perimeter. 

While most security tools focus on keeping bad actors *out* (like firewalls and antivirus), Garuda focuses on the users who already have legitimate access to your systems. By analyzing employee activity logs, network traffic, and device security states, Garuda flags suspicious behavioral patterns—such as logging in at odd hours, downloading massive amounts of data to USB drives, or suddenly changing file extensions to bypass data loss prevention.

### Why is it Useful?
1. **Fills a Critical Gap:** Insider threats are often the hardest to detect because the user already has valid credentials.
2. **Automated Analysis:** Security teams are often overwhelmed with raw log files. Garuda automatically digests messy CSV logs and presents prioritized, human-readable alerts.
3. **Immediate Mitigation:** Instead of just alerting the team, Garuda provides "Response Ops" (like revoking access or isolating a machine) and MDM controls directly from the dashboard to stop data exfiltration in its tracks.

---

## Core Features Details

### 1. File & Log Analysis Engine
- **What it does:** Administrators can drag-and-drop CSV system logs directly into the platform. A backend heuristic engine parses the logs looking for over 15 specific anomalies.
- **Anomalies Detected:** After-hours logins, unfamiliar IPs, huge data copies (indicative of exfiltration), hidden file metadata manipulation, disguised executables (e.g., `.jpg.exe`), log deletion, and unauthorized access attempts.
- **Result:** It generates an incident report with a "Threat Score" for each event and updates the dashboard charts in real-time.

### 2. Device Fleet Control (MDM)
- **What it does:** Tracks all corporate devices (laptops, mobile phones, servers) assigned to users.
- **Actionable Controls:** Administrators can issue direct commands to enrolled devices: 
  - *Lock Device*, *Wipe Data*, *Enforce Encryption*, *Isolate from Network*, *Initiate Malware Scan*, and *Revoke User*.
- **Syncing:** Actions are synced to the cloud (Firebase) to be picked up by an endpoint agent running on the actual devices.

### 3. Response Ops & SOC Integration
- **What it does:** A dedicated command-center view for taking drastic, global countermeasures during an active breach.
- **Actions:** 
  - *Revoke Access:* Instantly disables a user's account across the entire environment.
  - *Encrypt Data:* Simulates a global data lock to prevent physical theft of hard drives.
  - *Isolate Node:* Cuts off a compromised system from the internal corporate network while maintaining contact with the security server.
  - *Broadcast SOC Alert:* Escalates the threat level and pages the Security Operations Center.

### 4. Interactive Dashboard & Reporting
- **Dashboard:** Provides a live view of Total Events, High-Risk Anomalies, and simulated live Network Traffic Volume.
- **Reporting:** Security analysts can click "Export Incident Report" to automatically generate a professional PDF document containing all critical alerts, timestamps, and details for management review.

### 5. Learning Center
- **What it does:** An integrated educational hub explaining the psychology and mechanics behind insider threats (negligent vs. malicious), what indicators to look out for, and how to enact preventive measures like Least Privilege.

---

## How It Can Be Further Implemented (Future Roadmap)

While this application serves as a strong functional prototype and demonstration, it can be expanded into a true enterprise-grade product through the following implementations:

1. **Machine Learning Anomaly Detection:** 
   Currently, the log analysis relies on strict rules and heuristics (e.g., "if time > 6 PM and data > 100MB"). In the future, deploying an unsupervised Machine Learning model (like Isolation Forests or Autoencoders) could learn a specific user's baseline behavior and flag deviations entirely dynamically.

2. **Real-time Endpoint Agents:** 
   The platform currently simulates device enrollment. By developing an actual lightweight desktop agent (installed on Windows/macOS), the app could ingest logs in real-time via WebSockets without needing manual CSV uploads.

3. **Active Directory / SSO Integration:** 
   Instead of using its own SQLite database for user management, Garuda could integrate with Azure AD, Okta, or Google Workspace to automatically ingest the company's organizational chart and sync permissions.

4. **Automated Playbooks (SOAR):** 
   Allowing administrators to write "Playbooks." For example: `If Threat Score > 90 -> Automatically Lock Device -> Slack the Security Team -> Revoke Access.` This removes the need for manual button-clicks during a crisis.
