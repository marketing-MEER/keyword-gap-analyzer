"""Keyword gap analysis between your site and up to 5 competitors.

Every keyword any site ranks for is put into one gap type (missing, weak,
untapped, shared, strong) and scored by revenue potential instead of raw
volume, because long, specific keywords drive most SEO revenue.
"""
import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from .report import find_column, to_number

# Revenue share by keyword length, NP Digital (579,240 leads, Jan 2024):
# 1-2 words 4.76%, 3-6 words 46.29%, 7+ words 48.95%. Normalised to the 3-6 bucket,
# so a 1-2 word keyword counts ~0.1x and a 7+ word keyword ~1.06x of its volume.
# Source: https://neilpatel.com/marketing-stats/keywords-that-drive-revenue/
LENGTH_WEIGHT = {"1-2 words": 4.76 / 46.29, "3-6 words": 1.0, "7+ words": 48.95 / 46.29}

# Comparison modifiers. "Top"/"best" keywords converted at 1.08% (2022) -> 1.66% (2023), NP Digital.
# Source: https://neilpatel.com/marketing-stats/conversion-rate-keywords-containing-top-or-best/
COMPARISON = re.compile(r"\b(?:best|top|vs|versus|review|reviews|alternative|alternatives|compare|comparison)\b")

GAP_ORDER = ["missing", "weak", "untapped", "shared", "strong"]


def length_bucket(keyword: str) -> str:
    n = len(keyword.split())
    return "1-2 words" if n <= 2 else ("3-6 words" if n <= 6 else "7+ words")


def site_name(df_raw: pd.DataFrame, url_col: str | None, path) -> str:
    if url_col:
        for url in df_raw[url_col].dropna().astype(str):
            host = urlparse(url if "://" in url else "https://" + url).netloc.lower()
            if host:
                return host[4:] if host.startswith("www.") else host
    return Path(path).stem


def load_export(path, max_position: int = 100) -> tuple[str, pd.DataFrame]:
    """Read an Ahrefs 'Organic keywords' / Semrush 'Organic Positions' / GSC queries export."""
    raw = pd.read_csv(path)
    kw = find_column(raw, ["keyword", "query", "top queries", "search term"])
    pos = find_column(raw, ["position", "current position", "rank", "pos"])
    vol = find_column(raw, ["volume", "search volume", "avg. monthly searches", "impressions"])
    url = find_column(raw, ["url", "current url", "landing page", "page", "top pages"])
    if not kw or not pos:
        raise ValueError(f"{path}: need keyword and position columns. Found: {list(raw.columns)}")
    df = pd.DataFrame({
        "keyword": raw[kw].astype(str).str.strip().str.lower(),
        "position": to_number(raw[pos]),
        "volume": to_number(raw[vol]) if vol else 0,
        "url": raw[url].astype(str) if url else "",
    })
    df = df[(df["position"] > 0) & (df["position"] <= max_position) & (df["keyword"] != "")]
    df = df.sort_values("position").drop_duplicates("keyword")
    return site_name(raw, url, path), df


def gap_type(you: float | None, rivals: list[float]) -> str:
    """you = your position or None; rivals = positions of competitors that rank."""
    if you is None:
        return "untapped" if len(rivals) == 1 else "missing"
    if not rivals:
        return "strong"
    if you < min(rivals):
        return "strong"
    if you > max(rivals):
        return "weak"
    return "shared"


def analyze(you_path, competitor_paths, max_position: int = 100) -> tuple[pd.DataFrame, str, list[str]]:
    me, mine = load_export(you_path, max_position)
    rivals = [load_export(p, max_position) for p in competitor_paths]
    names = [name if name != me else f"{name} ({i + 1})" for i, (name, _) in enumerate(rivals)]

    table = mine.set_index("keyword")[["position", "volume", "url"]].rename(
        columns={"position": "you", "volume": "vol_you", "url": "your_url"})
    for name, (_, df) in zip(names, rivals):
        part = df.set_index("keyword")[["position", "volume"]].rename(
            columns={"position": name, "volume": f"vol_{name}"})
        table = table.join(part, how="outer")

    vol_cols = [c for c in table.columns if c.startswith("vol_")]
    table["volume"] = table[vol_cols].max(axis=1).fillna(0)
    table = table.drop(columns=vol_cols).reset_index().rename(columns={"index": "keyword"})

    def classify(row):
        you = None if pd.isna(row["you"]) else row["you"]
        ranks = [row[n] for n in names if not pd.isna(row[n])]
        return gap_type(you, ranks)

    table["gap"] = table.apply(classify, axis=1)
    any_rival = table[names].notna().any(axis=1)
    table["best_competitor"] = table[names].fillna(float("inf")).idxmin(axis=1).where(any_rival, "")
    table["best_competitor_pos"] = table[names].min(axis=1)
    table["competitors_ranking"] = table[names].notna().sum(axis=1)
    table["words"] = table["keyword"].map(length_bucket)
    table["comparison_intent"] = table["keyword"].str.contains(COMPARISON)
    table["revenue_score"] = (table["volume"] * table["words"].map(LENGTH_WEIGHT)).round(1)

    cols = (["keyword", "gap", "volume", "words", "comparison_intent", "revenue_score", "you"] + names
            + ["best_competitor", "best_competitor_pos", "competitors_ranking", "your_url"])
    table = table[cols].sort_values(["revenue_score", "volume"], ascending=False).reset_index(drop=True)
    return table, me, names


def summary(table: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for gap in GAP_ORDER:
        g = table[table["gap"] == gap]
        rows.append({
            "gap": gap,
            "keywords": len(g),
            "total_volume": int(g["volume"].sum()),
            "revenue_score": round(g["revenue_score"].sum()),
            "long_tail_keywords": int((g["words"] != "1-2 words").sum()),
            "comparison_keywords": int(g["comparison_intent"].sum()),
        })
    return pd.DataFrame(rows)


def by_length(table: pd.DataFrame) -> pd.DataFrame:
    """Missing + untapped keywords split by length: where the revenue in your gap sits."""
    gaps = table[table["gap"].isin(["missing", "untapped"])]
    out = gaps.groupby("words").agg(keywords=("keyword", "count"), volume=("volume", "sum"),
                                    revenue_score=("revenue_score", "sum")).reindex(list(LENGTH_WEIGHT)).fillna(0)
    out["share_of_volume_pct"] = (out["volume"] / max(out["volume"].sum(), 1) * 100).round(1)
    out["share_of_revenue_score_pct"] = (out["revenue_score"] / max(out["revenue_score"].sum(), 1) * 100).round(1)
    return out.reset_index().astype({"keywords": int, "volume": int})
