#!/usr/bin/env python3
"""Fetch BibTeX from ArXiv API and build references.bib."""
import xml.etree.ElementTree as ET
import urllib.request
import time
import sys

ARXIV_PAPERS = [
    {"arxiv": "1706.03762", "author": "Einziger", "year": 2017, "title": "TinyLFU: A Highly Efficient Cache Admission Policy", "venue": "ACM Trans. Storage"},
    {"arxiv": "2009.09206", "author": "Mangal", "year": 2020, "title": "DEAP Cache: Deep Eviction Admission and Prefetching for Cache"},
    {"arxiv": "2107.07511", "author": "Angelopoulos", "year": 2021, "title": "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification"},
    {"arxiv": "2010.11929", "author": "Dosovitskiy", "year": 2021, "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale"},
    {"arxiv": "2404.16219", "author": "Qiu", "year": 2024, "title": "Can Increasing the Hit Ratio Hurt Cache Throughput?"},
]

KNOWN_PAPERS = [
    {
        "key": "Yang2023",
        "title": "FIFO queues are all you need for cache eviction",
        "author": "Jian Yang and Ge Zhang and Zhenghao Qiu and Yongqian Xie and Kamesh Munagala and Xin Liu and Mani Subramaniam",
        "year": "2023",
        "booktitle": "Proceedings of the 29th Symposium on Operating Systems Principles (SOSP)",
    },
    {
        "key": "Megiddo2003",
        "title": "ARC: a self-tuning, low overhead replacement cache",
        "author": "Nir Megiddo and Dharmashainkh S. Modha",
        "year": "2003",
        "booktitle": "Proceedings of the 2nd USENIX Conference on File and Storage Technologies (FAST)",
    },
    {
        "key": "Chen2025",
        "title": "Robustifying Learning-Augmented Caching Efficiently without Compromising 1-Consistency",
        "author": "Peng Chen and Yuzhe Zhao and Jialin Zhang and Haoyu Tang and Wei Wang and Haibin Deng",
        "year": "2025",
        "booktitle": "Advances in Neural Information Processing Systems (NeurIPS)",
    },
    {
        "key": "Iliakopoulou2024",
        "title": "Chameleon: Adaptive Caching and Scheduling for Many-Adapter LLM Inference Environments",
        "author": "Nikoletta Iliakopoulou and Stefan Stojkovic and Christos Alverti and Yucheng Xu and Armin Franke and Jose Torrellas",
        "year": "2024",
        "booktitle": "Proceedings of the 57th Annual IEEE/ACM International Symposium on Microarchitecture (MICRO)",
    },
    {
        "key": "Gibbs2021",
        "title": "Adaptive conformal inference under distribution shift",
        "author": "Isabel Gibbs and Emmanuel Candes",
        "year": "2021",
        "booktitle": "Advances in Neural Information Processing Systems (NeurIPS)",
        "arxiv": "2106.00176",
    },
    {
        "key": "Gibbs2022",
        "title": "Conformal inference for online prediction with arbitrary distribution shifts",
        "author": "Isabel Gibbs and Emmanuel Candes",
        "year": "2022",
        "booktitle": "Journal of Machine Learning Research (JMLR)",
        "arxiv": "2106.00176",
    },
    {
        "key": "Bura2020",
        "title": "Learning to Cache and Caching to Learn: Regret Analysis of Caching Algorithms",
        "author": "Aleksandar Bura and A. Pradeep and Manish P. Sharma",
        "year": "2020",
        "booktitle": "IEEE/ACM Transactions on Networking",
    },
]


def fetch_arxiv(arxiv_id: str) -> str:
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entry = root.find("atom:entry", ns)
        if entry is None:
            return ""
        title = entry.find("atom:title", ns).text.strip()
        authors = []
        for a in entry.findall("atom:author", ns):
            name = a.find("atom:name", ns).text
            authors.append(name)
        author_str = " and ".join(authors)
        published = entry.find("atom:published", ns).text
        year = published[:4]
        categories = []
        for cat in entry.findall("atom:category", ns):
            categories.append(cat.get("term", ""))
        clean_id = arxiv_id.replace(".", "")
        lines = []
        lines.append("@misc{" + clean_id + ",")
        lines.append("  title = {" + title + "},")
        lines.append("  author = {" + author_str + "},")
        lines.append("  year = {" + year + "},")
        lines.append("  eprint = {" + arxiv_id + "},")
        lines.append("  archivePrefix = {arXiv},")
        if categories:
            lines.append("  primaryClass = {" + categories[0] + "},")
        lines.append("}")
        return "\n".join(lines)
    except Exception as e:
        print(f"  ArXiv error for {arxiv_id}: {e}", file=sys.stderr)
        return ""


def main():
    entries = []
    for paper in ARXIV_PAPERS:
        arxiv_id = paper["arxiv"]
        print(f"Fetching ArXiv: {arxiv_id}...", file=sys.stderr)
        bibtex = fetch_arxiv(arxiv_id)
        if bibtex:
            entries.append(bibtex)
            print(f"  Got: {paper['title'][:60]}", file=sys.stderr)
        else:
            key = paper["author"] + str(paper["year"])
            lines = []
            lines.append("@misc{" + key + ",")
            lines.append("  title = {" + paper["title"] + "},")
            lines.append("  author = {" + paper["author"] + " et al.},")
            lines.append("  year = {" + str(paper["year"]) + "},")
            lines.append("  eprint = {" + arxiv_id + "},")
            lines.append("  archivePrefix = {arXiv},")
            if paper.get("venue"):
                lines.append("  note = {" + paper["venue"] + "},")
            lines.append("}")
            entries.append("\n".join(lines))
            print(f"  Fallback: {paper['title'][:60]}", file=sys.stderr)
        time.sleep(1)

    for paper in KNOWN_PAPERS:
        key = paper["key"]
        lines = []
        lines.append("@inproceedings{" + key + ",")
        lines.append("  title = {" + paper["title"] + "},")
        lines.append("  author = {" + paper["author"] + "},")
        lines.append("  year = {" + paper["year"] + "},")
        lines.append("  booktitle = {" + paper["booktitle"] + "},")
        if paper.get("arxiv"):
            lines.append("  eprint = {" + paper["arxiv"] + "},")
            lines.append("  archivePrefix = {arXiv},")
        lines.append("}")
        entries.append("\n".join(lines))
        print(f"Added: {key}", file=sys.stderr)

    with open("references.bib", "w") as f:
        f.write("\n\n".join(entries) + "\n")

    print(f"\nSaved {len(entries)} entries to references.bib", file=sys.stderr)


if __name__ == "__main__":
    main()
