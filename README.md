# RTDS-Dataset-Generation-Framework

[![GitHub Repository](https://img.shields.io/badge/GitHub-sudipbarua%2FRTDS--Dataset--Generation--Framework-blue?logo=github)](https://github.com/sudipbarua/RTDS-Dataset-Generation-Framework.git)

This repository contains the implementation of the **RTDS (Red Teaming & Data Shift) Framework**. This automated framework is designed to generate high-quality, realistic network traffic datasets for evaluating Intrusion Detection Systems (IDS). Unlike traditional datasets, this framework focuses on two critical, often overlooked aspects:

1.  **Concept Drift:** Simulating evolving traffic patterns (e.g., changes in user behavior, throughput, and protocols) to test IDS robustness over time.
2.  **Red Teaming Scenarios:** Leveraging automated adversary emulation (using **Caldera** and **Metasploit**) to conduct objective-based attack campaigns rather than simple, isolated exploits.

The framework utilizes automated bots to mimic human behavior for benign traffic and sophisticated scripts for malicious activities, operating within a controlled cloud network environment.

---

## Key Components

The RTDS Framework consists of three main components for comprehensive network traffic generation and evaluation:

### 1. Normal Traffic Generation

**Location:** `/workspaces/RTDS-Dataset-Generation-Framework/user_profiles/oop/`

The `BotGenerator` and `NormalBot` classes in `bot_executor.py` generate realistic benign network traffic through automated bots that simulate human user behavior. 

#### Bot Types:
- **Normal Bots** - Execute sequential, typical user tasks for realistic traffic patterns
- **CD (Concept Drift) Bots** - Execute parallel, high-volume tasks to introduce statistical shifts in traffic patterns

#### Capabilities:
Bots can perform the following user activities:

* **Web Browsing:**
  * Google, YouTube, Facebook, LinkedIn, Amazon, Booking.com
  * Search functionality with randomized keywords
  * Link clicking and content exploration
  * Cookie acceptance and authentication

* **Email Management:**
  * Send emails via Mailcow server
  * Support for attachments
  * CC/BCC recipients
  * Randomized email subjects and body content

* **Instant Messaging:**
  * Skype-based chat interactions
  * Random message selection from predefined text lists
  * Multi-user conversation simulation

* **File Transfers:**
  * FTP client operations
  * File downloads from configured FTP servers
  * Support for different file types based on drift requirements

#### Bot Serialization & Remote Execution:
- Bot objects are created with all their configurations, methods, and action lists
- Bots are serialized using Python's `pickle` module and saved as `.pickle` files
- These serialized bots can be transferred to remote machines for distributed execution
- Saved bots are organized in:
  - `normal_bots/` directory for standard traffic generation
  - `cd_bots/` directory for concept drift traffic generation

#### Configuration:
Bots are configured via YAML files:
- `bot_config_parameters.yml` - Defines browsing sites, email parameters, chatting accounts, FTP servers
- `bot_specs` - Specifies ranges for number of browsers, chats, emails, and FTP operations
- Inter-arrival times (IAT) and task duration parameters

---

### 2. Concept Drift Detection

**Location:** `/workspaces/RTDS-Dataset-Generation-Framework/concept_drift/`

Concept drift detection capabilities to identify and analyze changes in network traffic patterns over time.

#### Implemented Drift Detectors:

| Detector | Description | Location |
| :--- | :--- | :--- |
| **DDM (Drift Detection Method)** | General drift detector for supervised learning scenarios | `supervised_concept_drift_detector.py` |
| **EDDM (Early Drift Detection Method)** | Early warning system that detects drift in early stages based on prediction error rates | `EDDM_detection.py` |
| **STEPD (Stochastic Exponential Gradient Descent)** | Window-based drift detector using exponential gradient descent with configurable window size | `stepd_detection.py` |

#### Supporting Modules:

* **Flow Conversion & Labeling** (`flow_conversion_labeling.py`):
  - Converts PCAP files to network flow data using NFStream
  - Cleans and scales flow data using MinMaxScaler
  - Supports binary and multi-class labeling based on IP addresses and attack types
  - Label flows based on attacker/victim IP pairs

* **Visualization & Analysis** (`distro_plot.py`):
  - Generates distribution plots for concept drift analysis
  - Visualizes performance metrics and drift points

* **Supervised Drift Detection** (`supervised_concept_drift_detector.py`):
  - Base class for all drift detectors
  - Calculates performance metrics: Precision, Recall, F1-Score, TNR
  - Marks drift detection points and warning thresholds
  - Supports model loading and training

---

### 3. Malicious Traffic Generation

**Location:** `/workspaces/RTDS-Dataset-Generation-Framework/scripts/`

Automated attack scripts that simulate realistic adversarial activities using Metasploit and Nmap.

#### Attack Scenarios:

| Attack Type | Script | Description |
| :--- | :--- | :--- |
| **Reconnaissance & Scanning** | `attack_scripts/general_scan.sh` | Comprehensive Nmap scanning including: intense scanning, UDP scanning, port enumeration, traceroute, ping scans |
| **SSH Brute-Force & C2** | `attack_scripts/exploit_ssh.sh` | SSH credential brute-forcing using Metasploit, backdoor creation, and Caldera C2 agent deployment |
| **HTTP/Web Exploitation** | `attack_scripts/exploit_http.sh` | Web-based exploit execution |
| **Java RMI Exploitation** | `attack_scripts/exploit_java-rmi.sh` | Java Remote Method Invocation vulnerabilities |
| **NetBIOS Exploitation** | `attack_scripts/exploit_netbios-ssn.sh` | Windows NetBIOS protocol exploitation |
| **NFS Exploitation** | `attack_scripts/exploit_nfs.sh` | Network File System vulnerabilities |
| **PostgreSQL Exploitation** | `attack_scripts/exploit_postgresql.sh` | Database credential attacks |
| **ProFTP Exploitation** | `attack_scripts/exploit_proftp.sh` | FTP server vulnerabilities (Metasploit resource script: `proftp_exploit_msfconsole.rc`) |
| **Samba Exploitation** | `attack_scripts/exploit_samba.sh` | SMB/Samba protocol exploitation |
| **SMTP Exploitation** | `attack_scripts/exploit_smtp.sh` | Email server attacks |
| **Telnet Exploitation** | `attack_scripts/exploit_telnet.sh` | Telnet protocol brute-force |
| **Tomcat Exploitation** | `attack_scripts/exploit_tomcat.sh` | Apache Tomcat server vulnerabilities |
| **VSFTP Exploitation** | `attack_scripts/exploit_vsftp.sh` | VSFTP server vulnerabilities (Metasploit resource script: `vsftp_exploit_msfconsole.rc`) |

#### Concept Drift Simulation Scripts:

* **`s1_gradCD.sh`** - Simulates gradual concept drift by progressively increasing download rates and bandwidth usage
  * Initiates multiple parallel wget downloads
  * Incrementally adds more high-bandwidth file transfers
  * Simulates realistic gradual changes in network behavior

#### Attack Orchestration:

* All attack scripts support logging to a centralized log server
* Integration with Metasploit Framework for automated exploitation
* Support for Caldera agent deployment for command & control
* Automated resource scripts (`.rc` files) for msfconsole

---

## Architecture Overview

The framework operates within a Controlled Cloud Network and is divided into three main component groups:

### 1. Controlled Cloud Network

A virtual network environment (e.g., OpenStack) hosting:

* **Controllers:** Orchestrator, Attacker Nodes (Kali Linux, Caldera Server).
* **Victim Nodes:** Windows and Linux VMs running benign bots.
* **Infrastructure:** Mail/FTP servers, Vulnerable Web Servers (Metasploitable).

### 2. Bots & Agents

| Agent Type | Purpose |
| :--- | :--- |
| **Normal Bots** | Execute sequential, typical user tasks. |
| **CD (Concept Drift) Bots** | Execute parallel, high-volume tasks to introduce statistical shifts. |
| **Malicious Agents** | Execute attack vectors defined in the scenarios. |

### 3. Evaluation Pipeline

* Traffic Collector (TCPdump)
* Flow Extraction (NFStream)
* Drift Detectors (DDM, EDDM, STEPD)
* ML-Based IDS Evaluation

---

## Lab Setup

To deploy this framework, you need a virtualized network environment.

### System Description

| Category | Requirement |
| :--- | :--- |
| **Virtualization** | OpenStack, Proxmox, or local VMs (VirtualBox/VMware). |
| **Operating Systems** | Ubuntu 20.04 LTS, Windows 10, Kali Linux. |

### Software & Tools

* Python 3.8+
* Caldera (Adversary Emulation)
* Metasploit Framework
* Selenium (Web Automation)
* NFStream (Flow Extraction)
* Menelaus (Drift Detection)
* TCPdump & Wireshark
* Nmap (Network Scanning)

---

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sudipbarua/RTDS-Dataset-Generation-Framework.git
    cd RTDS-Dataset-Generation-Framework
    ```
2.  **Setup the Environment:**
    * Configure your VMs according to the network topology described in the `docs/Network_Architecture.pdf`.
    * Deploy the `Orchestrator` scripts to the controller node.
    * Deploy `Client_Bot` scripts to the victim/normal user nodes.

---

##  Usage

### 1. Normal Traffic Generation

To generate benign network traffic:

```bash
cd user_profiles/oop/
python bot_executor.py
```

This will:
- Create normal bots and concept drift bots based on configuration
- Generate action lists for each bot (browsing, chatting, emailing, FTP)
- Schedule and execute bot processes
- Save bot objects as pickle files for remote deployment

### 2. Malicious Traffic Generation

Execute attack scenarios against target machines:

```bash
# Reconnaissance scanning
./scripts/attack_scripts/general_scan.sh <target_ip>

# SSH brute-force and C2 deployment
./scripts/attack_scripts/exploit_ssh.sh <target_ip>

# Simulate gradual concept drift with bandwidth increase
./scripts/s1_gradCD.sh
```

### 3. Concept Drift Detection

Analyze traffic for concept drift:

```bash
cd concept_drift/

# Detect drift using EDDM
python EDDM_detection.py --train_file <training_flows> --test_file <test_flows>

# Detect drift using STEPD
python stepd_detection.py --train_file <training_flows> --test_file <test_flows>

# Convert PCAP to flow format
python flow_conversion_labeling.py --pcap_file <pcap_file>
```

### 4. Configuration

Modify configuration files to customize bot behavior:

- **`user_profiles/oop/bot_config_parameters.yml`** - Bot capabilities and resources
- **`user_profiles/oop/log_file_path.yml`** - Logging configuration
- **`user_profiles/oop/bot_executor.py`** - Bot generator parameters (duration, counts, warmup period)




<img width="803" height="606" alt="image" src="https://github.com/user-attachments/assets/5ad8ca1e-990a-42f5-968b-3757db961b9d" />

<img width="781" height="615" alt="image" src="https://github.com/user-attachments/assets/99cb78c1-07b0-4c29-b942-a05a3758101d" />

<img width="802" height="335" alt="image" src="https://github.com/user-attachments/assets/cd24a0e0-09cb-469e-9fae-0a4833c4fd46" />

<img width="785" height="386" alt="image" src="https://github.com/user-attachments/assets/4892c0d5-6ab1-432a-a5dd-f1184b3393e9" />

<img width="793" height="393" alt="image" src="https://github.com/user-attachments/assets/1b29ccf2-987e-46f2-8fe5-f8355f98de81" />

