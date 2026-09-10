# gen_full_paper — report_results

> Phase: `gen_paper_repo` · `gen_full_paper`
> Run: `run_XUVIPW24BQbP` — Visual Uncertainty-Aware Conformal Cache Admission with Adaptive Bias
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_full_paper` (sdk_openhands_agent)

### [1] SYSTEM-USER prompt · 2026-09-10 01:21:51 UTC

````
<task>
Create a publication-ready top-conference LaTeX paper with BibTeX from <paper_text> and <available_figures>, compile to PDF.
</task>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<paper_text>
title: Visual Uncertainty-Aware Conformal Cache Admission with Adaptive Bias
abstract: >-
  Cache admission policies decide which items enter a limited-capacity cache. Existing policies rely on recency, frequency,
  or learned signals, yet they provide no uncertainty quantification: when popularity shifts or new content arrives, they
  admit items with the same confidence as they do stable ones. We propose Visual Uncertainty-Aware Conformal Cache Admission
  (VUCCA), the first admission mechanism to combine semantic embeddings, conformal prediction intervals, and confidence-adaptive
  bias. VUCCA clusters items by visual embedding, computes conformal prediction intervals for per-cluster miss rates, and
  adjusts admission thresholds via a soft-sigmoid function: high-confidence clusters admit freely, uncertain clusters are
  filtered selectively. We evaluate VUCCA against LRU, TinyLFU, and ARC2 on three synthetic regimes derived from CDN trace
  statistics. VUCCA matches LRU hit ratios across all regimes while providing distribution-free coverage guarantees that baselines
  lack. An ablation confirms the soft-sigmoid bias is essential: removing it drops hit ratio by 67%. The conformal framework
  enables uncertainty-aware admission where baselines offer none.
paper_text: |-
  # Visual Uncertainty-Aware Conformal Cache Admission with Adaptive Bias

  ## Abstract

  Cache admission policies decide which items enter a limited-capacity cache. Existing policies rely on recency, frequency, or learned signals, yet they provide no uncertainty quantification: when popularity shifts or new content arrives, they admit items with the same confidence as they do stable ones. We propose Visual Uncertainty-Aware Conformal Cache Admission (VUCCA), the first admission mechanism to combine semantic embeddings, conformal prediction intervals, and confidence-adaptive bias. VUCCA clusters items by visual embedding, computes conformal prediction intervals for per-cluster miss rates, and adjusts admission thresholds via a soft-sigmoid function: high-confidence clusters admit freely, uncertain clusters are filtered selectively. We evaluate VUCCA against LRU, TinyLFU, and ARC2 on three synthetic regimes derived from CDN trace statistics. VUCCA matches LRU hit ratios across all regimes (0.479, 0.441, 0.413) while providing distribution-free coverage guarantees. An ablation confirms the soft-sigmoid bias is essential: removing it drops hit ratio by 67%.

  ## 1 Introduction

  ### 1.1 Problem

  Software caches are ubiquitous: from Memcached and CDN edge caches to LLM KV caches and database buffer pools. The admission decision, whether to insert a newly requested item into a full cache, directly determines hit ratio, throughput, and latency. A poor admission policy admits one-hit wonders that pollute the cache, or rejects items that would become hot, wasting capacity and increasing backend load.

  ### 1.2 Importance

  Modern workloads exhibit three properties that strain existing admission policies. First, popularity is highly skewed: a few items receive most requests while the majority are one-hit wonders. Second, popularity shifts abruptly: viral content, news events, or model updates cause request mass to migrate between semantic clusters. Third, cold-start streams continuously introduce previously unseen items with no access history. These properties appear in CDN object traces (Twitter, Wikimedia, Tencent Photo), LLM serving (LoRA adapter popularity), and database workloads.

  ### 1.3 Challenges

  Naive frequency-based admission (TinyLFU) uses a fixed window to estimate popularity. When popularity shifts, the window contains stale statistics, causing both false admits and false rejects. Recency-based policies (LRU, ARC) adapt to shifts but lack semantic understanding: they cannot generalize from one item to semantically similar items. Learning-augmented policies (DEAP Cache, CACHEUS) model the joint distribution of features and future accesses but provide no distribution-free uncertainty guarantees: they can be overconfident on out-of-distribution items.

  ### 1.4 Prior Work Gap

  A survey of 12 state-of-the-art admission policies (TinyLFU, S3-FIFO, Segcache, CacheSack, DEAP Cache, Guard, AdCache, Chameleon, Bandit Learning-to-Cache, Learning-Augmented Caching, LeCaR, ARC) confirms that zero apply distribution-free uncertainty quantification to admission decisions [1, 2, 3, 4, 5, 6, 12]. DEAP Cache uses Kernel Density Estimation for non-stationary data modeling but provides no coverage guarantees [4]. Guard provides robustness bounds via algorithmic analysis, not statistical uncertainty quantification [5]. Visual or semantic embeddings (CLIP, ViT) are used for similarity search in caching but never combined with uncertainty-aware admission [10]. This gap limits performance in content-rich systems where hot and cold clusters are dynamically rich and semantically structured.

  ### 1.5 Our Approach and Summary of Results

  We propose Visual Uncertainty-Aware Conformal Cache Admission (VUCCA), the first cache admission mechanism combining visual semantic embeddings, conformal prediction intervals, and confidence-adaptive admission bias. We evaluate VUCCA against LRU, TinyLFU, and ARC2 on three controlled regimes. VUCCA matches LRU hit ratios across all regimes while providing distribution-free coverage guarantees that baselines lack. An ablation confirms the soft-sigmoid bias function is essential: replacing it with the exponential bias from our initial design drops hit ratio by 67%, reproducing the "admission cliff" failure mode.

  **Summary of Contributions**

  - **Novel mechanism**: First cache admission policy combining visual semantic embeddings, conformal prediction intervals, and confidence-adaptive bias with a soft-sigmoid function.
  - **Adaptive Conformal Inference**: Implementation of ACI with exponential weighting for non-stationary workloads, addressing exchangeability violations under popularity shifts [8].
  - **Comprehensive survey**: Verification that zero of 12 modern baselines use conformal prediction or visual signals for admission.
  - **Synthetic benchmark**: Three regimes (stationary, shift, cold-start) with 512-d embeddings and temporal splits for controlled evaluation.
  - **Ablation study**: Four ablations isolating the contribution of soft-sigmoid bias, ACI, cluster granularity, and entropy-based uncertainty.

  [FIGURE:fig1]

  ## 2 Related Work

  ### 2.1 Cache Admission and Eviction Policies

  **Frequency-based admission.** TinyLFU [1] maintains a Count-Min Sketch of recent access frequencies and admits a new item only if its estimated frequency exceeds the victim's. S3-FIFO [2] uses a small probationary FIFO queue to filter one-hit wonders, achieving lower miss ratios than LRU-based policies across 6594 production traces. Both use fixed thresholds without uncertainty quantification.

  **Recency and adaptive replacement.** ARC [3] maintains four LRU queues (recent, frequent, and their ghosts) and adapts the partition based on ghost hits. LIRS uses reuse distance. These adapt to workload shifts but lack semantic generalization.

  **Learning-augmented caching.** DEAP Cache [4] jointly learns eviction, admission, and prefetching with a deep network and Kernel Density Estimation for non-stationarity. CACHEUS selects among expert policies via online learning. Guard [5] robustifies learning-augmented policies to $2H_{k-1}+2$ consistency with $O(1)$ overhead. None provide distribution-free prediction intervals.

  **LLM-specific caching.** Chameleon [6] caches LoRA adapters for multi-adapter LLM inference, reducing P99 latency by 80.7%. GPTCache and RAGCache use embedding similarity for semantic cache hits. These are domain-specific and do not address general admission with uncertainty.

  ### 2.2 Conformal Prediction

  Conformal prediction [7] generates prediction sets with guaranteed marginal coverage $1-\alpha$ under exchangeability, without distributional assumptions. Split conformal reserves a calibration set to compute a quantile of nonconformity scores; the resulting intervals are valid for any model. Gibbs and Candès [8] extend conformal prediction to handle distribution shift via Adaptive Conformal Inference (ACI), which updates quantiles with exponential weighting to track non-stationary environments. Their follow-up [9] handles arbitrary distribution shifts in online prediction. To our knowledge, conformal prediction has not been applied to cache admission.

  ### 2.3 Visual and Semantic Embeddings in Caching

  ViT and CLIP embeddings enable semantic similarity search [10]. IGTCache uses ViT for image retrieval caching (+55.6% hit ratio). Document embedding caches implement metric indices for nearest-neighbor queries. None incorporate embedding-derived uncertainty into admission.

  ### 2.4 Throughput-Hit Ratio Trade-offs

  Qiu et al. [11] show that increasing hit ratio can hurt throughput under certain queueing conditions, challenging the assumption that higher hit ratio always improves performance. This motivates our dual evaluation of both hit ratio and throughput.

  ## 3 Method

  ### 3.1 Overview

  VUCCA operates in three stages (Figure 1): (1) **Embedding and Clustering**: items are mapped to 512-d visual embeddings and clustered into K semantic groups; (2) **Conformal Uncertainty Quantification**: per-cluster miss rates are estimated over a calibration window, and conformal prediction produces intervals with coverage $1-\alpha$; (3) **Confidence-Adaptive Admission**: the interval width determines an uncertainty score, which scales the admission threshold via a soft-sigmoid bias function.

  ### 3.2 Visual Semantic Embeddings

  Each item $i$ has an associated image or visual representation. We extract a 512-dimensional embedding $e_i \in \mathbb{R}^{512}$ using a pretrained ViT-B/32 [10]. In our synthetic benchmark, embeddings are generated deterministically from item IDs using structured sinusoidal functions. Items are clustered via K-means ($K=64$) into semantic clusters $C_1,\dots,C_K$. Clusters smaller than 5 items are merged into the nearest larger cluster.

  ### 3.3 Conformal Prediction for Miss Rates

  Let $M_c(t)$ be the empirical miss rate of cluster $c$ at time $t$. We reserve the first 20% of the trace as a calibration set. For each cluster $c$, we compute nonconformity scores $s_i = |M_c(t_i) - M_c(t_i-1)|$ for calibration points $i$.

  **Split conformal** (stationary regimes): The conformal quantile $\hat{q}_c$ is the $\lceil(n+1)(1-\alpha)\rceil/n$ empirical quantile of $\{s_i\}$. The prediction interval for the next miss rate is $[M_c(t) - \hat{q}_c, M_c(t) + \hat{q}_c] \cap [0,1]$.

  **Adaptive Conformal Inference** (shift regime): Following Gibbs and Candès [8], we weight calibration residuals by exponential decay: $w_i = \exp(-\lambda(t_{\text{current}} - t_i))$ with $\lambda = 0.01$. The weighted quantile tracks distribution shifts by upweighting recent residuals.

  The interval half-width $h_c = \hat{q}_c$ measures uncertainty: narrow intervals indicate stable miss rates (high confidence); wide intervals indicate volatility or insufficient data (low confidence).

  ### 3.4 Confidence-Adaptive Admission Bias

  Define normalized uncertainty $u_c = \min(h_c, 1.0) \in [0, 1]$. The adaptive bias factor uses a soft-sigmoid function:

  $$\tau_c = \tau_{\text{base}} + \beta \cdot \sigma(\gamma \cdot (1 - u_c))$$

  where $\sigma(x) = 1/(1 + e^{-x})$ is the sigmoid, $\tau_{\text{base}} = 0.3$, $\beta = 0.4$, and $\gamma = 5.0$. The threshold $\tau_c \in [\tau_{\text{base}}, \tau_{\text{base}} + \beta] = [0.3, 0.7]$.

  When $u_c \approx 0$ (high confidence), $\sigma(\gamma) \approx 1$ and $\tau_c \approx 0.7$, making admission permissive. When $u_c \approx 1$ (low confidence), $\sigma(0) = 0.5$ and $\tau_c \approx 0.5$, making admission more selective but not disabled. This contrasts with our initial design, which used $\tau_c = \tau_{\text{base}}(1 + u_c)$, pushing thresholds to 1.0 and disabling admission entirely.

  An item from cluster $c$ with normalized popularity $p_i$ is admitted if:
  $$p_i \cdot \tau_c + (1 - p_i) \cdot 0.05 > 0.6 - \tau_c$$

  The cache uses an LRU backbone with capacity 50. Admission is checked on each miss; admitted items are inserted at the MRU position.

  ### 3.5 Baselines

  - **LRU**: Standard least-recently-used eviction, admit all misses.
  - **TinyLFU**: Frequency sketch with 4096-slot Count-Min Sketch; admit if freq(new) > 0 or cache not full.
  - **ARC2**: Adaptive Replacement Cache with T1, T2, B1, B2 lists and ghost tracking.

  All baselines use the same cache capacity (50) and trace length (~24000 requests per regime).

  ## 4 Experimental Setup

  ### 4.1 Datasets

  We generate three regimes from a base Zipf($\alpha=1.0$) trace of 5000 items and 2000 requests:

  1. **Stationary Hot Clusters**: Stable Zipf popularity; approximately 10% of items (500) receive approximately 90% of requests. 826 unique items.
  2. **Sudden Popularity Shift**: First half follows Zipf over items 1–2500; second half shifts to items 2501–5000. 826 unique items.
  3. **Cold Start**: 80% of requests target 500 popular items; 20% uniformly sample from all 5000 items. 926 unique items.

  Each item has a 512-d embedding, cluster ID (64 clusters), and popularity count. Traces are expanded by repeating each item $3 \times$ its popularity count, yielding ~30000 requests per regime. The first 20% serves as calibration; the remainder is test.

  ### 4.2 Metrics

  - **Hit ratio**: Hits / total requests.
  - **Throughput**: Requests / total latency (hit=1, miss=100 time units).
  - **Coverage error**: $|0.9 - \text{empirical\_coverage}|$ for conformal intervals ($\alpha=0.1$).

  ### 4.3 Configuration

  Cache capacity: 50. Calibration fraction: 0.2. $\alpha=0.1$. $\gamma=5.0$. $K=64$ clusters. $\lambda_{\text{ACI}}=0.01$. 8 methods per regime (3 baselines + 5 VUCCA variants) = 24 total runs.

  ## 5 Results

  ### 5.1 Main Comparison

  [FIGURE:fig2]

  Table 1 summarizes hit ratios across regimes. VUCCA matches LRU across all three regimes.

  | Regime | LRU | TinyLFU | ARC2 | VUCCA |
  |--------|-----|---------|------|-------|
  | Stationary | 0.479 | 0.464 | 0.921 | **0.479** |
  | Popularity-Shift | 0.441 | 0.409 | 0.925 | **0.441** |
  | Cold-Start | 0.413 | 0.385 | 0.908 | **0.413** |

  ARC2 dominates across all regimes with ~92% hit ratio, consistent with its ghost list advantage: it remembers recently evicted items and prioritizes their re-admission. VUCCA matches LRU, demonstrating that the conformal admission filter does not degrade performance relative to the simplest baseline.

  Throughput follows the same pattern. In stationary: VUCCA throughput 5.69 vs 5.69 for LRU. In shift: VUCCA 6.03 vs LRU 6.03. In cold-start: VUCCA 6.29 vs LRU 6.28.

  [FIGURE:fig3]

  ### 5.2 Ablation Study

  We run four ablations to isolate the contribution of each design component.

  **Removing soft-sigmoid (exponential bias).** Replacing the soft-sigmoid with the exponential bias $b_c = \exp(-\gamma u_c)$ from our initial design drops hit ratio by 67% across all regimes: 0.160 (stationary), 0.146 (shift), 0.157 (cold-start). The exponential function creates an "admission cliff" where moderate uncertainty effectively disables admission. VUCCA_no_sigmoid admits only 14–15% of items (1823/12517 stationary, 2182/13432 shift, 4019/14105 cold-start), compared to 99.8% for VUCCA. This confirms the soft-sigmoid is essential for maintaining a gradient of admission.

  **Removing ACI (split conformal everywhere).** VUCCA_no_ACI produces identical results to VUCCA across all regimes (0.479, 0.441, 0.413). The synthetic shift regime's structure (reversing the second half of the trace) does not create enough distribution drift for ACI to matter. On real CDN traces with gradual popularity migration, ACI would be expected to improve coverage.

  **Reducing cluster count (K=10 vs K=64).** VUCCA_small_K matches VUCCA in hit ratio (0.478 vs 0.479 stationary) but shows higher coverage error (0.30 vs 0.06 stationary). Coarser clustering yields wider conformal intervals, reducing the resolution of uncertainty estimates. The hit ratio is unaffected because the soft-sigmoid prevents the admission cliff even with coarser clusters.

  **Entropy-based uncertainty.** VUCCA_entropy uses the entropy of the request distribution across clusters instead of conformal interval width. It achieves 0.472 (stationary), 0.427 (shift), 0.397 (cold-start), slightly below VUCCA. Entropy measures diversity, not prediction uncertainty, and provides no coverage guarantees.

  [FIGURE:fig4]

  ### 5.3 Coverage Calibration

  The conformal intervals target 90% coverage ($\alpha=0.1$). Empirical coverage across regimes: 0.94 (stationary), 0.76 (shift), 0.97 (cold-start). The shift regime shows anti-conservative coverage (0.76), consistent with exchangeability violations under popularity shifts. The ACI weighting mitigates but does not fully correct this, suggesting that the synthetic shift's abrupt nature exceeds what exponential weighting can track.

  ### 5.4 Admission Behavior

  VUCCA's bias range is [0.50, 0.70] across all regimes, with the sigmoid ensuring no cluster falls below $\tau_{\text{base}} = 0.3$. In the stationary regime, VUCCA admits 12497/12517 items (99.8%), rejecting only 20. In the shift and cold-start regimes, it admits all items (0 rejections). This contrasts sharply with our initial design, which rejected 68% of items due to the admission cliff.

  ## 6 Discussion

  ### 6.1 Why VUCCA Matches LRU

  VUCCA's hit ratio equals LRU because the soft-sigmoid bias function, combined with the synthetic workload's structure, results in nearly permissive admission. The conformal intervals are narrow enough that the bias stays in the permissive range. This is both a success (no performance degradation) and a limitation: the conformal filter is not yet selective enough to demonstrate an advantage over LRU.

  The gap to ARC2 (~92% vs ~48%) reflects a fundamental difference: ARC2's ghost lists provide a form of semantic memory (remembering recently evicted items) that our embedding-based approach does not yet exploit. Our clusters group items by embedding similarity, but we do not use inter-cluster relationships to inform admission.

  ### 6.2 What the Ablation Tells Us

  The no-sigmoid ablation is the most informative result. It reproduces the failure mode of our first iteration: the exponential bias function creates a cliff where moderate uncertainty disables admission. The soft-sigmoid eliminates this cliff by ensuring that even high-uncertainty clusters maintain a minimum admission rate. This is the key design insight: uncertainty should modulate admission, not disable it.

  The no-ACI result suggests that our synthetic shift regime is too abrupt for ACI to matter. Real workloads with gradual popularity migration would benefit more from ACI's exponential weighting.

  ### 6.3 Limitations

  - **Synthetic embeddings**: Our dataset uses deterministic sinusoidal embeddings, not true ViT features. Real visual embeddings may have stronger or weaker semantic structure.
  - **Exchangeability violations**: The shift regime's abrupt transition violates the i.i.d. assumption. ACI mitigates but does not eliminate the coverage gap.
  - **Cache capacity**: We use capacity 50, smaller than production caches. The admission filter's impact may differ at scale.
  - **No end-to-end latency modeling**: Embedding inference overhead (ViT-B/32 $\approx$ 10–50ms on CPU) is not modeled. In latency-sensitive caches, this overhead must be weighed against hit ratio gains.

  ### 6.4 Future Work

  - Evaluate on real CDN traces (S3-FIFO collection: 6594 traces, 856B requests) with true CLIP embeddings.
  - Use inter-cluster similarity to inform admission: if cluster A is semantically close to a hot cluster B, admit items from A more freely.
  - Learn the bias function parameters ($\tau_{\text{base}}, \beta, \gamma$) via bandit optimization over the admission threshold space.
  - Explore conformal admission for LLM KV cache and LoRA adapter caching, where semantic structure is strong and the cost of miss is high.

  ## 7 Conclusion

  VUCCA demonstrates that combining conformal prediction with semantic embeddings for cache admission is a viable research direction. The method matches LRU hit ratios across three workload regimes while providing distribution-free coverage guarantees that baselines lack. The soft-sigmoid bias function is essential: removing it reproduces the "admission cliff" failure mode of our initial design. The gap to ARC2 reflects the advantage of ghost-list-based semantic memory, which our embedding-based approach does not yet exploit. Future work on real CDN traces with true visual embeddings will determine whether the conformal framework can deliver performance gains beyond matching baselines.

  ## References

  [1] G. Einziger, R. Friedman, and B. Manes, "TinyLFU: A Highly Efficient Cache Admission Policy," *ACM Trans. Storage*, 2017.

  [2] J. Yang et al., "FIFO queues are all you need for cache eviction," *SOSP*, 2023.

  [3] N. Megiddo and D. S. Modha, "ARC: A Self-Tuning, Low Overhead Replacement Cache," *FAST*, 2003.

  [4] A. Mangal et al., "DEAP Cache: Deep Eviction Admission and Prefetching for Cache," *arXiv:2009.09206*, 2020.

  [5] P. Chen et al., "Robustifying Learning-Augmented Caching Efficiently without Compromising 1-Consistency," *NeurIPS*, 2025.

  [6] N. Iliakopoulou et al., "Chameleon: Adaptive Caching and Scheduling for Many-Adapter LLM Inference Environments," *MICRO*, 2024.

  [7] A. N. Angelopoulos and S. Bates, "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification," *arXiv:2107.07511*, 2021.

  [8] I. Gibbs and E. Candès, "Adaptive Conformal Inference Under Distribution Shift," *NeurIPS*, 2021.

  [9] I. Gibbs and E. Candès, "Conformal Inference for Online Prediction with Arbitrary Distribution Shifts," *JMLR*, 2022.

  [10] A. Dosovitskiy et al., "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale," *ICLR*, 2021.

  [11] Z. Qiu, J. Yang, and M. Harchol-Balter, "Can Increasing the Hit Ratio Hurt Cache Throughput?" *arXiv:2404.16219*, 2024.

  [12] A. Bura et al., "Learning to Cache and Caching to Learn: Regret Analysis of Caching Algorithms," *IEEE/ACM Trans. Netw.*, 2020.
summary: >-
  VUCCA is the first cache admission policy combining visual semantic embeddings, conformal prediction intervals, and confidence-adaptive
  bias. It matches LRU hit ratios across three workload regimes while providing distribution-free coverage guarantees. The
  soft-sigmoid bias function is essential: removing it drops hit ratio by 67%.
</paper_text>

<available_figures>
--- Item 1 ---
id: fig1
figure_type: concept
title: VUCCA Pipeline Architecture
caption: >-
  VUCCA operates in three stages: (1) items are embedded and clustered into semantic groups, (2) conformal prediction intervals
  quantify per-cluster miss-rate uncertainty, and (3) a soft-sigmoid bias function adjusts admission thresholds. ACI with
  exponential weighting handles non-stationary workloads.
image_gen_detailed_description: >-
  Horizontal flow diagram, left to right, three main stages. Stage 1 (blue box): 'Visual Embedding + Clustering' with sub-labels
  '512-d embeddings', 'KMeans (K=64)', '64 semantic clusters'. Arrow labeled 'cluster assignments' points to Stage 2. Stage
  2 (green box): 'Conformal Uncertainty Quantification' with sub-labels 'Split Conformal (stationary)', 'ACI with exponential
  weighting (shift)', 'interval half-width h_c'. Arrow labeled 'uncertainty u_c' points to Stage 3. Stage 3 (orange box):
  'Confidence-Adaptive Admission' with sub-labels 'soft-sigmoid bias: tau_c = 0.3 + 0.4 * sigmoid(5*(1-u_c))', 'threshold
  in [0.3, 0.7]', 'admit if score > threshold'. Below Stage 3: 'LRU cache (capacity=50)'. Clean white background, sans-serif
  font, no 3D effects. Arrows are solid black lines with arrowheads.
aspect_ratio: '21:9'
summary: Hero architecture diagram showing the three-stage VUCCA pipeline
figure_path: figures/fig1_v0.jpg

--- Item 2 ---
id: fig2
figure_type: data
title: Hit Ratio Across Workload Regimes
caption: >-
  Hit ratio comparison across three workload regimes. VUCCA matches LRU across all regimes (0.479, 0.441, 0.413) while providing
  conformal coverage guarantees. ARC2 dominates at ~92% due to ghost-list advantage. VUCCA_no_sigmoid crashes to ~0.15, confirming
  the soft-sigmoid is essential.
image_gen_detailed_description: >-
  Grouped bar chart with 3 groups on x-axis (Stationary, Popularity-Shift, Cold-Start) and 8 bars per group. Y-axis: Hit Ratio
  (0.0 to 1.0). Values per group: Stationary: LRU=0.479, TinyLFU=0.464, ARC2=0.921, VUCCA=0.479, VUCCA_no_sigmoid=0.160, VUCCA_no_ACI=0.479,
  VUCCA_small_K=0.478, VUCCA_entropy=0.472. Popularity-Shift: LRU=0.441, TinyLFU=0.409, ARC2=0.925, VUCCA=0.441, VUCCA_no_sigmoid=0.146,
  VUCCA_no_ACI=0.441, VUCCA_small_K=0.441, VUCCA_entropy=0.427. Cold-Start: LRU=0.413, TinyLFU=0.385, ARC2=0.908, VUCCA=0.413,
  VUCCA_no_sigmoid=0.157, VUCCA_no_ACI=0.413, VUCCA_small_K=0.413, VUCCA_entropy=0.397. Color scheme: baselines in gray (LRU,
  TinyLFU, ARC2), VUCCA in blue, ablations in lighter shades. Legend on right. Grid lines horizontal. Sans-serif font, white
  background.
aspect_ratio: '16:9'
summary: Hit ratio comparison showing VUCCA matches LRU and ablation effects
figure_path: figures/fig2_v0.pdf

--- Item 3 ---
id: fig3
figure_type: data
title: Throughput Comparison Across Regimes
caption: >-
  Throughput (requests per total latency) across three regimes. VUCCA matches LRU throughput in all regimes. Lower throughput
  indicates higher average latency due to more cache misses. ARC2 achieves highest throughput due to its ~92% hit ratio.
image_gen_detailed_description: >-
  Grouped bar chart with 3 groups on x-axis (Stationary, Popularity-Shift, Cold-Start) and 4 bars per group (LRU, TinyLFU,
  ARC2, VUCCA). Y-axis: Throughput (requests/latency, 0.0 to 10.0). Values: Stationary: LRU=5.69, TinyLFU=5.83, ARC2=1.55,
  VUCCA=5.69. Popularity-Shift: LRU=6.03, TinyLFU=6.32, ARC2=1.55, VUCCA=6.03. Cold-Start: LRU=6.28, TinyLFU=6.54, ARC2=1.66,
  VUCCA=6.29. Note: ARC2 has lower throughput despite higher hit ratio because throughput = requests/total_latency and ARC2's
  hit ratio is so high that total latency is low per request. Color scheme: LRU=gray, TinyLFU=light gray, ARC2=dark gray,
  VUCCA=blue. Legend on right. Grid lines horizontal. Sans-serif font, white background.
aspect_ratio: '16:9'
summary: Throughput comparison showing VUCCA matches LRU across regimes
figure_path: figures/fig3_v0.pdf

--- Item 4 ---
id: fig4
figure_type: data
title: 'Ablation: Impact of Design Components'
caption: >-
  Ablation study showing the impact of each VUCCA component on hit ratio relative to the full method. Removing soft-sigmoid
  causes the largest drop (-67%). Removing ACI has no measurable effect. Reducing K from 64 to 10 has negligible effect on
  hit ratio but increases coverage error. Entropy-based uncertainty slightly underperforms conformal intervals.
image_gen_detailed_description: >-
  Horizontal bar chart showing delta in hit ratio relative to full VUCCA (baseline=0). 4 bars, one per ablation. Y-axis labels:
  'no_sigmoid', 'no_ACI', 'small_K', 'entropy'. X-axis: Delta Hit Ratio (-0.35 to 0.0). Values: no_sigmoid=-0.319 (stationary:
  0.479-0.160), no_ACI=0.000, small_K=-0.001, entropy=-0.007. All bars extend left (negative) except no_ACI which is at zero.
  Color: red for negative bars, gray for zero. Error bars showing range across 3 regimes: no_sigmoid ranges from -0.295 to
  -0.323. Bold annotation on no_sigmoid bar: '-67% drop'. Sans-serif font, white background, grid lines vertical.
aspect_ratio: '4:3'
summary: Ablation study showing soft-sigmoid is the critical design component
figure_path: figures/fig4_v0.pdf
</available_figures>

<figure_requirements>
CRITICAL: Include ALL figures from <available_figures>. No exceptions.

- Every figure MUST use \includegraphics{figures/<the filename from its own `figure_path` above>} — INCLUDING the extension it actually has. Data figures are delivered as `.pdf` (vector, so their axis labels stay sharp) and concept figures as `.jpg`. Writing `.jpg` for a `.pdf` figure names a file that is not in figures/ and the build fails on it
- Do NOT skip, convert to tables, or describe without inserting
- Each needs: \begin{figure}[placement], \includegraphics, \caption, \label, \end{figure} — one placement for every figure, see FLOAT PLACEMENT below. Constrain every \includegraphics with `width=\linewidth,height=0.85\textheight,keepaspectratio`. The height is a LAST RESORT, not the usual limit: it exists so a very tall figure cannot overrun the page, and at 0.4 it bound almost everything instead — a 1:1 confusion matrix printed at 50.9% and its 11 pt axis labels reached the page at 5.6 pt, below what any venue accepts. At 0.85 every ratio the paper prompt prescribes (21:9, 16:9, 4:3, 1:1) is limited by WIDTH, prints at 93% and keeps its text above 10 pt. Use exactly these option keys — `max height=` is NOT valid LaTeX
- Use the `caption` field from each figure for \caption{...} — do NOT invent new captions
- Place figures where their [FIGURE:fig_id] markers appear in paper_text
- VERIFICATION: paper.tex MUST have exact same number of \includegraphics as <available_figures>
- Do NOT generate new figure images (no matplotlib, no PIL, no image generation). Use ONLY the pre-generated figures from <available_figures>. They were already created by a previous pipeline step.

FLOAT PLACEMENT: every figure gets \begin{figure}[!htbp]. Measured, not chosen:
the document the aii-paper-to-latex skill sets up is ONE column, so `figure*` is
exactly as wide as `figure` (469.76pt either way) and gains nothing; and any
placement asking for a page TOP — `[!t]`, `[!tbp]` — floated the hero diagram above
the paper's own title on page 1, while `[!htbp]` did not. `[!htbp]` also gives LaTeX
four options, so a float can never be deferred to the end of the document, which one
option alone risks. Where the hero ENDS UP is decided by its [FIGURE:] marker in
paper_text, which is already placed near the end of the Introduction — preserve it.
</figure_requirements>

<artifact_links>
The paper_text contains \footnote{Code: \url{...}} references linking to artifact source code
on GitHub. Include \usepackage{hyperref} and \usepackage{url}.
Preserve these exactly as-is — do not remove, rewrite, or convert them to plain text.
The URLs will not resolve yet (the repo is deployed after compilation) — do NOT try to verify or fix them.
</artifact_links>

<headings>
NEVER use inline math (``$...$``) inside ``\section{...}`` / ``\subsection{...}`` / ``\subsubsection{...}`` arguments — hyperref's bookmark builder errors out (``Token not allowed in a PDF string``) and the PDF outline breaks. If a section heading needs a math-looking term, use the text equivalent (``d star`` not ``$d^*$``, ``alpha-equivalent`` not ``$\alpha$-equivalent``) or wrap it in ``\texorpdfstring{$math$}{plain}``. Inline math inside body paragraphs is fine.
</headings>

<writing_register>
Write in the register of the field's best papers (the style exemplars block below, when the writing step saved any), not in the register of a language
model. Four things are measured on the finished draft, and a draft outside them is sent back with
the numbers:
- Never use: delve, underscore, showcase, intricate, pivotal, realm, commendable, meticulous, tapestry, garner, multifaceted, it is worth noting, plays a crucial role, not only ... but also. These are 10 to 30 times more frequent in machine-written abstracts than in
  human ones, and reviewers read them as such.
- Em dashes: at most 3 per 1,000 words. Use a comma, a colon or a full stop.
- Sentence rhythm: mix short and long sentences. An interquartile range of sentence length under
  8 words reads as machine-written.
- Hedging: at most 15 hedges (may, likely, suggests, appears) per 1,000
  words. State what the evidence supports plainly; hedge where it is thin, not everywhere.
Style never changes substance: numbers, claims, citations and figure markers stay exactly as the
evidence gives them. The user's original request (delivered as a separate message) overrides all
of this wherever the two conflict.
</writing_register>

<style_exemplars>
The draft in <paper_text> was written to the register of these passages, which the writing step
saved as style_exemplars.md. Any prose you add or change here (captions, transitions, cuts
for the page limit) stays in that register.

# Style Exemplars for Cache Admission / Systems Paper

**Style Note**: These papers (SOSP, NSDI, ATC, MICRO, SIGMETRICS) use:
- Short-to-medium sentences (12-20 words median), varied rhythm
- Low hedging (~5-10 per 1000 words) — claims are direct when evidence is strong
- First person ("We", "Our") in abstract/intro, third person in methods/results
- Dense citations: 1-2 per paragraph in Related Work, inline in Methods when citing techniques
- No "delve", "underscore", "showcase", "intricate", "pivotal", "realm", "commendable", "meticulous", "tapestry", "garner", "multifaceted", "it is worth noting", "plays a crucial role", "not only...but also"
- Em dashes: sparse (~1-2 per 1000 words); commas, colons, periods preferred
- Numbers in text: exact values from tables/figures, not approximate

---

## Exemplar 1: S3-FIFO (SOSP '23) — "FIFO Queues are All You Need for Cache Eviction"
*Yang, Zhang, Qiu, Yue, Rashmi. SOSP 2023.*

### Abstract
As a cache eviction algorithm, FIFO has a lot of attractive properties, such as simplicity, speed, scalability, and flash-friendliness. The most prominent criticism of FIFO is its low efficiency (high miss ratio). In this work, we demonstrate a simple, scalable FIFO-based algorithm with three static queues (S3-FIFO). Evaluated on 6594 cache traces from 14 datasets, we show that S3-FIFO has lower miss ratios than state-of-the-art algorithms across traces. Moreover, S3-FIFO's efficiency is robust — it has the lowest mean miss ratio on 10 of the 14 datasets. FIFO queues enable S3-FIFO to achieve good scalability with 6× higher throughput compared to optimized LRU at 16 threads. Our insight is that most objects in skewed workloads will only be accessed once in a short window, so it is critical to evict them early (also called quick demotion). The key of S3-FIFO is a small FIFO queue that filters out most objects from entering the main cache, which provides a guaranteed demotion speed and high demotion precision.

### Introduction (first paragraph)
Software caches, such as Memcached and Linux page cache, are widely deployed today to speed up data access and avoid repeated computation. A cache should be (1) efficient: it should provide a low miss ratio allowing most requests to be fulfilled by the cache with short latencies; (2) performant: serving data from the cache should perform minimal operations with a high throughput; and (3) scalable: the number of cache hits it can serve per second grows with the number of CPU cores. The heart of a cache is the eviction algorithm, which dictates a cache's efficiency, throughput, and scalability.

### Results paragraph (from §5.2)
At the large cache size, S3-FIFO has the largest reductions across almost all percentiles than other algorithms. For example, S3-FIFO reduces miss ratios by more than 32% on 10% of the traces (P90) with a mean of 14% on the large cache size. TinyLFU is the closest competitor. TinyLFU uses a 1% LRU window to filter out unpopular objects and stores most objects in a SLRU cache. TinyLFU's good performance corroborates our observation that quick demotion is critical for efficiency. However, TinyLFU does not work well for all traces, with miss ratios being lower than FIFO on almost 20% of the traces. This phenomenon is more pronounced when the cache size is small, where TinyLFU is worse than FIFO on close to 50% of the traces.

### Discussion/Limitations paragraph (from §6)
We studied the limited number of traces on which S3-FIFO performed poorly and identified one pattern. Most objects in these traces are accessed only twice, and the second request falls out of the small FIFO queue S, which causes the second request to these objects to be cache misses. We remark that these workloads are adversarial for most algorithms that partition the cache space, e.g., TinyLFU, LIRS, 2Q, and CACHEUS. Because the partition for newly inserted objects is smaller than the cache size, it is possible that the second request is a cache hit in LRU and FIFO, but not in these advanced algorithms.

---

## Exemplar 2: Chameleon (MICRO '25) — "Chameleon: Adaptive Caching and Scheduling for Many-Adapter LLM Inference Environments"
*Iliakopoulou, Stojkovic, Alverti, Xu, Franke, Torrellas. MICRO 2025.*

### Abstract
The effectiveness of LLMs has triggered an exponential rise in their deployment, imposing substantial demands on inference clusters. Such clusters often handle numerous concurrent queries for different LLM downstream tasks. To handle multi-task settings with vast LLM parameter counts, Low-Rank Adaptation (LoRA) enables task-specific fine-tuning while sharing most of the base LLM model across tasks. Hence, it supports concurrent task serving with reduced memory requirements. However, existing designs face inefficiencies: they overlook workload heterogeneity, impose high CPU-GPU link bandwidth from frequent adapter loading, and suffer from head-of-line blocking in their schedulers. To address these challenges, we present Chameleon, a novel LLM serving system optimized for many-adapter environments. Chameleon introduces two new ideas: adapter caching and adapter-aware scheduling. First, Chameleon caches popular adapters in GPU memory, minimizing adapter loading times. For caching, it uses otherwise idle GPU memory, avoiding extra memory costs. Second, Chameleon uses a non-preemptive multi-queue scheduler to efficiently account for workload heterogeneity. In this way, Chameleon simultaneously prevents head of line blocking and starvation. Under high loads, Chameleon reduces the P99 and P50 TTFT latencies by 80.7% and 48.1%, respectively, over a state-of-the-art baseline, while improving the throughput by 1.5×.

### Introduction (first paragraph)
Generative Large Language Models (LLMs) have seen an exponential growth in recent years. They have become integral to numerous technologies and applications. As their popularity increases, the number of online queries received by datacenter inference clusters continuously grows. These queries typically target a variety of downstream tasks, e.g., chat-bot conversation, coding, or text summarization. These different tasks require different or special-purpose fine-tuned LLMs to achieve their highest accuracy. Unfortunately, this requirement imposes a large hardware and energy tax on datacenters, as each of these models typically requires large memory and, thus, many GPUs, to store its many parameters.

### Results paragraph (from §5)
Compared to a state-of-the-art baseline, Chameleon reduces the P99 and P50 time-to-first-token (TTFT) latencies by 80.7% and 48.1%, respectively, while improving the throughput by 1.5×. The adapter cache hit ratio reaches 94.2% under high load, and the average cache size is only 2.3% of total GPU memory. The multi-queue scheduler reduces head-of-line blocking by 73% compared to FIFO scheduling.

---

## Exemplar 3: "Can Increasing the Hit Ratio Hurt Cache Throughput?" (arXiv 2024)
*Qiu, Yang, Harchol-Balter. arXiv:2404.16219.*

### Abstract
Software caches are an intrinsic component of almost every computer system. Consequently, caching algorithms, particularly eviction policies, are the topic of many papers. Almost all these prior papers evaluate the caching algorithm based on its hit ratio, namely the fraction of requests that are found in the cache, as opposed to disk. The hit ratio is viewed as a proxy for traditional performance metrics like system throughput or response time. Intuitively it makes sense that higher hit ratio should lead to higher throughput (and lower response time), since more requests are found in the cache (low access time) as opposed to the disk (high access time). This paper challenges this intuition. We show that increasing the hit ratio can actually hurt the throughput (and response time) for many caching algorithms. Our investigation follows a three-pronged approach involving (i) queueing modeling and analysis, (ii) implementation and measurement, and (iii) simulation to validate the accuracy of the queueing model. We also show that the phenomenon of throughput decreasing at higher hit ratios is likely to be more pronounced in future systems, where the trend is towards faster disks and higher numbers of cores per CPU.

---

## Exemplar 4: Conformal Prediction Tutorial (Angelopoulos & Bates, 2021) — "A Gentle Introduction to Conformal Prediction"
*Angelopoulos, Bates. arXiv:2107.07511.*

### Methods-style paragraph (from §1)
Conformal prediction is a straightforward way to generate prediction sets for any model. We will introduce it with a short, pragmatic image classification example, and follow up in later paragraphs with a general explanation. The high-level outline of conformal prediction is as follows. First, we begin with a fitted predicted model (such as a neural network classifier) which we will call f̂. Then, we will create prediction sets (a set of possible labels) for this classifier using a small amount of additional calibration data — we will sometimes call this the calibration step. Formally, suppose we have images as input and they each contain one of K classes. We begin with a classifier that outputs estimated probabilities (softmax scores) for each class: f̂(x) ∈ [0, 1]^K. Then, we reserve a moderate number (e.g., 500) of fresh i.i.d. pairs of images and classes unseen during training, (X1, Y1), ..., (Xn, Yn), for use as calibration data. Using f̂ and the calibration data, we seek to construct a prediction set of possible labels C(Xtest) ⊂ {1, ..., K} that is valid in the following sense: 1−α ≤ P(Ytest ∈ C(Xtest)) ≤ 1−α + 1/(n+1), where (Xtest, Ytest) is a fresh test point from the same distribution, and α ∈ [0, 1] is a user-chosen error rate.

---

## Exemplar 5: Guard (NeurIPS '25) — "Robustifying Learning-Augmented Caching Efficiently without Compromising 1-Consistency"
*Chen, Zhao, Zhang, Tang, Wang, Deng. NeurIPS 2025.*

### Abstract
The online caching problem aims to minimize cache misses when serving a sequence of requests under a limited cache size. While naive learning-augmented caching algorithms achieve ideal 1-consistency, they lack robustness guarantees. Existing robustification methods either sacrifice 1-consistency or introduce excessive computational overhead. In this paper, we introduce Guard, a lightweight robustification framework that enhances the robustness of a broad class of learning-augmented caching algorithms to 2H_{k-1} + 2, while preserving their 1-consistency. Guard achieves the current best-known trade-off between consistency and robustness, with only O(1) additional per-request overhead, thereby maintaining the original time complexity of the base algorithm. Extensive experiments across multiple real-world datasets and prediction models validate the effectiveness of Guard in practice.
</style_exemplars>
FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-paper-to-latex, aii-semscholar-bib.
TODO 2. Review <paper_text> and <available_figures>. Copy all figure images into ./figures/ in your workspace. Count figures — MUST include every one. Plan placements per section. Build `./references.bib` via aii_semscholar_bib__fetch — collect DOIs/ArXiv IDs from <paper_text> and batch-fetch all BibTeX in one call. Do NOT fabricate entries.
TODO 3. Create `./paper.tex` per aii-paper-to-latex skill's setup, write ALL sections, insert ALL figures from <available_figures>, include `./references.bib` via \bibliography. Compile to PDF per skill's process. Fix errors.
TODO 4. CRITICAL VERIFICATION: Run `grep -c 'includegraphics' paper.tex`, confirm count equals figures in <available_figures>. If not, add missing figures. Verify `./paper.pdf` was created.
TODO 5. VISUAL REVIEW: Write Python script to convert EVERY page of paper.pdf to PNG at 150 DPI (use pdf2image or pymupdf). Then read ALL page screenshots — each page image costs ~1,600 tokens so a 15-page paper is only ~24K tokens. You MUST read every page. The ONLY exception is if all page images would not fit in your remaining context — in that case, read as many as fit and state which pages you are skipping and why. Check every page for layout issues, overlapping figures, cut-off text, bad spacing, formatting problems. Fix issues and recompile.
TODO 6. FINAL READ: Check page count (`pdfinfo paper.pdf` or pymupdf). Read entire paper.pdf — check for missing sections, unclear explanations, inconsistencies, typos. Fix and recompile. The ONLY exception is if all pages would not fit in your remaining context — in that case, read as many pages as fit and state which pages you are skipping and why.
</todos>

---

Output the result as JSON to: `/ai-inventor/aii_data/runs/run_XUVIPW24BQbP/4_gen_paper_repo/_4_assemble_paper/paper/workspace/.sdk_openhands_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "FullPaperExpectedFiles": {
      "description": "All expected output files from full paper generation.",
      "properties": {
        "paper_tex_path": {
          "description": "Path to LaTeX source file. Example: 'paper.tex'",
          "title": "Paper Tex Path",
          "type": "string"
        },
        "paper_pdf_path": {
          "description": "Path to compiled PDF. Example: 'paper.pdf'",
          "title": "Paper Pdf Path",
          "type": "string"
        },
        "references_bib_path": {
          "description": "Path to BibTeX bibliography file. Example: 'references.bib'",
          "title": "References Bib Path",
          "type": "string"
        },
        "figure_paths": {
          "description": "Paths to all figure image files. Example: ['figures/fig1_v0.jpg', 'figures/fig2_v0.jpg']",
          "items": {
            "type": "string"
          },
          "title": "Figure Paths",
          "type": "array"
        }
      },
      "required": [
        "paper_tex_path",
        "paper_pdf_path",
        "references_bib_path",
        "figure_paths"
      ],
      "title": "FullPaperExpectedFiles",
      "type": "object"
    }
  },
  "description": "Full paper \u2014 structured output from paper generation.",
  "properties": {
    "title": {
      "description": "Paper title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance. Aim for about 4-8 words (~40 characters).",
      "maxLength": 90,
      "minLength": 12,
      "title": "Title",
      "type": "string"
    },
    "summary": {
      "description": "Brief summary of the generated paper: sections written, figures included, compilation status",
      "maxLength": 5000,
      "minLength": 500,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/FullPaperExpectedFiles",
      "description": "All output files you created. Must include paper.tex, paper.pdf, references.bib, and paths to all figure files."
    }
  },
  "required": [
    "title",
    "summary",
    "out_expected_files"
  ],
  "title": "FullPaper",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `/ai-inventor/aii_data/runs/run_XUVIPW24BQbP/4_gen_paper_repo/_4_assemble_paper/paper/workspace/.sdk_openhands_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [2] HUMAN-USER prompt · 2026-09-10 01:21:51 UTC

```
Survey two recent methods for cache admission and write a one-page note
```

### [3] SKILL-INPUT — aii-paper-to-latex · 2026-09-10 01:22:13 UTC

The agent loaded the **aii-paper-to-latex** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-paper-to-latex
description: "Assembles and compiles a LaTeX paper into paper.pdf: documentclass and package preamble, figure floats that includegraphics pre-generated vector .pdf and .jpg files, float-placement and width rules, and the required pdflatex, bibtex, pdflatex, pdflatex run sequence. Use whenever pre-written text and pre-generated figures must become a compiled PDF, and whenever a build misbehaves — citations printing as question marks, figures drifting to the end or above the title, shrunken axis labels, undefined references. Triggers: latex, tex, pdflatex, bibtex, natbib, includegraphics, figure float, htbp, compile or build the paper, paper.tex, paper.pdf. NOT for: writing the paper's text or deciding its structure (use aii-paper-writing), creating the figure images (aii-data-fig-gen, aii-concept-fig-gen), or fetching bibliography entries (use aii-semscholar-bib); NOT for reshaping a PDF that already exists — merging, splitting, form filling, table extraction (use anthropic-pdf)."
---

## LaTeX Paper Assembly

Assembles a research paper from paper text, pre-generated figures (vector `.pdf` for data figures, `.jpg` for concept figures) and a bibliography into a compiled PDF.

### Document Setup

```latex
\documentclass[11pt,letterpaper]{article}
\usepackage{graphicx, geometry, amsmath, hyperref, url, natbib, booktabs, xcolor, listings}
\geometry{margin=1in}
\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black}
```

### Figure Inclusion

CRITICAL: Include ALL figures. Every figure MUST appear in the paper.

```latex
\begin{figure}[!htbp]
  \centering
  \includegraphics[width=\linewidth,height=0.85\textheight,keepaspectratio]{figures/filename.pdf}
  \caption{Descriptive caption.}
  \label{fig:label}
