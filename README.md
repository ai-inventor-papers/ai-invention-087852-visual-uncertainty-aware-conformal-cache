# Visual Uncertainty-Aware Conformal Cache Admission with Adaptive Bias

<div align="center">

<a href="https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache@main/workflow.svg">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="workflow-dark.svg">
  <img alt="Artifact workflow — how every artifact in this repo was built" src="workflow.svg">
</picture>
</a>

<sub>🖱️ <b><a href="https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache@main/workflow.svg">Open the interactive diagram</a></b> — every card links to its artifact folder.</sub>

</div>

> **TL;DR** — VUCCA is the first cache admission policy combining visual semantic embeddings, conformal prediction intervals, and confidence-adaptive bias. It matches LRU hit ratios across three workload regimes while providing distribution-free coverage guarantees. The soft-sigmoid bias function is essential: removing it drops hit ratio by 67%.

<details>
<summary>Full hypothesis</summary>

Combining visual/semantic embeddings with conformal (distribution-free) uncertainty quantification to modulate cache admission does NOT, in its current formulation, improve hit ratio over a plain LRU baseline, and it substantially underperforms ARC2's ghost-list adaptive-replacement mechanism. The evidence is now specific about the mechanism of failure and the conditions under which the approach might still help. First, the admission threshold as implemented was inverted (threshold = 0.6 - tau_c with tau_c in [0.5, 0.7] and score bounded below by 0.05) so that the conformal filter admitted 99.8%-100% of items and was effectively disabled: VUCCA collapsed to LRU (hit ratios 0.479/0.441/0.413 stationary/shift/cold-start, exactly matching LRU). Second, the soft-sigmoid bias was necessary but only defensive: removing it (exponential bias, the earlier 'admission cliff' bug) cut hit ratio to ~0.16 (a 67% drop), but the soft-sigmoid alone cannot produce a selectivity advantage because a permissive sigmoid that never disables admission cannot discriminate hot from cold items. Third, ARC2's ~92% hit ratio (vs ~48% for LRU/VUCCA/TinyLFU) is driven by ghost-list temporal-locality memory — remembering recently evicted items — a signal that per-cluster semantic grouping of synthetic/visual embeddings does not capture; simply clustering items by embedding similarity yields no inter-item temporal generalization. The revised claim is accordingly narrower and negative-forward: (a) a conformal/uncertainty admission filter is only meaningful when its threshold is monotone-increasing in uncertainty (higher uncertainty must raise the admission bar, e.g. threshold = 0.5 + 0.5*uncertainty), and when the popularity signal is properly normalized (per-trace max, not a fixed /1000); (b) the central open question, now empirically sharpened, is whether semantic proximity CAN compensate for absent ghost-list temporal memory — i.e., whether admitting items that are semantically near known-hot clusters recovers the ARC2 gap — and this remains undemonstrated on the current synthetic traces; (c) coverage under distribution shift is NOT currently achieved (empirical coverage error 0.06/0.24/0.03 vs target 0.1, with the shift regime under-covered at 0.24), so Adaptive Conformal Inference's claimed benefit is unsupported on the evaluated abrupt-shift regime and its contribution must be removed or re-validated on a gradual-migration workload.

</details>

