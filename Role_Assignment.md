# Role Assignment - Group 7

## Project: 
# National long distance transport network
---


##  Team Members

| Role | Name | ID | Section |
|------|------|-----|---------|
| Architect | รพีภัทร แก้วคูณ (ไผ่) | 673380056-7 | 2 |
| Engineer | สุชาดา ศรีจักรโคตร (เค้ก) | 673380068-0 | 2 |
| Specialist | พิไลพร คำเวียง (เอวา) | 673380286-0 | 2 |
| DevOps | หทัยพัทธ วิสุทธิธรรม (แก้ม) | 673380297-5 | 1 |
| Tester/QA | เจตนิพิฐ แก้วทรัพย์ (ลูกแก้ว) | 673380299-1 | 1 |

---

## Roles and Responsibilities

### 1. **Rapeephat Kaewkoon (Pai) - Architect**

| Aspect | Details |
|:---|:---|
| **Primary Role** | System Architect |
| **Responsibilities** | - Design overall Triple-Layer Network architecture<br>- Define system structure and components<br>- Plan integration of each Layer<br>- Analyze and select appropriate technologies<br>- Define Technical Specifications |
| **Code Responsibilities** | - `TripleLayerNetworkSimulator` (main structure)<br>- `NetworkConstants` (parameter configuration)<br>- `NodeType`, `PacketType` (Enum design)<br>- Inter-layer connections |
| **Report Sections** | - Introduction and project overview<br>- Overall system architecture<br>- Triple-Layer Network design<br>- Technical specifications |

---

### 2. **Suchada Srijakkot (Cake) - Engineer**

| Aspect | Details |
|:---|:---|
| **Primary Role** | Network Engineer |
| **Responsibilities** | - Design and develop ILNP (Identifier-Locator Protocol)<br>- Simulate DetNet/TSN operations<br>- Design Handover Mechanism<br>- Configure network parameters (Bandwidth, Latency, Reliability)<br>- Test connection performance |
| **Code Responsibilities** | - `simulate_handover()`<br>- `get_connected_core()`<br>- `find_alternative_connections()`<br>- `calculate_signal_strength()`<br>- `_setup_connections()` |
| **Report Sections** | - ILNP and DetNet operations<br>- Handover Mechanism<br>- Inter-layer connections<br>- Network parameters |


---

### 3. **Pilaiporn Khamwiang (Eva) - Specialist**

| Aspect | Details |
|:---|:---|
| **Primary Role** | AI & Digital Twin Specialist |
| **Responsibilities** | - Design and develop Edge AI Models<br>- Develop Anomaly Detection Model<br>- Develop Route Optimization Model<br>- Design Digital Twin<br>- Improve system with RAG and Federated Learning |
| **Code Responsibilities** | - `class DigitalTwin`<br>- `class AnomalyDetectionModel`<br>- `class RouteOptimizationModel`<br>- `predict_node_failure()`<br>- `predict_handover_needed()`<br>- `check_emergencies()` |
| **Report Sections** | - Edge AI and Digital Twin operations<br>- Anomaly Detection and Z-score<br>- Route Optimization and A* Algorithm<br>- Federated Learning and Human-in-the-loop |


---

### 4. **Hathaipat Wisutthitham (Gam) - DevOps**

| Aspect | Details |
|:---|:---|
| **Primary Role** | DevOps & Security Engineer |
| **Responsibilities** | - Design Quantum-resistant Encryption<br>- Develop Tree of Thoughts and Chain of Thought<br>- Create Governance Framework<br>- Define Security Policy<br>- Design Audit Trail and Compliance Monitoring |
| **Code Responsibilities** | - `class QuantumResistantEncryption`<br>- `class TreeOfThoughts`<br>- `class ChainOfThought`<br>- `_handover_solution_paths()`<br>- `_battery_management_paths()`<br>- `_emergency_response_paths()` |
| **Report Sections** | - Quantum-resistant Security<br>- Tree of Thoughts Reasoning<br>- Chain of Thought Reasoning<br>- Governance Framework<br>- Compliance and Security |


---

### 5. **Jetnipit Kaewsap (Lookkaew) - Tester/QA**

| Aspect | Details |
|:---|:---|
| **Primary Role** | Tester & Quality Assurance |
| **Responsibilities** | - Test all system functions<br>- Measure and record Performance Metrics<br>- Design Demo Scenarios<br>- Develop Demo Controller<br>- Verify standards compliance |
| **Code Responsibilities** | - `class DemoController`<br>- `demo_b1_handover()`<br>- `demo_b2_anomaly()`<br>- `demo_b2_emergency()`<br>- `demo_b2_battery()`<br>- `run_demo_menu()`<br>- Statistics collection (`metrics`) |
| **Report Sections** | - Quality Metrics and KPIs<br>- Test results<br>- Live Demonstration<br>- Standards compliance (3GPP, IEEE, ITU, NIST) |