\end{figure}
```

Rules:
- ALWAYS `[!htbp]` — all four options, so a float can never be deferred to the end of the
  document, which `[t]` or `[h]` alone risks. Do not ask for a page TOP: `[!t]` and
  `[!tbp]` both floated a figure ABOVE the paper's own title on page 1, where `[!htbp]`
  on the same document did not. Where a figure lands is decided by where it is declared
  in the text
- Use `figure`, never `figure*`. This document class is ONE column, so `figure*` is exactly
  as wide as `figure` (469.76pt either way) and gains nothing, while restricting the float
  to a page top
- ALWAYS constrain with `width` and `keepaspectratio`. Add `height` only as a
  LAST RESORT against a very tall figure overrunning the page, and keep it
  generous — `0.85\textheight`. A tight height cap binds on ordinary figures
  and LaTeX then shrinks the TEXT with them: at `0.4\textheight` a square
  figure printed at 50.9%, putting 11 pt axis labels on the page at 5.6 pt.
  The figure generator measures legibility at the figure's OWN size, so it
  cannot see this happen
- Every figure needs `\caption`, `\label`, and a `\ref` in the text
- Do NOT convert figures to tables or describe them without inserting the image
- Do NOT skip any figures

### Compilation Process

Run each command separately (do NOT chain with `&&` — pdflatex often exits non-zero on warnings, which would skip bibtex and leave citations as `??`):

```bash
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

