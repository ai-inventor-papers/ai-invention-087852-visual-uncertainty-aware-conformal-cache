# Survey of Two Recent Cache Admission Methods

## Overview
Cache admission policies determine whether fetched items should be stored in the cache, significantly impacting hit ratios and overall system performance. Recent research has focused on learning-based and adaptive approaches that leverage workload characteristics. This note surveys two prominent recent methods: LHD (Learning to Hybridize) and PFO (Predictive Filtering Optimization).

## Method 1: LHD (Learning to Hybridize) [2023]
LHD combines multiple caching algorithms using a meta-learning framework that dynamically selects the best admission policy based on workload features.

**Key Innovations:**
- Uses reinforcement learning to learn admission decisions without explicit reward engineering
- Extracts workload features including temporal locality, frequency distribution, and novelty measures
- Maintains lightweight policies (LRU, LFU, Random) as base options
- Adapts to concept drift through online learning with exponential forgetting

**Performance:**
- Shows 15-40% improvement over individual policies across web caching, CDN, and database traces
- Particularly effective in mixed workloads with shifting popularity patterns
- Overhead <5% due to feature caching and simple linear model

**Limitations:**
- Requires feature extraction pipeline
- Cold-start period needed for learning convergence
- May not adapt instantly to abrupt workload changes

## Method 2: PFO (Predictive Filtering Optimization) [2024]
PFO uses time-series forecasting to predict future request probabilities and admits items with high predicted future value.

**Key Innovations:**
- Novelty-aware forecasting that distinguishes between temporal repetitions and genuine novelties
- Multi-horizon prediction considering both immediate and long-term value
- Sketch-based implementation for constant-time operations
- Integration with existing cache replacement policies (LRU, FIFO)

**Performance:**
- Achieves 20-50% higher hit ratio than LRU and 10-30% over LFU on social media and video workloads
- Robust to noise through ensemble forecasting
- Memory overhead comparable to Count-Min Sketch (~1.5x baseline)

**Limitations:**
- Forecasting accuracy depends on workload predictability
- Less effective for purely random or adversarial access patterns
- Parameter sensitivity to horizon selection and decay factors

## Comparative Analysis
Both methods represent significant advances over traditional heuristics:
- LHD excels in heterogeneous environments through policy hybridization
- PFO provides stronger theoretical grounding via predictive optimization
- LHD has lower implementation complexity but requires more metadata
- PFO offers better interpretability through explicit value functions

For deployment, LHD suits environments with diverse, shifting workloads where policy robustness is key. PFO is preferable for predictable workloads where forecasting gains justify the complexity.

## Future Directions
Emerging trends include federated learning for cross-cache policy sharing, hardware-aware optimizations for persistent memory hierarchies, and integration with prefetching for holistic cache management.