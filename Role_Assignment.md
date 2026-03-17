# Role Assignment.md

---

# 📋 Role Assignment - กลุ่มที่ 7

## โครงการ: Triple-Layer Network สำหรับการขนส่งวัตถุอันตรายและการกู้ภัยฉุกเฉิน

---

## 👥 สมาชิกกลุ่ม

| รหัสนักศึกษา | ชื่อ-นามสกุล | ชื่อเล่น | Section |
|:---:|:---|:---:|:---:|
| 673380056-7 | รพีภัทร แก้วคูณ | ไผ่ | 2 |
| 673380068-0 | สุชาดา ศรีจักรโคตร | เค้ก | 2 |
| 673380286-0 | พิไลพร คำเวียง | เอวา | 2 |
| 673380297-5 | หทัยพัทธ วิสุทธิธรรม | แก้ม | 1 |
| 673380299-1 | เจตนิพิฐ แก้วทรัพย์ | ลูกแก้ว | 1 |

---

## 🎯 บทบาทและความรับผิดชอบ (Role Assignment)

### 1. **รพีภัทร แก้วคูณ (ไผ่) - Architect**

| ด้าน | รายละเอียด |
|:---|:---|
| **บทบาทหลัก** | สถาปนิกระบบ (System Architect) |
| **ความรับผิดชอบ** | - ออกแบบสถาปัตยกรรม Triple-Layer Network โดยรวม<br>- กำหนดโครงสร้างและองค์ประกอบของระบบ<br>- วางแผนการทำงานร่วมกันของแต่ละ Layer<br>- วิเคราะห์และเลือกเทคโนโลยีที่เหมาะสม<br>- กำหนดข้อกำหนดทางเทคนิค (Technical Specifications) |
| **ส่วนของโค้ดที่รับผิดชอบ** | - `TripleLayerNetworkSimulator` (โครงสร้างหลัก)<br>- `NetworkConstants` (การกำหนดค่าพารามิเตอร์)<br>- `NodeType`, `PacketType` (การออกแบบ Enum)<br>- การเชื่อมต่อระหว่าง Layers |
| **ส่วนของรายงาน** | - บทนำและภาพรวมโครงการ<br>- สถาปัตยกรรมระบบโดยรวม<br>- การออกแบบ Triple-Layer Network<br>- ข้อกำหนดทางเทคนิค |
| **การนำเสนอ** | - ช่วงที่ 1: บทนำและภาพรวมโครงการ (2 นาที)<br>- ช่วงที่ 4: สรุปและตอบคำถาม |

---

### 2. **สุชาดา ศรีจักรโคตร (เค้ก) - Engineer**

| ด้าน | รายละเอียด |
|:---|:---|
| **บทบาทหลัก** | วิศวกรเครือข่าย (Network Engineer) |
| **ความรับผิดชอบ** | - ออกแบบและพัฒนา ILNP (Identifier-Locator Protocol)<br>- จำลองการทำงานของ DetNet/TSN<br>- ออกแบบ Handover Mechanism<br>- กำหนดค่าพารามิเตอร์เครือข่าย (Bandwidth, Latency, Reliability)<br>- ทดสอบประสิทธิภาพการเชื่อมต่อ |
| **ส่วนของโค้ดที่รับผิดชอบ** | - `simulate_handover()`<br>- `get_connected_core()`<br>- `find_alternative_connections()`<br>- `calculate_signal_strength()`<br>- `_setup_connections()` |
| **ส่วนของรายงาน** | - การทำงานของ ILNP และ DetNet<br>- Handover Mechanism<br>- การเชื่อมต่อระหว่าง Layers<br>- พารามิเตอร์เครือข่าย |
| **การนำเสนอ** | - ช่วงที่ 1: Model Maturity and Improvement (ร่วมกับไผ่และเอวา)<br>- ช่วงที่ 2: DAFT Domain Interface Mapping (ร่วมกับเอวาและแก้ม)<br>- ช่วงที่ 4: ตอบคำถาม |

---

### 3. **พิไลพร คำเวียง (เอวา) - Specialist**