All four commands are required. Skipping bibtex causes `??` in all citations.
Fix any errors between runs. Verify `./paper.pdf` was created.

### Output Files

- `./paper.tex` — LaTeX source
- `./references.bib` — bibliography file
- `./paper.pdf` — compiled PDF
- `./figures/` — all figure images (pre-generated, copied into workspace). Data
  figures are `.pdf` (vector — LaTeX renders their text at page resolution, which
  is what keeps axis labels sharp in print); concept figures are `.jpg`. Use each
  file's OWN extension in `\includegraphics`; there is no conversion step.
````

### [4] SKILL-INPUT — aii-semscholar-bib · 2026-09-10 01:22:13 UTC

The agent loaded the **aii-semscholar-bib** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-semscholar-bib
description: "Fetches real BibTeX entries in one batch from Semantic Scholar by DOI, ArXiv ID or title via aii_semscholar_bib__fetch, normalises citation keys to AuthorYYYY, injects DOIs, and writes the result into references.bib, with a mandatory web-search fallback for anything not found. ALWAYS use whenever a bibliography, reference list or .bib file is being built or extended, and whenever a citation needs a verified entry instead of an invented one — never hand-write BibTeX first. Triggers: bibliography, references.bib, bibtex, citation key, DOI, arXiv id, Semantic Scholar, reference list, cite these papers, natbib entries. NOT for: writing the text around the citations (use aii-paper-writing), running bibtex and compiling (use aii-paper-to-latex), judging whether cited work supports the claims (use amg-paper-verification), or open-ended literature search and PDF mining (use aii-web-tools)."
---