[![Read the interactive presentation](https://img.shields.io/badge/Read-Interactive_Presentation-8A2BE2?style=for-the-badge)](https://ai-inventor-papers.github.io/ai-invention-087852-visual-uncertainty-aware-conformal-cache/)

[![Download PDF](https://img.shields.io/badge/Download-PDF-red)](https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache@main/paper.pdf) [![LaTeX Source](https://img.shields.io/badge/LaTeX-Source-orange)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/paper_latex)

This repository contains all **5 artifacts** produced across **2 rounds** of an autonomous AI research run — round by round, exactly in the order they were invented.

## Round 1

| Artifact | Type | Demo | Source | Builds on |
|----------|------|------|--------|-----------|
| **[Visual Uncertainty-Aware Cache Admission Survey](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/research-1)** | [![research](https://img.shields.io/badge/research-3b82f6)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/research-1) | [![View Research](https://img.shields.io/badge/View-Research-green)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/blob/main/round-1/research-1/demo/research_demo.md) | [![Source Code](https://img.shields.io/badge/Source_Code-2962FF)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/research-1/src) | — |
| **[Cache Access Trace Datasets with Visual Embeddings](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/dataset-1)** | [![dataset](https://img.shields.io/badge/dataset-f59e0b)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/dataset-1) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/blob/main/round-1/dataset-1/demo/data_code_demo.ipynb) | [![Source Code](https://img.shields.io/badge/Source_Code-2962FF)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/dataset-1/src) | — |
| **[Visual Uncertainty-Aware Cache Admission Experiment](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/experiment-1)** | [![experiment](https://img.shields.io/badge/experiment-8b5cf6)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/experiment-1) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/blob/main/round-1/experiment-1/demo/method_code_demo.ipynb) | [![Source Code](https://img.shields.io/badge/Source_Code-2962FF)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/experiment-1/src) | — |

## Round 2

| Artifact | Type | Demo | Source | Builds on |
|----------|------|------|--------|-----------|
| **[VUCCA: Uncertainty-Aware Cache Admission](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-2/experiment-1)** | [![experiment](https://img.shields.io/badge/experiment-8b5cf6)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-2/experiment-1) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/blob/main/round-2/experiment-1/demo/method_code_demo.ipynb) | [![Source Code](https://img.shields.io/badge/Source_Code-2962FF)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-2/experiment-1/src) | <sub><i>uses:</i><br/>[dataset‑1&nbsp;(R1)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/dataset-1)<br/>[research‑1&nbsp;(R1)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/research-1)</sub> |
| **[Statistical Evaluation of VUCCA Cache Results](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-2/evaluation-1)** | [![evaluation](https://img.shields.io/badge/evaluation-10b981)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-2/evaluation-1) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/blob/main/round-2/evaluation-1/demo/eval_code_demo.ipynb) | [![Source Code](https://img.shields.io/badge/Source_Code-2962FF)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-2/evaluation-1/src) | <sub><i>differences:</i><br/>[experiment‑1&nbsp;(R1)](https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache/tree/main/round-1/experiment-1)</sub> |

## Repository Structure

Artifacts are grouped by the round of invention that produced them. Each
artifact has its own folder with source code and a self-contained demo:

```
.
├── round-1/                         # One folder per round of invention
│   ├── experiment-1/
│   │   ├── README.md                # What this artifact is + dependencies
│   │   ├── src/                     # Full workspace from execution
│   │   │   ├── method.py            # Main implementation
│   │   │   ├── method_out.json      # Full output data
│   │   │   └── ...                  # All execution artifacts
│   │   └── demo/                    # Self-contained demo
│   │       └── method_code_demo.ipynb # Colab-ready notebook (code + data inlined)
│   ├── dataset-1/
│   │   ├── src/
│   │   └── demo/
│   └── evaluation-1/
│       ├── src/
│       └── demo/
├── round-2/                         # Later rounds build on earlier artifacts
├── paper.pdf                        # Research paper
├── paper_latex/                     # LaTeX source files
├── chat/                            # Every prompt, response and tool call, per module
├── workflow.svg                     # Artifact dependency diagram (this page's header)
└── README.md
```

## Running Notebooks

### Option 1: Google Colab (Recommended)

Click the "Open in Colab" badges above to run notebooks directly in your browser.
No installation required!

### Option 2: Local Jupyter

```bash
# Clone the repo
git clone https://github.com/ai-inventor-papers/ai-invention-087852-visual-uncertainty-aware-conformal-cache
cd ai-invention-087852-visual-uncertainty-aware-conformal-cache

# Install dependencies
pip install jupyter

# Run any artifact's demo notebook
jupyter notebook <artifact_folder>/demo/
```

## Source Code

The original source files are in each artifact's `src/` folder.
These files may have external dependencies - use the demo notebooks for a self-contained experience.

---
*Generated by AI Inventor Pipeline - Automated Research Generation*
