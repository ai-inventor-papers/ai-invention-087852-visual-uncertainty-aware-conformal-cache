#!/usr/bin/env python3
"""Evaluation of Visual Uncertainty-Aware Conformal Cache Admission experiment results."""

import json
import numpy as np
from pathlib import Path
from loguru import logger
from scipy import stats
import sys

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

@logger.catch(reraise=True)
def main():
    # Load experiment results
    data_path = Path("full_method_out.json")
    logger.info(f"Loading experiment results from {data_path}")
    with data_path.open() as f:
        exp_data = json.load(f)
    
    # Extract datasets
    datasets = exp_data.get("datasets", [])
    if not datasets:
        logger.error("No datasets found in experiment results")
        sys.exit(1)
    
    # We assume single dataset
    dataset = datasets[0]
    examples = dataset.get("examples", [])
    logger.info(f"Loaded {len(examples)} examples")
    
    # Organize data by regime, policy, chunk
    # Structure: data[regime][policy][chunk] = parsed_output_dict
    data = {}
    # Also keep raw examples for output
    raw_examples = []
    
    for ex in examples:
        input_str = ex["input"]
        output_str = ex["output"]
        # Parse output JSON string
        try:
            output = json.loads(output_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse output JSON: {output_str}")
            continue
        
        regime = ex.get("metadata_regime")
        policy = ex.get("metadata_policy")
        chunk = ex.get("metadata_chunk")
        
        if regime not in data:
            data[regime] = {}
        if policy not in data[regime]:
            data[regime][policy] = {}
        data[regime][policy][chunk] = output
        
        # Keep raw example for output, but add per-example evaluation metrics
        eval_ex = ex.copy()
        # Parse predict_* fields to compute improvement metrics
        try:
            pred_lru = float(ex.get("predict_LRU", 0))
            pred_tinylfu = float(ex.get("predict_TinyLFU", 0))
            pred_arc2 = float(ex.get("predict_ARC2", 0))
            pred_ours = float(ex.get("predict_OURS", 0))
            
            # Avoid division by zero
            if pred_lru > 0:
                eval_ex["eval_improvement_over_lru"] = (pred_ours - pred_lru) / pred_lru * 100.0
            else:
                eval_ex["eval_improvement_over_lru"] = 0.0
                
            if pred_tinylfu > 0:
                eval_ex["eval_improvement_over_tinylfu"] = (pred_ours - pred_tinylfu) / pred_tinylfu * 100.0
            else:
                eval_ex["eval_improvement_over_tinylfu"] = 0.0
                
            if pred_arc2 > 0:
                eval_ex["eval_improvement_over_arc2"] = (pred_ours - pred_arc2) / pred_arc2 * 100.0
            else:
                eval_ex["eval_improvement_over_arc2"] = 0.0
        except (ValueError, TypeError):
            # If parsing fails, set default values
            eval_ex["eval_improvement_over_lru"] = 0.0
            eval_ex["eval_improvement_over_tinylfu"] = 0.0
            eval_ex["eval_improvement_over_arc2"] = 0.0
        
        raw_examples.append(eval_ex)
    
    logger.info(f"Regimes found: {list(data.keys())}")
    for regime in data:
        logger.info(f"  Policies: {list(data[regime].keys())}")
        for policy in data[regime]:
            logger.info(f"    Chunks: {sorted(data[regime][policy].keys())}")
    
    # Metrics to compute
    metrics = ["hit_ratio", "throughput", "average_latency", "coverage_error"]
    regimes = list(data.keys())
    policies = ["LRU", "TinyLFU", "ARC2", "OURS"]
    baselines = ["LRU", "TinyLFU", "ARC2"]
    
    # Prepare metrics_agg dictionary
    metrics_agg = {}
    
    # Compute mean metrics per regime, policy
    for regime in regimes:
        for policy in policies:
            if policy not in data[regime]:
                continue
            policy_data = data[regime][policy]
            # Get list of chunk keys sorted
            chunks = sorted(policy_data.keys())
            for metric in metrics:
                values = [policy_data[chunk].get(metric, np.nan) for chunk in chunks]
                # Filter out NaN
                values = [v for v in values if not np.isnan(v)]
                if len(values) == 0:
                    mean_val = np.nan
                else:
                    mean_val = np.mean(values)
                # Replace hyphens in regime name for metric key
                regime_key = regime.replace('-', '_')
                metric_name = f"{metric}_{regime_key}_{policy}"
                metrics_agg[metric_name] = float(mean_val)
    
    # Compute effect sizes, p-values, improvement percentages for each metric vs each baseline
    for regime in regimes:
        for metric in metrics:
            for baseline in baselines:
                if baseline not in data[regime] or "OURS" not in data[regime]:
                    continue
                baseline_chunks = sorted(data[regime][baseline].keys())
                ours_chunks = sorted(data[regime]["OURS"].keys())
                # We assume same chunks for both
                common_chunks = sorted(set(baseline_chunks) & set(ours_chunks))
                if len(common_chunks) < 2:
                    logger.warning(f"Not enough common chunks for {regime} {metric} {baseline}")
                    continue
                baseline_vals = [data[regime][baseline][c].get(metric, np.nan) for c in common_chunks]
                ours_vals = [data[regime]["OURS"][c].get(metric, np.nan) for c in common_chunks]
                # Filter NaN
                pairs = [(b, o) for b, o in zip(baseline_vals, ours_vals) if not (np.isnan(b) or np.isnan(o))]
                if len(pairs) < 2:
                    logger.warning(f"Not enough valid pairs for {regime} {metric} {baseline}")
                    continue
                baseline_arr, ours_arr = zip(*pairs)
                baseline_arr = np.array(baseline_arr)
                ours_arr = np.array(ours_arr)
                
                # For latency, lower is better; but we keep raw values for effect size
                differences = ours_arr - baseline_arr
                mean_diff = np.mean(differences)
                std_diff = np.std(differences, ddof=1)
                if std_diff == 0:
                    effect_size = np.nan
                else:
                    effect_size = mean_diff / std_diff
                
                # Paired t-test
                try:
                    t_stat, p_val = stats.ttest_rel(ours_arr, baseline_arr)
                except Exception as e:
                    logger.warning(f"Paired t-test failed: {e}")
                    p_val = np.nan
                
                # Improvement percentage: ((OURS - baseline) / baseline) * 100
                # Avoid division by zero
                baseline_mean = np.mean(baseline_arr)
                if baseline_mean == 0:
                    improvement_pct = np.nan
                else:
                    improvement_pct = (mean_diff / baseline_mean) * 100.0
                
                metrics_agg[f"effect_size_{metric}_{regime_key}_vs_{baseline}"] = float(effect_size)
                metrics_agg[f"p_value_{metric}_{regime_key}_vs_{baseline}"] = float(p_val)
                metrics_agg[f"improvement_percentage_{metric}_{regime_key}_vs_{baseline}"] = float(improvement_pct)
    
    # Data quality flags
    # 1. identical-baseline-results: check if LRU, TinyLFU, ARC2 have identical results across all chunks and regimes
    identical_baseline = True
    for regime in regimes:
        for policy in baselines:
            if policy not in data[regime]:
                identical_baseline = False
                break
            if policy == baselines[0]:
                continue
            # Compare with first baseline
            ref_policy = baselines[0]
            ref_chunks = sorted(data[regime][ref_policy].keys())
            curr_chunks = sorted(data[regime][policy].keys())
            if ref_chunks != curr_chunks:
                identical_baseline = False
                break
            for chunk in ref_chunks:
                ref_vals = data[regime][ref_policy][chunk]
                curr_vals = data[regime][policy][chunk]
                for metric in metrics:
                    if ref_vals.get(metric) != curr_vals.get(metric):
                        identical_baseline = False
                        break
                if not identical_baseline:
                    break
            if not identical_baseline:
                break
        if not identical_baseline:
            break
    metrics_agg["data_quality_identical_baseline_results"] = float(identical_baseline)
    
    # 2. hardcoded-coverage: check if coverage_error is constant across all examples for each policy
    hardcoded_coverage = True
    for regime in regimes:
        for policy in policies:
            if policy not in data[regime]:
                continue
            policy_data = data[regime][policy]
            chunks = sorted(policy_data.keys())
            cov_errors = [policy_data[chunk].get("coverage_error", np.nan) for chunk in chunks]
            cov_errors = [v for v in cov_errors if not np.isnan(v)]
            if len(cov_errors) == 0:
                continue
            # Check if all values are the same
            if len(set(cov_errors)) > 1:
                hardcoded_coverage = False
                break
        if not hardcoded_coverage:
            break
    metrics_agg["data_quality_hardcoded_coverage"] = float(hardcoded_coverage)
    
    # 3. vucca_underperforming_baselines: check if VUCCA has lower hit_ratio than all baselines in all regimes
    vucca_underperforming = True
    for regime in regimes:
        if "OURS" not in data[regime]:
            vucca_underperforming = False
            break
        ours_data = data[regime]["OURS"]
        for baseline in baselines:
            if baseline not in data[regime]:
                vucca_underperforming = False
                break
            baseline_data = data[regime][baseline]
            common_chunks = sorted(set(ours_data.keys()) & set(baseline_data.keys()))
            for chunk in common_chunks:
                ours_hr = ours_data[chunk].get("hit_ratio", np.nan)
                base_hr = baseline_data[chunk].get("hit_ratio", np.nan)
                if np.isnan(ours_hr) or np.isnan(base_hr):
                    continue
                if ours_hr >= base_hr:  # OURS not worse (i.e., equal or better)
                    vucca_underperforming = False
                    break
            if not vucca_underperforming:
                break
        if not vucca_underperforming:
            break
    metrics_agg["data_quality_vucca_underperforming_baselines"] = float(vucca_underperforming)
    
    # Prepare output in exp_eval_sol_out format
    output = {
        "metadata": {
            "evaluation_name": "Statistical Evaluation of VUCCA Cache Results",
            "description": "Comprehensive statistical evaluation of Visual Uncertainty-Aware Conformal Cache Admission experiment results",
            "regimes": regimes,
            "policies": policies,
            "metrics_computed": metrics,
        },
        "metrics_agg": metrics_agg,
        "datasets": [
            {
                "dataset": dataset.get("dataset", "cache_admission_evaluation"),
                "examples": raw_examples
            }
        ]
    }
    
    # Save output
    output_path = Path("full_eval_out.json")
    logger.info(f"Saving evaluation results to {output_path}")
    with output_path.open("w") as f:
        json.dump(output, f, indent=2)
    
    logger.info("Evaluation completed successfully")

if __name__ == "__main__":
    main()