## Tool: `aii_semscholar_bib__fetch`

Batch-fetch BibTeX entries from Semantic Scholar. Pass all references in a single call — the tool handles batching internally.

### How it works

1. **DOI/ArXiv refs** → batched into POST /paper/batch calls (up to 500 per API call, auto-chunked)
2. **Title-only refs** → individual GET /paper/search/match (1s delay between)
3. **Post-process** → fix entry type, fix citation key (AuthorYYYY), inject DOI

The ability server runs a single worker (`max_threads: 1`). Multiple concurrent tool calls are queued — each runs independently (no cross-request aggregation). Batching happens within each request.

### Input format

```json
{
  "references": [
    {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
    {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
    {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
  ]
}
```

Each reference object can have:
- `doi` — DOI string (ArXiv DOIs like `10.48550/arXiv.XXXX.XXXXX` auto-convert to ArXiv IDs)
- `arxiv` — ArXiv ID (e.g. `"2305.14325"`)
- `title` — Paper title (used for search/match when no DOI/ArXiv)
- `author` — First author last name (for cleaner citation key)
- `year` — Publication year (int, for citation key)

At least one of `doi`, `arxiv`, or `title` is required per reference.

### Output format

```json
{
  "success": true,
  "bib_text": "@inproceedings{Vaswani2017, ...}\n\n@article{Wei2022, ...}",
  "total": 3,
  "found": 3,
  "failed_count": 0,
  "entries": [{"citation_key": "Vaswani2017", "bibtex": "...", "title": "...", "doi": "...", "arxiv": ""}],
  "failed": []
}
```

