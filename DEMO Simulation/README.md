# Triple-Layer Network for Hazardous Material Transport and Emergency Rescue Operations

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A comprehensive network simulation combining 5G/6G deterministic core, satellite backup, and drone mesh networks with edge AI and digital twin technologies.

## 📋 Table of Contents
- [Overview](#overview)
- [Team Members](#team-members)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Scenarios](#scenarios)
- [Documentation](#documentation)

## Overview

This project presents a **Triple-Layer Network Architecture** designed for:
- Long-distance hazardous material transport
- Emergency rescue operations in risk-prone areas

The network ensures:
- **< 1 ms latency** for remote control operations
- **99.9999% reliability** (six nines)
- **Quantum-safe security** against future attacks
- **Seamless connectivity** in remote and disaster areas

## Team Members

| Role | Name | ID |
|------|------|-----|
| Architect | รพีภัทร แก้วคูณ (ไผ่) | 673380056-7 |
| Engineer | สุชาดา ศรีจักรโคตร (เค้ก) | 673380068-0 |
| Specialist | พิไลพร คำเวียง (เอวา) | 673380286-0 |
| DevOps | หทัยพัทธ วิสุทธิธรรม (แก้ม) | 673380297-5 |
| Tester/QA | เจตนิพิฐ แก้วทรัพย์ (ลูกแก้ว) | 673380299-1 |

## Architecture
+---------------------+
| INTELLIGENCE LAYER |
| Edge AI + Digital Twin |
+---------------------+
|
+--------------------+--------------------+
| | |
v v v
+----------------+ +----------------+ +----------------+
| LAYER 1 | | LAYER 2 | | LAYER 3 |
| Deterministic | | Satellite | | Emergency |
| Core | | Backup | | Mesh |
| | | | | |
| 5G/6G + TSN | | LEO Satellite | | Drone Swarm |
| ILNP + RSUs | | 3GPP NTN | | On-demand |
+----------------+ +----------------+ +----------------+

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/triple-layer-network.git
cd triple-layer-network

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env