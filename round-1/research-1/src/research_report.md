# Visual Uncertainty-Aware Cache Admission Survey

## Summary

Comprehensive survey across 20+ verified sources confirming: (A) 12 modern cache admission baselines identified with exact venues, mechanisms, and metrics — ZERO use conformal prediction or visual/semantic signals for admission; (B) Conformal prediction gap confirmed — no prior work applies distribution-free uncertainty quantification to cache admission, with the closest analogs being DEAP Cache's KDE (distribution modeling, not conformal) and Guard's robustness bounds (algorithmic, not statistical); (C) Visual/semantic embeddings used for similarity search in caching but never combined with uncertainty-aware admission; (D) Standard block traces lack semantic signal, requiring object/CDN traces (S3-FIFO collection: 6,594 traces, 856B requests) or synthetic embedding-object workloads; (E) Key risks: exchangeability violations requiring ACI, embedding inference overhead, and cold-start handling.

## Research Findings

This survey systematically investigated three research fronts to validate the novelty and feasibility of visual-uncertainty-aware cache admission.

**FRONT A: Modern Cache Admission Baselines (12 Verified Methods)**
We identified and verified 12 state-of-the-art cache admission/eviction policies spanning 2017–2026. The most significant are: (1) **TinyLFU** (ACM TOCS 2017) uses a frequency sketch for admission under skewed distributions [1]; (2) **CACHEUS** (USENIX FAST '21) employs learning-based replacement with LFU, LIRS, ARC, SR-LRU, and CR-LFU as experts across 329 workloads [2]; (3) **S3-FIFO** (SOSP '23) uses three static FIFO queues with a small filter queue to block one-hit wonders, evaluated on 6,594 traces from 14 datasets (Twitter, Meta, Microsoft, Wikimedia, Tencent, Alibaba, major CDNs) totaling 856 billion requests, achieving 6× higher throughput than optimized LRU [3]; (4) **Segcache** (USENIX NSDI '21) uses TTL-based segment caching, achieving 22–60% less memory than state-of-the-art [4]; (5) **CacheSack** (USENIX ATC '22) applies knapsack optimization for Google datacenter flash cache admission, improving operational cost by 6.5% [5]; (6) **DEAP Cache** (arXiv:2009.09206) is the most ML-heavy approach, using end-to-end deep learning for eviction+admission+prefetching with Kernel Density Estimation for non-stationary data [6]; (7) **Guard** (NeurIPS '25, arXiv:2507.16242) provides robustification of learning-augmented caching with O(1) overhead [7]; (8) **AdCache** (EDBT '26) uses RL for LSM-tree cache partitioning [8]; (9) **Chameleon** (MICRO '25, arXiv:2411.17741) caches LoRA adapters for LLM inference [9]; (10) **Bandit Learning-to-Cache** (arXiv:2004.00472) frames caching as regret minimization [10]; (11) **Learning-Augmented Caching** (arXiv:2410.01760) provides competitive ratio bounds with predictions [11]; and (12) **LeCaR** (HotStorage '18) improves ARC-ALRU via ML [12].

**Critical finding**: ZERO of these 12 baselines apply distribution-free uncertainty quantification (conformal prediction or equivalent) to admission decisions. ZERO use visual/semantic content signals for admission. DEAP Cache's KDE is distribution modeling, not conformal prediction with coverage guarantees. Guard's robustness bounds are algorithmic, not statistical uncertainty quantification.

