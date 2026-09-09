#!/usr/bin/env python3
"""
VUCCA: Visual Uncertainty-Aware Conformal Cache Admission

Implements VUCCA and baselines (LRU, TinyLFU, ARC2) with ablations.
Evaluates across stationary, shift, and cold-start regimes.

Key design: Each dataset entry is an ITEM CATALOG (unique items with popularity).
We expand the catalog into a REQUEST TRACE by repeating each item popularity_count times,
then replay the trace through cache simulators to measure hit rates.
"""

from loguru import logger
from pathlib import Path
import json
import sys
import math
import resource
import gc
import numpy as np
from scipy.special import expit as sigmoid
from sklearn.cluster import KMeans
from collections import OrderedDict, defaultdict
from typing import Dict, List, Any, Tuple, Optional

# ─── Logging ───
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

# ─── Hardware limits ───
RAM_BUDGET = 10 * 1024**3  # 10 GB of 14 GB available
resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET * 3, RAM_BUDGET * 3))

# ─── Constants ───
DATASET_DIR = Path("/ai-inventor/aii_data/runs/run_XUVIPW24BQbP/3_invention_loop/iter_1/gen_art/gen_art_dataset_1")
WORKSPACE = Path(__file__).resolve().parent
CACHE_SIZE = 50  # Cache capacity (number of items)
CALIBRATION_FRACTION = 0.2
ALPHA = 0.1  # Conformal miscoverage rate (target 90% coverage)
K_CLUSTERS = 64
MIN_CLUSTER_SIZE = 5
TRACE_MULTIPLIER = 3  # Multiply popularity to get enough repeats for hits
MAX_TRACE_LEN = 50000  # Cap trace length to avoid memory issues


# ─── Data Loading ───
def load_all_regimes() -> Dict[str, List[Dict[str, Any]]]:
    """Load all three regimes from the full dataset."""
    data_path = DATASET_DIR / "full_data_out.json"
    
    with open(data_path, 'r') as f:
        raw = json.load(f)
    
    regimes = {}
    for ds in raw.get("datasets", []):
        name = ds["dataset"]
        examples = []
        for ex in ds.get("examples", []):
            inp = json.loads(ex["input"])
            examples.append({
                "item_id": int(ex["output"]),
                "embedding": np.array(inp["embedding"], dtype=np.float32),
                "popularity_count": int(inp["popularity_count"]),
                "cluster_id": int(inp["cluster_id"]),
                "timestamp": int(inp["timestamp"]),
                "image_file": inp.get("image_file", ""),
                "fold": ex.get("metadata_fold", 0),
                "dataset": name,
            })
        regimes[name] = examples
    return regimes


def catalog_to_trace(items: List[Dict[str, Any]], regime: str,
                     rng: np.random.RandomState) -> List[int]:
    """
    Expand an item catalog into a request trace.
    
    Each item appears popularity_count * TRACE_MULTIPLIER times.
    Requests are shuffled to simulate realistic access patterns.
    For 'sudden_popularity_shift', we create two halves with different popularity.
    """
    # Build weighted list: each item appears popularity_count * multiplier times
    trace = []
    for item in items:
        count = max(1, item["popularity_count"] * TRACE_MULTIPLIER)
        trace.extend([item["item_id"]] * count)
    
    # Cap trace length
    if len(trace) > MAX_TRACE_LEN:
        trace = trace[:MAX_TRACE_LEN]
    
    # Shuffle to simulate realistic access patterns
    rng.shuffle(trace)
    
    # For shift regime, create two phases with different distributions
    if regime == "sudden_popularity_shift":
        mid = len(trace) // 2
        # First half: keep as-is (old popularity distribution)
        # Second half: reverse order to simulate shift (old cold items become hot)
        trace[mid:] = list(reversed(trace[mid:]))
    
    return trace