| ด้าน | รายละเอียด |
|:---|:---|
| **บทบาทหลัก** | ผู้เชี่ยวชาญด้าน AI และ Digital Twin (AI/Digital Twin Specialist) |
| **ความรับผิดชอบ** | - ออกแบบและพัฒนา Edge AI Models<br>- พัฒนา Anomaly Detection Model<br>- พัฒนา Route Optimization Model<br>- ออกแบบ Digital Twin<br>- ปรับปรุงระบบด้วย RAG และ Federated Learning |
| **ส่วนของโค้ดที่รับผิดชอบ** | - `class DigitalTwin`<br>- `class AnomalyDetectionModel`<br>- `class RouteOptimizationModel`<br>- `predict_node_failure()`<br>- `predict_handover_needed()`<br>- `check_emergencies()` |
| **ส่วนของรายงาน** | - การทำงานของ Edge AI และ Digital Twin<br>- Anomaly Detection และ Z-score<br>- Route Optimization และ A* Algorithm<br>- Federated Learning และ Human-in-the-loop |
| **การนำเสนอ** | - ช่วงที่ 1: Model Maturity and Improvement (ร่วมกับไผ่และเค้ก)<br>- ช่วงที่ 2: DAFT Domain Interface Mapping (ร่วมกับเค้กและแก้ม)<br>- ช่วงที่ 4: ตอบคำถาม |

---

### 4. **หทัยพัทธ วิสุทธิธรรม (แก้ม) - DevOps**

| ด้าน | รายละเอียด |
|:---|:---|
| **บทบาทหลัก** | วิศวกร DevOps และความปลอดภัย (DevOps & Security Engineer) |
| **ความรับผิดชอบ** | - ออกแบบ Quantum-resistant Encryption<br>- พัฒนา Tree of Thoughts และ Chain of Thought<br>- จัดทำ Governance Framework<br>- กำหนด Security Policy<br>- ออกแบบ Audit Trail และ Compliance Monitoring |
| **ส่วนของโค้ดที่รับผิดชอบ** | - `class QuantumResistantEncryption`<br>- `class TreeOfThoughts`<br>- `class ChainOfThought`<br>- `_handover_solution_paths()`<br>- `_battery_management_paths()`<br>- `_emergency_response_paths()` |
| **ส่วนของรายงาน** | - ความปลอดภัยแบบ Quantum-resistant<br>- Tree of Thoughts Reasoning<br>- Chain of Thought Reasoning<br>- Governance Framework<br>- Compliance และ Security |
| **การนำเสนอ** | - ช่วงที่ 2: DAFT Domain Interface Mapping (ร่วมกับเค้กและเอวา)<br>- ช่วงที่ 3: Quality Metrics, Governance, Live Demo (ร่วมกับลูกแก้ว)<br>- ช่วงที่ 4: ตอบคำถาม |

---

### 5. **เจตนิพิฐ แก้วทรัพย์ (ลูกแก้ว) - Tester/QA**

| ด้าน | รายละเอียด |
|:---|:---|
| **บทบาทหลัก** | ผู้ทดสอบและประกันคุณภาพ (Tester & Quality Assurance) |
| **ความรับผิดชอบ** | - ทดสอบระบบทุกฟังก์ชัน<br>- วัดและบันทึก Performance Metrics<br>- ออกแบบ Demo Scenarios<br>- พัฒนา Demo Controller<br>- ตรวจสอบความสอดคล้องกับมาตรฐาน |
| **ส่วนของโค้ดที่รับผิดชอบ** | - `class DemoController`<br>- `demo_b1_handover()`<br>- `demo_b2_anomaly()`<br>- `demo_b2_emergency()`<br>- `demo_b2_battery()`<br>- `run_demo_menu()`<br>- การเก็บสถิติ (`metrics`) |
| **ส่วนของรายงาน** | - Quality Metrics และ KPI<br>- ผลการทดสอบ<br>- การสาธิตการทำงาน (Live Demo)<br>- การตรวจสอบมาตรฐาน (3GPP, IEEE, ITU, NIST) |
| **การนำเสนอ** | - ช่วงที่ 3: Quality Metrics, Governance, Live Demo (ร่วมกับแก้ม)<br>- ช่วงที่ 4: ตอบคำถาม |

---