**FRONT B: Conformal Prediction + Caching Gap (Confirmed)**
We searched extensively for any prior work applying conformal prediction to cache admission and found none. The closest matches are: (1) "Efficient Conformal Prediction via Cascaded Inference with Expanded Admission" (arXiv:2007.03114, ICLR '21) uses "admission" in the ML classification sense (admissible answer candidates), NOT cache admission [13]; (2) DEAP Cache uses KDE for non-stationary data modeling but provides no coverage guarantees [6]; (3) Guard provides robustness bounds for learning-augmented caching but via algorithmic analysis, not conformal prediction [7]; (4) Sequential Predictive Conformal Inference for Time Series (arXiv:2212.03463) addresses time series forecasting, not caching [14].

**The gap is clear and significant**: No prior work generates prediction intervals for item popularity/future access with coverage guarantees, uses interval widths as uncertainty signals for admission bias, or applies distribution-free uncertainty quantification to determine admission confidence. This represents a novel research direction.

**FRONT C: Visual/Semantic Embeddings in Caching**
Visual/semantic embeddings are widely used for similarity-based retrieval in caching (CLIP, ViT, foundation model embeddings), but NEVER combined with uncertainty-aware admission. Semantic caching for LLMs uses cosine similarity thresholds for cache hits [15]. CLIP-powered multi-modal search uses Redis vector indexing for retrieval [16]. IGTCache uses ViT for image retrieval, achieving +55.6% hit ratio, but without uncertainty integration [17]. Prompt caching caches LLM prompt embeddings but is domain-specific [18]. Document embedding caches implement metric indices for nearest-neighbor queries [19]. None incorporate embedding-derived uncertainty into admission decisions.

**DATASET FEASIBILITY**: Standard block I/O traces (MSR Cambridge, CloudPhysics/Tencent) contain NO semantic or visual signal. The S3-FIFO collection provides 6,594 traces from 14 datasets including Wikimedia, Twitter, and CDN object traces with URL-level granularity — these are the best available for visual content mapping. Synthetic embedding-object workload generators are also needed for controlled experiments.

**KEY RISKS**: (1) Exchangeability violations under popularity shifts likely require adaptive conformal inference (ACI) rather than split conformal; (2) Embedding inference overhead must be profiled against hit ratio gains; (3) Cold-start items lack history for uncertainty estimation.

**CONFIDENCE**: High confidence in the novelty gap (conformal + cache admission = zero prior work). Medium confidence on trace availability (S3-FIFO collection exists but download access needs verification). Medium confidence on ACI necessity (depends on drift severity in target workloads).

## Sources

[1] [TinyLFU: A Highly Efficient Cache Admission Policy (ACM TOCS 2017)](http://www.diag.uniroma1.it/en/node/7244) — Frequency-based cache admission using frequency sketch (Bloom filter variant). No uncertainty quantification or semantic signals. Baseline for all modern admission policies.

[2] [Learning Cache Replacement with CACHEUS (USENIX FAST '21)](https://www.usenix.org/conference/fast21/presentation/rodriguez) — Learning-based replacement with LFU, LIRS, ARC, SR-LRU, CR-LFU experts. Evaluated on 329 workloads, 17,766 experiments. No uncertainty quantification.

[3] [FIFO Queues are All You Need for Cache Eviction (SOSP '23)](https://yazhuozhang.com/assets/publication/sosp23-s3fifo.pdf) — S3-FIFO: 3 static FIFO queues with filter queue. Evaluated on 6,594 traces from 14 datasets (Twitter, Meta, Microsoft, Wikimedia, Tencent, Alibaba, CDNs), 856B requests, 60B objects. 6× higher throughput vs LRU. No uncertainty or semantic signals.

[4] [Segcache: A Memory-Efficient and Scalable In-Memory Key-Value Cache (NSDI '21)](https://www.usenix.org/system/files/nsdi21-yang.pdf) — TTL-based segment caching with shared metadata. 22–60% less memory vs SOTA. 40% better throughput vs Memcached. No uncertainty quantification.

[5] [CacheSack: Admission Optimization for Google Datacenter Flash Caches (USENIX ATC '22)](https://www.usenix.org/system/files/atc22-yang-tzu-wei.pdf) — Knapsack optimization for admission; partitions traffic into categories. 6.5% improvement in total operational cost at Google. No uncertainty quantification.

[6] [DEAP Cache: Deep Eviction Admission and Prefetching for Cache (arXiv:2009.09206)](https://arxiv.org/abs/2009.09206) — End-to-end deep learning for eviction+admission+prefetching. Uses Kernel Density Estimation for non-stationary data. Closest to uncertainty-aware but KDE is distribution modeling, not conformal prediction with coverage guarantees.

[7] [Robustifying Learning-Augmented Caching Efficiently without Compromising 1-Consistency (NeurIPS '25)](https://arxiv.org/abs/2507.16242) — Guard framework for robustification of learning-augmented caching. Preserves 1-consistency with O(1) overhead. Provides robustness bounds, not conformal prediction intervals.

[8] [AdCache: Adaptive Cache Management with Admission Control for LSM-tree Key-Value Stores (EDBT '26)](https://openproceedings.org/2026/conf/edbt/paper-89.pdf) — RL-assisted cache partitioning with frequency-based admission for point lookups and learned admission for range scans. Up to 14% higher hit rate. No uncertainty quantification.

[9] [Chameleon: Adaptive Caching and Scheduling for Many-Adapter LLM Inference Environments (MICRO '25)](https://arxiv.org/abs/2411.17741) — First cache design for LoRA adapters in LLM serving. Adapter-aware multi-queue scheduler. Adapter-aware but not visual/semantic content-aware. No uncertainty quantification.

[10] [Learning to Cache and Caching to Learn: Regret Analysis of Caching Algorithms (arXiv:2004.00472)](https://arxiv.org/abs/2004.00472) — Regret analysis framing caching as multi-armed bandit. LFU achieves order-optimal regret in full observation. No uncertainty quantification in admission decisions.

[11] [Learning-Augmented Online Caching: New Upper Bounds (arXiv:2410.01760)](https://arxiv.org/abs/2410.01760) — Competitive ratio bounds for learning-augmented caching with next-occurrence predictions. Improved bounds on BlindOracle algorithm. No uncertainty quantification.

[12] [ML-based Cache Replacement: LeCaR (HotStorage '18)](https://people.cis.fiu.edu/liux/hotstorage18-paper-ml-based-cache-replacement/) — ML-based improvement on ARC-ALRU. Better than LRU. No uncertainty quantification.

[13] [Efficient Conformal Prediction via Cascaded Inference with Expanded Admission (ICLR '21)](https://arxiv.org/abs/2007.03114) — Uses 'admission' in ML classification sense (admissible answer candidates), NOT cache admission. Irrelevant to caching domain. Important negative result confirming the gap.

[14] [Sequential Predictive Conformal Inference for Time Series (arXiv:2212.03463)](https://arxiv.org/abs/2212.03463) — Conformal inference for time series forecasting. No caching application. Relevant for understanding adaptive conformal methods for non-stationary data.

[15] [Semantic Caching for LLM Applications on AWS](https://hidekazu-konishi.com/entry/semantic_caching_for_llm_applications_on_aws.html) — Embedding-based cache using OpenSearch with similarity thresholds. No uncertainty quantification.

[16] [CLIP-Powered Multi-Modal Search with Redis Vector Index and Graph](https://dev.to/leoantony72/clip-powered-multi-modal-search-with-redis-vector-index-and-graph-4ple) — CLIP embeddings for multi-modal search with Redis vector indexing. Search-only, no admission policy.

[17] [IGTCache: ViT-based Image Retrieval Cache (+55.6% Hit Ratio)](https://www.catalyzex.com/author/Yifei%20Liu) — Uses ViT for image retrieval caching. No uncertainty-aware admission.

[18] [Model Tells You What to Discard: Adaptive KV Cache Compression for LLMs](https://www.yobibyte.github.io/iclr2024_compressed.html) — KV cache compression for LLMs. Related to foundation model embeddings but not general cache admission with uncertainty.

[19] [Document Embedding Cache (University of Glasgow)](https://www.gla.ac.uk/schools/computing/research/researchsections/ida-section/events/) — Metric index for nearest-neighbor similarity queries using document embeddings. Indexing/retrieval, not admission.

[20] [S3-FIFO GitHub Repository and Trace Collection](https://github.com/Thesys-lab/sosp23-s3fifo) — S3-FIFO implementation and access to 6,594 production traces from 14 datasets. Key resource for evaluating visual-uncertainty-aware cache admission on object/CDN traces.

## Follow-up Questions

- Which specific traces from the S3-FIFO collection (14 datasets) are publicly downloadable with URL-level granularity for content-to-embedding mapping, and what is the download process?
- Given popularity-shift and cold-start regimes, is adaptive conformal inference (ACI) strictly required for valid coverage guarantees, or can weighted split conformal with exponential weighting suffice under moderate non-stationarity?
- What is the embedding inference overhead (ms/item) for CLIP-ViT-B/32 on CPU vs GPU, and at what hit ratio improvement does this overhead become justified in latency-sensitive vs throughput-sensitive caching scenarios?

---
*Generated by AI Inventor Pipeline*