# ─── Cache Simulators ───
class LRUCache:
    """Standard LRU cache with no admission filter (admits everything)."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.total = 0

    def access(self, item_id: int) -> bool:
        self.total += 1
        if item_id in self.cache:
            self.cache.move_to_end(item_id)
            self.hits += 1
            return True
        else:
            self.misses += 1
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[item_id] = True
            return False

    @property
    def hit_rate(self) -> float:
        return self.hits / max(self.total, 1)


class TinyLFUCache:
    """TinyLFU: Frequency sketch-based admission filter + LRU."""
    def __init__(self, capacity: int, sketch_size: int = 4096):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.sketch_size = sketch_size
        self.sketch = np.zeros((4, sketch_size), dtype=np.uint16)
        self.hits = 0
        self.misses = 0
        self.total = 0

    def _hashes(self, item_id: int) -> List[int]:
        h = hash(item_id)
        return [(h >> (8 * i)) % self.sketch_size for i in range(4)]

    def _frequency(self, item_id: int) -> int:
        hs = self._hashes(item_id)
        return min(self.sketch[i][h] for i, h in enumerate(hs))

    def _increment(self, item_id: int):
        hs = self._hashes(item_id)
        for i, h in enumerate(hs):
            self.sketch[i][h] = min(self.sketch[i][h] + 1, 65535)

    def access(self, item_id: int) -> bool:
        self.total += 1
        if item_id in self.cache:
            self.cache.move_to_end(item_id)
            self._increment(item_id)
            self.hits += 1
            return True
        else:
            self.misses += 1
            freq = self._frequency(item_id)
            if freq > 0 or len(self.cache) < self.capacity:
                if len(self.cache) >= self.capacity:
                    self.cache.popitem(last=False)
                self.cache[item_id] = True
                self._increment(item_id)
            return False

    @property
    def hit_rate(self) -> float:
        return self.hits / max(self.total, 1)


class ARC2Cache:
    """ARC2: Adaptive Replacement Cache with T1, T2, B1, B2 lists."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.p = 0  # Replacement target
        self.t1 = OrderedDict()  # Recent
        self.t2 = OrderedDict()  # Frequent
        self.b1 = OrderedDict()  # Ghost recent
        self.b2 = OrderedDict()  # Ghost frequent
        self.hits = 0
        self.misses = 0
        self.total = 0

    def _adjust_p(self, in_b1: bool, in_b2: bool):
        if in_b1:
            self.p = min(self.p + len(self.t2), self.capacity)
        elif in_b2:
            self.p = max(self.p - len(self.t1), 0)

    def access(self, item_id: int) -> bool:
        self.total += 1
        if item_id in self.t1:
            self.t1.move_to_end(item_id)
            del self.t1[item_id]
            self.t2[item_id] = True
            self.t2.move_to_end(item_id)
            self.hits += 1
            return True
        if item_id in self.t2:
            self.t2.move_to_end(item_id)
            self.hits += 1
            return True
        if item_id in self.b1:
            self._adjust_p(True, False)
            self._evict(item_id, from_ghost=True, ghost_list='b1')
            return False
        if item_id in self.b2:
            self._adjust_p(False, True)
            self._evict(item_id, from_ghost=True, ghost_list='b2')
            return False
        self._evict(item_id, from_ghost=False)
        self.misses += 1
        return False

    def _evict(self, new_item: int, from_ghost: bool = False, ghost_list: str = ''):
        if not from_ghost:
            if len(self.t1) + len(self.t2) >= self.capacity:
                if len(self.t1) > self.p:
                    evicted = next(iter(self.t1))
                    del self.t1[evicted]
                    self.b1[evicted] = True
                else:
                    evicted = next(iter(self.t2))
                    del self.t2[evicted]
                    self.b2[evicted] = True
            # Limit ghost sizes
            while len(self.b1) > self.capacity:
                self.b1.popitem(last=False)
            while len(self.b2) > self.capacity:
                self.b2.popitem(last=False)
        self.t1[new_item] = True
        self.t1.move_to_end(new_item)

    @property
    def hit_rate(self) -> float:
        return self.hits / max(self.total, 1)


