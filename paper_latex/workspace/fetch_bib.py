#!/usr/bin/env python3
"""Fetch BibTeX entries from Semantic Scholar for all paper references."""
import json
import time
import sys
from typing import Optional

import requests

API_BASE = "https://api.semanticscholar.org/graph/v1"

REFERENCES = [
    {"arxiv": "1706.03762", "author": "Einziger", "year": 2017, "title": "TinyLFU: A Highly Efficient Cache Admission Policy"},
    {"title": "FIFO queues are all you need for cache eviction", "author": "Yang", "year": 2023},
    {"title": "ARC: A Self-Tuning, Low Overhead Replacement Cache", "author": "Megiddo", "year": 2003},
    {"arxiv": "2009.09206", "author": "Mangal", "year": 2020, "title": "DEAP Cache: Deep Eviction Admission and Prefetching for Cache"},
    {"title": "Robustifying Learning-Augmented Caching Efficiently without Compromising 1-Consistency", "author": "Chen", "year": 2025},
    {"title": "Chameleon: Adaptive Caching and Scheduling for Many-Adapter LLM Inference Environments", "author": "Iliakopoulou", "year": 2024},
    {"arxiv": "2107.07511", "author": "Angelopoulos", "year": 2021, "title": "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification"},
    {"title": "Adaptive Conformal Inference Under Distribution Shift", "author": "Gibbs", "year": 2021},
    {"title": "Conformal Inference for Online Prediction with Arbitrary Distribution Shifts", "author": "Gibbs", "year": 2022},
    {"arxiv": "2010.11929", "author": "Dosovitskiy", "year": 2021, "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale"},
    {"arxiv": "2404.16219", "author": "Qiu", "year": 2024, "title": "Can Increasing the Hit Ratio Hurt Cache Throughput?"},
    {"title": "Learning to Cache and Caching to Learn: Regret Analysis of Caching Algorithms", "author": "Bura", "year": 2020},
]


def search_by_title(title: str, author: str, year: int) -> Optional[dict]:
    """Search Semantic Scholar by title and author."""
    url = f"{API_BASE}/paper/search"
    params = {
        "query": f"{title} {author}",
        "limit": 5,
        "fields": "title,authors,year,venue,externalIds,publicationDate",
        "year": year,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("data"):
            # Try to find the best match
            for paper in data["data"]:
                if paper.get("year") == year:
                    return paper
            return data["data"][0]
    except Exception as e:
        print(f"  Search error: {e}", file=sys.stderr)
    return None


def get_by_arxiv(arxiv_id: str) -> Optional[dict]:
    """Get paper by ArXiv ID."""
    url = f"{API_BASE}/paper/ARXIV:{arxiv_id}"
    params = {"fields": "title,authors,year,venue,externalIds,publicationDate"}
    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"  ArXiv lookup error: {e}", file=sys.stderr)
    return None


def format_bibtex(paper: dict, key_author: str, key_year: int, entry_type: str = "inproceedings") -> str:
    """Format a paper dict as BibTeX."""
    title = paper.get("title", "Unknown Title")
    authors_raw = paper.get("authors", [])
    authors = " and ".join(a.get("name", "") for a in authors_raw) if authors_raw else f"{key_author} et al."
    year = paper.get("year", key_year)
    venue = paper.get("venue", "")
    external_ids = paper.get("externalIds", {})
    doi = external_ids.get("DOI", "")
    arxiv = external_ids.get("ArXiv", "")
    
    citation_key = f"{key_author}{key_year}"
    
    lines = [f"@{entry_type}{{{citation_key},"]
    lines.append(f"  title = {{{title}}},")
    lines.append(f"  author = {{{authors}}},")
    lines.append(f"  year = {{{year}}},")
    if venue:
        lines.append(f"  booktitle = {{{venue}}},")
    if doi:
        lines.append(f"  doi = {{{doi}}},")
    if arxiv:
        lines.append(f"  note = {{{arxiv}}},")
    lines.append("}")
    return "\n".join(lines)


def main():
    results = []
    failed = []
    
    for i, ref in enumerate(REFERENCES):
        author = ref["author"]
        year = ref["year"]
        title = ref["title"]
        arxiv = ref.get("arxiv")
        
        print(f"[{i+1}/{len(REFERENCES)}] Fetching: {title[:60]}...", file=sys.stderr)
        
        paper = None
        
        # Try ArXiv first if available
        if arxiv:
            paper = get_by_arxiv(arxiv)
        
        # Fall back to title search
        if not paper:
            paper = search_by_title(title, author, year)
        
        if paper:
            entry_type = "article" if "journal" in str(paper.get("venue", "").lower()) else "inproceedings"
            bibtex = format_bibtex(paper, author, year, entry_type)
            results.append(bibtex)
            print(f"  Found: {paper.get('title', 'Unknown')[:60]}", file=sys.stderr)
        else:
            failed.append(ref)
            print(f"  FAILED", file=sys.stderr)
        
        time.sleep(2.0)  # Rate limiting - Semantic Scholar is strict
    
    # Write results
    with open("references.bib", "w") as f:
        f.write("\n\n".join(results) + "\n")
    
    print(f"\nSaved {len(results)} entries to references.bib", file=sys.stderr)
    if failed:
        print(f"Failed to fetch {len(failed)} entries:", file=sys.stderr)
        for ref in failed:
            print(f"  - {ref['title']}", file=sys.stderr)


if __name__ == "__main__":
    main()
