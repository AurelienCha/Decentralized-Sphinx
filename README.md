# DSphinx: Decentralized Sphinx Path Selection

DSphinx is a decentralized path-selection protocol for privacy-preserving networks based on the Sphinx packet format. Instead of allowing the client to choose the complete route, DSphinx distributes route sampling across multiple semi-trusted third parties (STTPs).

The design is described in **“DSphinx: A Decentralized Path Selection for Decentralized Networks”** by Aurélien Chassagne, Manuel Mota Leal Dias, Iness Ben Guirat, Jan Tobias Mühlberg, and Jean-Michel Dricot.
[![Paper](https://img.shields.io/badge/paper-DSphinx-blue)](./main.pdf)

> **Research prototype:** this repository implements a research protocol and should not be treated as production-ready anonymous networking software. The security properties described in the paper depend on the stated cryptographic and threshold assumptions. The Python implementation uses the `mclbn256` library for BN254 elliptic-curve operations.

## 1. Motivation

Sphinx provides compact, fixed-size packet headers with per-hop confidentiality, integrity protection, replay resistance, and strong unlinkability. However, the traditional Sphinx construction is performed by the client, so a malicious client can deliberately construct routes that deviate from the intended routing algorithm.

DSphinx moves route sampling away from the client.

A client supplies a nonce, and multiple STTPs independently derive the same route from that nonce. Each STTP returns secret-shared routing information. The client reconstructs the route only after obtaining responses from a threshold number `d` of STTPs.

This limits the client's ability to arbitrarily choose routes while retaining the Sphinx-style packet-processing model.

## 2. Repository structure

This repository contains:

- The paper **“DSphinx: A Decentralized Path Selection for Decentralized Networks”**, submitted to the **CBT Workshop 2026 of ESORICS**.
- A **Python implementation** of DSphinx, together with its benchmark, developed by Aurélien Chassagne as a PhD student.
- A **Rust implementation**, provided as a [GitLab submodule](https://gitlab.com/manuelmotadias/master_thesis.git), together with its benchmark for validating the results, developed by Manuel Mota Leal Dias as a master's student.
- **Benchmarking** and comparison tools for evaluating the different implementations.
- The **original** [**Sphinx implementation**](https://github.com/UCL-InfoSec/sphinx.git), included as a Git submodule and used as a baseline for comparison.

```text
.
├── README.md
├── requirements.txt
├── .gitmodules
├── report/
│
└── src/
    ├── Python_Version/
    │   ├── Client/
    │   │   ├── client.py
    │   │   ├── ECC.py
    │   │   ├── crypto.py
    │   │   ├── header.py
    │   │   ├── network.py
    │   │   └── main.py
    │   │
    │   ├── Mixnode/
    │   │   ├── mixnode.py
    │   │   ├── ECC.py
    │   │   ├── crypto.py
    │   │   ├── header.py
    │   │   ├── network.py
    │   │   └── main.py
    │   │
    │   ├── STTP/
    │   │   ├── node.py
    │   │   ├── ECC.py
    │   │   └── network.py
    │   │
    │   ├── config.py
    │   ├── run.sh
    │   ├── bench.sh
    │   └── .benchmark/
    │
    └── Rust_Version/
```

The repository uses Git submodules for the Rust implementation and the original Sphinx benchmark code. Clone the repository recursively.

## 3. Installation

### Prerequisites

The repository currently targets **Python 3.13.x**.

You also need:

- Git;
- Python 3.13;
- `pip`;
- Bash for the provided shell scripts;

### Clone the repository

```bash
git clone --recurse-submodules https://github.com/AurelienCha/Decentralized-Sphinx.git
cd Decentralized-Sphinx
```

### Create a virtual environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### Install Python dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Run the Python implementation

The easiest way to run the complete local prototype is the supplied `run.sh`.

From the Python implementation directory:
```bash
cd src/Python_Version
chmod +x run.sh
./run.sh
```

The default configuration in the script is:

| Parameter | Default |
|---|---:|
| Path length (`m`) | 5 |
| Threshold (`d`) | 5 |
| STTPs | 20 |
| Mixnodes | 50 |
| Clients | 1 |
| UDP port | 5000 |

The script performs the following operations:

1. removes stale processes and temporary state;
2. creates log directories;
3. generates `.config.json`;
4. starts the STTP processes;
5. waits for STTP initialization;
6. starts the mixnodes;
7. waits for mixnode setup;
8. starts the client;
9. constructs and sends a DSphinx packet through the local network.

The client currently sends the test packet to itself. This is intentional in the prototype and is marked as a TODO in the implementation; it should not be interpreted as a full multi-host deployment.

### Custom parameters

The script accepts:

```bash
./run.sh -p PATH_LENGTH -t THRESHOLD -m MIXNODES -s STTPS -c CLIENTS -v VERBOSE
```

For example:

```bash
./run.sh -p 3 -t 3 -m 10 -s 5 -c 1 -v 1
```

Keep the threshold consistent with the deployment: `d` must not exceed the number of STTPs.