# ─── VUCCA Components ───
class ConformalTracker:
    """Tracks conformal prediction residuals per cluster."""
    def __init__(self, alpha: float = 0.1, lambda_aci: float = 0.01):
        self.alpha = alpha
        self.lambda_aci = lambda_aci
        self.residuals: Dict[int, List[Tuple[float, float]]] = defaultdict(list)  # cluster -> [(residual, timestamp)]
        self.quantiles: Dict[int, float] = {}
        self.aci_weights: Dict[int, float] = {}  # Running weighted quantile for ACI

    def add_residual(self, cluster_id: int, residual: float, timestamp: float, regime: str):
        self.residuals[cluster_id].append((residual, timestamp))
        if regime == "sudden_popularity_shift":
            self._update_aci(cluster_id, timestamp)
        else:
            self._update_split_conformal(cluster_id)

    def _update_split_conformal(self, cluster_id: int):
        residuals = [r for r, _ in self.residuals[cluster_id]]
        if len(residuals) >= 2:
            q_level = np.ceil((1 - self.alpha) * (len(residuals) + 1)) / len(residuals)
            q_level = min(q_level, 1.0)
            self.quantiles[cluster_id] = np.quantile(residuals, q_level)

    def _update_aci(self, cluster_id: int, current_time: float):
        """Adaptive Conformal Inference with exponential weighting."""
        items = self.residuals[cluster_id]
        if len(items) < 2:
            return
        weights = []
        residuals = []
        for r, t in items:
            w = math.exp(-self.lambda_aci * (current_time - t))
            weights.append(w)
            residuals.append(r)
        weights = np.array(weights)
        weights /= weights.sum()
        residuals = np.array(residuals)
        # Weighted quantile
        sorted_idx = np.argsort(residuals)
        sorted_r = residuals[sorted_idx]
        sorted_w = weights[sorted_idx]
        cum_w = np.cumsum(sorted_w)
        q_level = 1 - self.alpha
        idx = np.searchsorted(cum_w, q_level)
        idx = min(idx, len(sorted_r) - 1)
        self.quantiles[cluster_id] = sorted_r[idx]

    def get_quantile(self, cluster_id: int) -> float:
        return self.quantiles.get(cluster_id, 1.0)  # Default to wide interval

    def get_half_width(self, cluster_id: int) -> float:
        """Get the conformal interval half-width as uncertainty measure."""
        q = self.get_quantile(cluster_id)
        return max(q, 0.01)