### Workflow

1. Collect DOIs, ArXiv IDs, or titles for all papers you need to cite
2. Call `aii_semscholar_bib__fetch` with the full list in **one call**
3. Save `bib_text` from the response to your `references.bib` file
4. Check `failed` — for any missed papers, follow the **fallback procedure** below

### Fallback for failed references (MANDATORY)

NEVER fabricate BibTeX. For each failed reference:
1. **WebSearch** for `"Title" author year` (try `site:arxiv.org` too)
2. **WebFetch** the paper page → extract title, authors, year, venue, DOI/ArXiv ID
3. If DOI/ArXiv found → retry `aii_semscholar_bib__fetch` with it
4. Last resort: write BibTeX by hand using **only verified info from the actual paper page**

---

### CLI (for manual use / debugging)

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-semscholar-bib" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_semscholar_bib__fetch.py --refs '[
  {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
  {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
  {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
]'
```

`--json, -j` — output raw JSON instead of .bib text

**If the script fails** with a connection error (ability server not running): create a local `.venv`, install server deps from `server_requirements.txt` into it, then import the `@aii_ability` function from the script and call it directly — bypassing the server:
```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r "$SKILL_DIR/scripts/server_requirements.txt"
```
````

### [5] SKILL-INPUT — amg-open-img-ubuntu · 2026-09-10 01:35:07 UTC

The agent loaded the **amg-open-img-ubuntu** skill.

```
Tool: invoke_skill
{
  "name": "amg-open-img-ubuntu"
}
```
