<div align="center">

# SkillFoundry

### Building Self-Evolving Agent Skill Libraries from Heterogeneous Scientific Resources

**Shuaike Shen\*, Wenduo Cheng\*, Mingqian Ma, Alistair Turcan, Martin Jinye Zhang, Jian Ma†**

Ray & Stephanie Lane Computational Biology, School of Computer Science, Carnegie Mellon University

[\*Equal contribution · †Correspondence: jianma@cs.cmu.edu]

<p>
  <a href="https://ma-compbio-lab.github.io/SkillFoundry/"><img src="https://img.shields.io/badge/Project-Page-blue?style=for-the-badge" alt="Project Page"></a>&nbsp;
  <a href="https://arxiv.org/abs/2604.03964"><img src="https://img.shields.io/badge/arXiv-2604.03964-b31b1b?style=for-the-badge" alt="arXiv"></a>&nbsp;
  <a href="assets/paper/paper.pdf"><img src="https://img.shields.io/badge/Paper-PDF-red?style=for-the-badge" alt="Paper"></a>&nbsp;
  <a href="https://github.com/ma-compbio-lab/SkillFoundry"><img src="https://img.shields.io/badge/GitHub-Code-black?style=for-the-badge&logo=github" alt="GitHub"></a>
</p>

</div>

---

## Overview

Modern scientific ecosystems are rich in procedural knowledge — repositories, APIs, scripts, notebooks, documentation, databases, and papers — yet much of this knowledge remains fragmented and difficult for agents to operationalize. **SkillFoundry** bridges this gap with a self-evolving framework that converts heterogeneous scientific resources into validated, reusable agent skills.

<div align="center">
  <img src="assets/paper/concept.png" width="90%" alt="SkillFoundry framework overview">
  <br>
  <sub><b>Figure 1.</b> SkillFoundry framework overview: from domain knowledge tree to validated skill library.</sub>
</div>

### Key Results

| | |
|:---|:---|
| **267+ skills** | mined across **28** scientific domains and **254** subdomains |
| **71.1% novelty** | vs. existing skill libraries (SkillHub, SkillSMP) |
| **5/6 datasets improved** | on [MoSciBench](https://github.com/MoSciBench/MoSciBench) benchmark |
| **Genomics boost** | substantial gains on two challenging genomics tasks |

---

## How It Works

SkillFoundry uses a **domain knowledge tree** as both a search prior and the evolving structure being updated, turning open-ended skill collection into a closed-loop acquisition process:

| Step | Stage | Description |
|:---:|:---|:---|
| 1 | **Tree Construction** | Build a rooted tree where internal nodes are domains/subdomains and leaves are actionable skill targets |
| 2 | **Resource Mining** | Select focus branches and retrieve relevant resources (repos, APIs, papers, notebooks, databases) |
| 3 | **Skill Compilation** | Extract operational contracts and compile into reusable skill packages with metadata, dependencies, and tests |
| 4 | **Multi-Level Validation** | Apply execution testing, system testing, and synthetic-data testing |
| 5 | **Tree Expansion** | Insert validated skills as new leaves, expanding domain coverage |
| 6 | **Refinement & Loop** | Revise, merge, or prune failing/redundant skills; repeat from step 2 |

---

## Repository Structure

```
SkillFoundry/
├── sciskill_framework/       # Core framework source code
├── scripts/                  # Utility scripts
├── tests/                    # Test suites (smoke, integration, regression)
├── skills.json               # Central skill registry (267+ skills)
├── skill_details.json        # Detailed skill documentation
├── tree.json                 # Domain taxonomy tree
├── graph.json                # Knowledge graph (642 nodes)
├── framework_runs.json       # Validation run statistics
├── index.html                # Project page entry point
├── app.js                    # Project page application logic
├── styles.css                # Project page styles
├── panels/                   # Project page dynamic panels
│   ├── overview.html
│   ├── catalog.html
│   ├── taxonomy.html
│   └── paper.html
├── taxonomy-radial/          # Radial taxonomy visualization data
└── assets/paper/             # Paper figures and PDF
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Required packages (see framework dependencies)

### Installation

```bash
git clone https://github.com/ma-compbio-lab/SkillFoundry.git
cd SkillFoundry
```

### Running the Project Page Locally

The project page is a static site — no build step required:

```bash
python3 -m http.server 8000
# Then open http://localhost:8000
```

---

## Citation

Citation information will be available once the paper is published. Check back later.

---

## License

This project is developed at [Ma Lab](https://www.cs.cmu.edu/~jianma/), Carnegie Mellon University.