class VUCCAAdmission:
    """VUCCA: Visual Uncertainty-Aware Conformal Cache Admission."""
    def __init__(self, tau_base: float = 0.3, beta: float = 0.4,
                 gamma: float = 5.0, alpha: float = 0.1, lambda_aci: float = 0.01,
                 use_soft_sigmoid: bool = True, use_aci: bool = True,
                 k_clusters: int = 64, use_entropy: bool = False):
        self.tau_base = tau_base
        self.beta = beta
        self.gamma = gamma
        self.alpha = alpha
        self.use_soft_sigmoid = use_soft_sigmoid
        self.use_aci = use_aci
        self.k_clusters = k_clusters
        self.use_entropy = use_entropy
        self.conformal = ConformalTracker(alpha=alpha, lambda_aci=lambda_aci)
        self.cluster_stats: Dict[int, Dict[str, float]] = {}
        self.cluster_embeddings: Dict[int, List[np.ndarray]] = defaultdict(list)
        self.cluster_counts: Dict[int, int] = defaultdict(int)
        self.cluster_total_requests: Dict[int, int] = defaultdict(int)
        self.cluster_misses: Dict[int, int] = defaultdict(int)
        self.kmeans = None
        self.admission_decisions: List[Dict[str, Any]] = []

    def fit_clusters(self, embeddings: np.ndarray):
        """Run KMeans clustering on embeddings."""
        n_samples = len(embeddings)
        k = min(self.k_clusters, max(n_samples // 2, 1))
        if k < 1:
            k = 1
        self.kmeans = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=100)
        labels = self.kmeans.fit_predict(embeddings)
        # Merge small clusters
        from collections import Counter
        counts = Counter(labels)
        merge_map = {}
        for lbl, cnt in counts.items():
            if cnt < MIN_CLUSTER_SIZE and len(counts) > 1:
                # Find nearest larger cluster
                center = self.kmeans.cluster_centers_[lbl]
                best_dist = float('inf')
                best_target = None
                for other_lbl, other_cnt in counts.items():
                    if other_cnt >= MIN_CLUSTER_SIZE and other_lbl != lbl:
                        d = np.linalg.norm(center - self.kmeans.cluster_centers_[other_lbl])
                        if d < best_dist:
                            best_dist = d
                            best_target = other_lbl
                if best_target is not None:
                    merge_map[lbl] = best_target
                else:
                    merge_map[lbl] = lbl
            else:
                merge_map[lbl] = lbl
        return np.array([merge_map[l] for l in labels]), k

    def get_bias(self, cluster_id: int) -> float:
        """Compute admission bias for a cluster.
        
        Returns a value in [tau_base, tau_base + beta].
        High confidence (narrow interval) -> high bias -> more permissive admission.
        Low confidence (wide interval) -> low bias -> more selective admission.
        """
        half_width = self.conformal.get_half_width(cluster_id)
        
        if self.use_entropy:
            # Use entropy-based uncertainty instead
            count = self.cluster_counts.get(cluster_id, 0)
            if count > 1:
                entropy = np.log(max(count, 1))
                half_width = entropy / max(np.log(max(self.k_clusters, 2)), 1)
            else:
                half_width = 0.5  # Default uncertainty for cold clusters
        
        # Normalize half_width to [0, 1] range for meaningful sigmoid input
        norm_uncertainty = min(half_width, 1.0)
        
        if self.use_soft_sigmoid:
            # Soft-sigmoid: tau_c = tau_base + beta * sigmoid(gamma * (1 - uncertainty))
            # High uncertainty -> low bias; Low uncertainty -> high bias
            tau_c = self.tau_base + self.beta * sigmoid(self.gamma * (1.0 - norm_uncertainty))
        else:
            # Exponential bias (ablation): tau_c = tau_base + beta * exp(-gamma * uncertainty)
            tau_c = self.tau_base + self.beta * math.exp(-self.gamma * norm_uncertainty)
            tau_c = min(tau_c, 1.0)
        
        return tau_c

    def admission_filter(self, item_id: int, cluster_id: int, popularity: int) -> bool:
        """Decide whether to admit an item based on conformal uncertainty.
        
        The key insight: items from uncertain clusters (wide conformal interval)
        should be admitted more selectively, even if they appear popular.
        Items from confident clusters (narrow interval) get a pass.
        
        Returns True if the item should be admitted to cache.
        """
        tau_c = self.get_bias(cluster_id)
        # Normalize popularity to [0, 1]
        norm_pop = min(popularity / 1000.0, 1.0)
        
        # Dynamic threshold: high confidence -> low threshold (admit more)
        #                    low confidence -> high threshold (admit fewer)
        # tau_c in [0.3, 0.7], so threshold ranges from ~0.15 to ~0.55
        threshold = 0.6 - tau_c
        
        # Score: popularity weighted by confidence
        # High confidence amplifies the popularity signal
        score = norm_pop * tau_c + (1.0 - norm_pop) * 0.05
        
        return score > threshold

    def update_from_calibration(self, item_id: int, cluster_id: int, popularity: int,
                                timestamp: float, regime: str, was_miss: bool):
        """Update conformal statistics during calibration phase."""
        self.cluster_counts[cluster_id] += 1
        self.cluster_total_requests[cluster_id] += 1
        if was_miss:
            self.cluster_misses[cluster_id] += 1
        
        # Estimate miss rate for this cluster
        total = self.cluster_total_requests[cluster_id]
        misses = self.cluster_misses[cluster_id]
        actual_miss_rate = misses / max(total, 1)
        
        # Predicted miss rate from popularity (inverse relationship)
        norm_pop = min(popularity / 1000.0, 1.0)
        predicted_miss_rate = 1.0 - norm_pop
        
        # Residual: absolute error in miss rate prediction
        residual = abs(actual_miss_rate - predicted_miss_rate)
        
        # Use ACI for shift regime, split conformal otherwise
        use_aci = self.use_aci and regime == "sudden_popularity_shift"
        self.conformal.add_residual(cluster_id, residual, timestamp,
                                     "sudden_popularity_shift" if use_aci else regime)


# ─── Simulation Engine ───
def run_baseline_simulation(trace: List[int], cache_class, cache_kwargs: Dict) -> Dict[str, Any]:
    """Run a baseline cache simulation on a request trace."""
    cache = cache_class(**cache_kwargs)
    
    # Split trace: first 20% calibration (warm-up), rest is test
    cal_size = max(int(len(trace) * CALIBRATION_FRACTION), 1)
    cal_trace = trace[:cal_size]
    test_trace = trace[cal_size:]
    
    # Calibration: run through cache to warm up
    for item_id in cal_trace:
        cache.access(item_id)
    
    # Reset counters for test phase only
    cal_hits = cache.hits
    cal_misses = cache.misses
    cal_total = cache.total
    
    # Test phase
    for item_id in test_trace:
        cache.access(item_id)
    
    # Test-only metrics
    test_hits = cache.hits - cal_hits
    test_misses = cache.misses - cal_misses
    test_total = cache.total - cal_total
    test_hit_rate = test_hits / max(test_total, 1)
    throughput = (test_hits * 1.0 + test_misses * 10.0) / max(test_total, 1)
    
    return {
        "hit_rate": test_hit_rate,
        "throughput": throughput,
        "hits": test_hits,
        "misses": test_misses,
        "total_requests": test_total,
        "coverage": 0.0,
        "calibration_size": cal_size,
        "test_size": len(test_trace),
    }


def run_vucca_simulation(items: List[Dict[str, Any]], vucca: VUCCAAdmission,
                         regime: str, rng: np.random.RandomState) -> Dict[str, Any]:
    """Run VUCCA simulation with clustering and conformal admission."""
    # Extract embeddings and fit clusters
    embeddings = np.array([ex["embedding"] for ex in items], dtype=np.float32)
    cluster_labels, k_used = vucca.fit_clusters(embeddings)
    
    # Build item -> cluster mapping
    item_to_cluster = {}
    item_to_pop = {}
    for i, ex in enumerate(items):
        item_to_cluster[ex["item_id"]] = int(cluster_labels[i])
        item_to_pop[ex["item_id"]] = ex["popularity_count"]
    
    # Generate request trace
    trace = catalog_to_trace(items, regime, rng)
    
    # Split trace
    cal_size = max(int(len(trace) * CALIBRATION_FRACTION), 1)
    cal_trace = trace[:cal_size]
    test_trace = trace[cal_size:]
    
    # Phase 1: Calibration - run with a reference cache to collect stats
    cal_cache = LRUCache(CACHE_SIZE)
    for t_idx, item_id in enumerate(cal_trace):
        hit = cal_cache.access(item_id)
        cluster_id = item_to_cluster.get(item_id, 0)
        pop = item_to_pop.get(item_id, 1)
        was_miss = not hit
        
        # Update conformal stats
        vucca.update_from_calibration(
            item_id, cluster_id, pop, float(t_idx), regime, was_miss
        )
    
    # Phase 2: Test - VUCCA admission
    test_cache = LRUCache(CACHE_SIZE)
    admitted = 0
    rejected = 0
    
    for t_idx, item_id in enumerate(test_trace):
        cluster_id = item_to_cluster.get(item_id, 0)
        pop = item_to_pop.get(item_id, 1)
        
        # Check if already in cache (hit regardless of admission)
        if hasattr(test_cache, 'cache') and item_id in test_cache.cache:
            test_cache.access(item_id)  # Hit
            continue
        
        # Admission decision
        admit = vucca.admission_filter(item_id, cluster_id, pop)
        if admit:
            admitted += 1
            test_cache.access(item_id)
        else:
            rejected += 1
            test_cache.misses += 1
            test_cache.total += 1
    
    # Compute metrics
    test_total = test_cache.total
    test_hits = test_cache.hits
    test_misses = test_cache.misses
    test_hit_rate = test_hits / max(test_total, 1)
    throughput = (test_hits * 1.0 + test_misses * 10.0) / max(test_total, 1)
    
    # Coverage: what fraction of cluster miss rates fall within conformal intervals
    covered = 0
    total_checked = 0
    for cluster_id in vucca.cluster_counts:
        if vucca.cluster_counts[cluster_id] > 0:
            q = vucca.conformal.get_quantile(cluster_id)
            actual_mr = vucca.cluster_misses[cluster_id] / vucca.cluster_total_requests[cluster_id]
            # Predicted miss rate from popularity
            avg_pop = sum(item_to_pop.get(vid, 1) for vid in vucca.cluster_stats.get(cluster_id, {})) / max(len(vucca.cluster_stats.get(cluster_id, {})), 1)
            predicted_mr = 1.0 - min(avg_pop / 1000.0, 1.0) if avg_pop > 0 else 0.5
            if abs(actual_mr - predicted_mr) <= q:
                covered += 1
            total_checked += 1
    coverage = covered / max(total_checked, 1)
    
    # Collect bias values
    bias_values = {}
    for cid in set(cluster_labels):
        bias_values[int(cid)] = vucca.get_bias(cid)
    
    return {
        "hit_rate": test_hit_rate,
        "throughput": throughput,
        "hits": test_hits,
        "misses": test_misses,
        "total_requests": test_total,
        "coverage": coverage,
        "clusters_used": k_used,
        "bias_min": min(bias_values.values()) if bias_values else 0,
        "bias_max": max(bias_values.values()) if bias_values else 0,
        "admitted": admitted,
        "rejected": rejected,
        "calibration_size": cal_size,
        "test_size": len(test_trace),
    }


# ─── Main Experiment ───
@logger.catch(reraise=True)
def main():
    logger.info("=" * 60)
    logger.info("VUCCA: Visual Uncertainty-Aware Conformal Cache Admission")
    logger.info("=" * 60)
    
    # Load data
    logger.info("Loading datasets...")
    regimes = load_all_regimes()
    for name, exs in regimes.items():
        logger.info(f"  {name}: {len(exs)} items")
    
    all_results = []
    
    # VUCCA variants
    vucca_configs = [
        ("VUCCA", {"use_soft_sigmoid": True, "use_aci": True, "k_clusters": K_CLUSTERS, "use_entropy": False}),
        ("VUCCA_no_sigmoid", {"use_soft_sigmoid": False, "use_aci": True, "k_clusters": K_CLUSTERS, "use_entropy": False}),
        ("VUCCA_no_ACI", {"use_soft_sigmoid": True, "use_aci": False, "k_clusters": K_CLUSTERS, "use_entropy": False}),
        ("VUCCA_small_K", {"use_soft_sigmoid": True, "use_aci": True, "k_clusters": 10, "use_entropy": False}),
        ("VUCCA_entropy", {"use_soft_sigmoid": True, "use_aci": True, "k_clusters": K_CLUSTERS, "use_entropy": True}),
    ]
    
    for regime_name, items in regimes.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Regime: {regime_name} ({len(items)} items)")
        logger.info(f"{'='*60}")
        
        regime_results = []
        
        # Generate trace once per regime
        rng = np.random.RandomState(42)
        trace = catalog_to_trace(items, regime_name, rng)
        logger.info(f"  Trace length: {len(trace)} requests")
        
        # Run baselines
        for bname, bclass in [("LRU", LRUCache), ("TinyLFU", TinyLFUCache), ("ARC2", ARC2Cache)]:
            logger.info(f"  Running {bname}...")
            try:
                result = run_baseline_simulation(trace, bclass, {"capacity": CACHE_SIZE})
                result["method"] = bname
                result["params"] = {}
                regime_results.append(result)
                logger.info(f"    Hit rate: {result['hit_rate']:.4f}, Throughput: {result['throughput']:.2f}")
            except Exception as e:
                logger.error(f"  {bname} failed: {e}")
                regime_results.append({"method": bname, "hit_rate": 0.0, "throughput": 0.0, "coverage": 0.0, "error": str(e), "params": {}})
        
        # Run VUCCA variants
        for vname, vparams in vucca_configs:
            logger.info(f"  Running {vname}...")
            try:
                vucca = VUCCAAdmission(
                    tau_base=0.3, beta=0.4, gamma=5.0,
                    alpha=ALPHA, lambda_aci=0.01,
                    use_soft_sigmoid=vparams["use_soft_sigmoid"],
                    use_aci=vparams["use_aci"],
                    k_clusters=vparams["k_clusters"],
                    use_entropy=vparams["use_entropy"],
                )
                # Use fresh RNG for each variant to ensure fair comparison
                v_rng = np.random.RandomState(42)
                result = run_vucca_simulation(items, vucca, regime_name, v_rng)
                result["method"] = vname
                result["params"] = vparams
                regime_results.append(result)
                logger.info(f"    Hit rate: {result['hit_rate']:.4f}, Throughput: {result['throughput']:.2f}, "
                           f"Coverage: {result.get('coverage', 0):.4f}, "
                           f"Bias: [{result.get('bias_min', 0):.3f}, {result.get('bias_max', 0):.3f}]")
            except Exception as e:
                logger.error(f"  {vname} failed: {e}")
                regime_results.append({"method": vname, "hit_rate": 0.0, "throughput": 0.0, "coverage": 0.0, "error": str(e), "params": vparams})
        
        all_results.append({
            "regime": regime_name,
            "num_items": len(items),
            "trace_length": len(trace),
            "results": regime_results,
        })
        
        # Free memory
        del trace, items
        gc.collect()
    
    # Build output in exp_gen_sol_out.json format
    output = {
        "metadata": {
            "method_name": "VUCCA",
            "description": "Visual Uncertainty-Aware Conformal Cache Admission with Adaptive Conformal Inference, soft-sigmoid admission bias, and semantic clustering",
            "parameters": {
                "cache_size": CACHE_SIZE,
                "calibration_fraction": CALIBRATION_FRACTION,
                "alpha": ALPHA,
                "k_clusters": K_CLUSTERS,
                "tau_base": 0.3,
                "beta": 0.4,
                "gamma": 5.0,
                "trace_multiplier": TRACE_MULTIPLIER,
            },
            "baselines": ["LRU", "TinyLFU", "ARC2"],
            "ablations": ["no_sigmoid", "no_ACI", "small_K", "entropy"],
            "regimes": ["stationary_hot_clusters", "sudden_popularity_shift", "cold_start"],
        },
        "datasets": []
    }
    
    for regime_data in all_results:
        dataset_entry = {
            "dataset": regime_data["regime"],
            "examples": []
        }
        for result in regime_data["results"]:
            method_key = result["method"].lower().replace(" ", "_")
            example = {
                "input": json.dumps({
                    "regime": regime_data["regime"],
                    "method": result["method"],
                    "params": result.get("params", {}),
                    "num_items": regime_data["num_items"],
                    "trace_length": regime_data["trace_length"],
                }),
                "output": json.dumps({
                    "hit_rate": result["hit_rate"],
                    "throughput": result["throughput"],
                    "hits": result.get("hits", 0),
                    "misses": result.get("misses", 0),
                    "total_requests": result.get("total_requests", 0),
                    "coverage": result.get("coverage", 0.0),
                    "clusters_used": result.get("clusters_used", None),
                    "bias_min": result.get("bias_min", None),
                    "bias_max": result.get("bias_max", None),
                    "admitted": result.get("admitted", None),
                    "rejected": result.get("rejected", None),
                    "calibration_size": result.get("calibration_size", 0),
                    "test_size": result.get("test_size", 0),
                    "error": result.get("error", None),
                }),
                "metadata_fold": 0,
                "metadata_feature_names": ["hit_rate", "throughput", "coverage"],
                f"predict_{method_key}": json.dumps({
                    "hit_rate": result["hit_rate"],
                    "throughput": result["throughput"],
                    "coverage": result.get("coverage", 0.0),
                }),
            }
            dataset_entry["examples"].append(example)
        output["datasets"].append(dataset_entry)
    
    # Write output
    output_path = WORKSPACE / "method_out.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"\nResults saved to {output_path}")
    logger.info("Experiment complete.")
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    for regime_data in all_results:
        logger.info(f"\nRegime: {regime_data['regime']} (trace={regime_data['trace_length']})")
        for r in regime_data["results"]:
            logger.info(f"  {r['method']:25s} | Hit: {r['hit_rate']:.4f} | "
                       f"Throughput: {r['throughput']:.2f} | Coverage: {r.get('coverage', 0):.4f}")


if __name__ == "__main__":
    main()
