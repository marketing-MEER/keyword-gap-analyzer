<div align="center">

# 🕳️ keyword-gap-analyzer

### Find the keywords your competitors win and you don't, ranked by revenue potential, not just volume.

[![tests](https://github.com/marketing-MEER/keyword-gap-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/marketing-MEER/keyword-gap-analyzer/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![No API keys](https://img.shields.io/badge/API%20keys-none%20needed-brightgreen)
[![Part of SEO Toolbox](https://img.shields.io/badge/part%20of-SEO%20Toolbox-orange)](https://github.com/marketing-MEER/seo-toolbox)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meer%20Hamza-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)

[🚀 Quick start](#quick-start) · [⚙️ How it works](#how-it-works) · [📄 Report](#report) · [❓ FAQ](#faq) · [👤 Author](#author)

</div>

---

## 💡 What it does

A keyword gap analysis compares your rankings with your competitors' and shows where they win and you don't. Most tools sort that list by search volume, so it fills up with short head terms that are hard to win and rarely convert.

`keyword-gap-analyzer` takes your keyword export plus up to 5 competitor exports and puts every keyword into one gap type. It then **sorts by revenue potential**: volume weighted by how much revenue keywords of that length actually drive.

- ✅ Five gap types: **missing**, **untapped**, **weak**, **shared**, **strong**
- ✅ A revenue score based on published lead data, plus a flag for comparison-intent keywords ("best", "vs", "alternatives")
- ✅ Shows where the revenue in your gap sits: short head terms vs long-tail
- ✅ Free, MIT licensed, no API keys. Works with Ahrefs, Semrush or GSC exports

## 📊 Why this matters

> **Which Keywords Actually Drive Revenue** · NP Digital, January 2024 (579,240 leads)
> - Keywords with 1 to 2 words drive 4.76 percent of revenue.
> - Keywords with 3 to 6 words generate 46.29 percent of revenue.
> - Keywords with 7 or more words drive 48.95 percent of revenue.
>
> **Top And Best Keywords Drive Higher Conversion** · NP Digital, December 2023
> - Keywords containing top or best converted at 1.08% in 2022, rising to 1.66% in 2023.
>
> Data: [revenue by keyword length](https://neilpatel.com/marketing-stats/keywords-that-drive-revenue/) · [top/best keywords](https://neilpatel.com/marketing-stats/conversion-rate-keywords-containing-top-or-best/)

**How keyword-gap-analyzer uses this:** the insights say to *"reduce emphasis on ranking for short head terms"* and *"align SEO KPIs with revenue contribution, not traffic."* So every keyword's **revenue score = volume × the revenue share of its length group**, normalised to the 3–6 word group: 1–2 words ≈ 0.1×, 3–6 words 1×, 7+ words ≈ 1.06×. Keywords with comparison modifiers are flagged, because the second stat shows they convert better and need pages with a clear verdict.

<a id="quick-start"></a>

## 🚀 Quick start

```bash
git clone https://github.com/marketing-MEER/keyword-gap-analyzer.git
cd keyword-gap-analyzer
pip install -e .
keyword-gap-analyzer examples/brightcrm_keywords.csv examples/pipelinehq_keywords.csv examples/salesdeck_keywords.csv
```

The first file is **you**; the rest (1 to 5) are competitors. This writes **`keyword_gap.html`** (a formatted report you can share or print to PDF) and **`keyword_gap.xlsx`** (all data, one sheet per gap type).

> [!TIP]
> If the `keyword-gap-analyzer` command isn't found, use `python -m keyword_gap_analyzer`.

## 📥 Input

One organic keywords export per site. The keyword, position, volume and URL columns are detected automatically:

| Source | How to export | Columns detected |
|---|---|---|
| Ahrefs | Site Explorer → Organic keywords → Export | `Keyword`, `Current position`, `Volume`, `Current URL` |
| Semrush | Organic Research → Positions → Export | `Keyword`, `Position`, `Search Volume`, `URL` |
| Google Search Console (your site only) | Performance → Queries → Export | `Top queries`, `Position`, `Impressions` (used as volume) |

Each site is named from the domain in its URLs, or from the file name if there are no URLs.

<a id="how-it-works"></a>

## ⚙️ How it works

1. **Load and clean**: keep each keyword's best position per site, and ignore rankings below `--max-position` (default 100).
2. **Join** all sites on the keyword, keeping the highest volume seen.
3. **Gap type** for every keyword:

| Gap type | Rule | What to do |
|---|---|---|
| 🔴 **missing** | You don't rank; 2+ competitors do | Proven demand: create a page |
| 🟠 **untapped** | You don't rank; exactly 1 competitor does | Often easier wins |
| 🟡 **weak** | You rank, but below every competitor that ranks | Improve or consolidate the page |
| ⚪ **shared** | You rank between competitors | Push toward the top 3 |
| 🟢 **strong** | You beat every competitor that ranks | Protect and update |

4. **Revenue score** = volume × length weight (from the NP revenue shares above).
5. **Comparison intent** = the keyword contains *best, top, vs, versus, review(s), alternative(s), compare, comparison*.
6. **Sort** by revenue score, then volume.

### Options

| Option | Default | What it does |
|---|---|---|
| `--max-position` | `100` | Ignore rankings below this position |
| `-o`, `--output` | `keyword_gap` | Report name; writes `.html` and `.xlsx` |

<a id="report"></a>

## 📄 The report

| Section / Excel sheet | Shows |
|---|---|
| Summary cards | Number of keywords in each gap type |
| Benchmark panels | The two Neil Patel stats behind the scoring |
| **Summary** | Per gap type: keywords, volume, revenue score, long-tail count, comparison keywords |
| **Gap by length** | Missing + untapped keywords split into 1–2 / 3–6 / 7+ words: share of volume vs share of revenue score |
| **Missing / Untapped / Weak / Strong** | One table each: keyword, volume, length, comparison flag, revenue score, every site's position, the best competitor |
| **All keywords** | Everything in one sheet for your own filters |

<details>
<summary>📄 Example: real output from <code>examples/</code> (fictional CRM sites)</summary>

**Summary**

| gap | keywords | total volume | revenue score | long-tail keywords | comparison keywords |
|---|---|---|---|---|---|
| missing | 8 | 28,590 | 17,589 | 5 | 4 |
| weak | 2 | 7,190 | 7,190 | 2 | 0 |
| untapped | 14 | 239,910 | 45,789 | 9 | 2 |
| shared | 1 | 720 | 761 | 1 | 0 |
| strong | 10 | 16,950 | 16,977 | 10 | 5 |

**Where the revenue in the gap sits.** Short head terms are 85% of the gap's volume but only 37% of its revenue potential:

| words | keywords | volume | revenue score | share of volume % | share of revenue score % |
|---|---|---|---|---|---|
| 1-2 words | 8 | 228,700 | 23,517 | 85.2 | 37.1 |
| 3-6 words | 11 | 38,750 | 38,750 | 14.4 | 61.1 |
| 7+ words | 3 | 1,050 | 1,110 | 0.4 | 1.8 |

**Missing keywords** (top 5). "free crm" has the 2nd-highest volume but drops to 5th by revenue score:

| keyword | volume | words | comparison | revenue score | pipelinehq.com | salesdeck.io |
|---|---|---|---|---|---|---|
| crm for small business | 9,900 | 3-6 words | | 9,900 | 7 | 7 |
| pipedrive vs hubspot | 2,900 | 3-6 words | ✓ | 2,900 | 6 | 2 |
| sales pipeline software | 1,900 | 3-6 words | | 1,900 | 48 | 67 |
| salesforce alternatives for small business | 1,000 | 3-6 words | ✓ | 1,000 | 4 | 11 |
| free crm | 8,100 | 1-2 words | | 833 | 23 | 5 |

</details>

## 🧰 More free SEO tools

This repo is one tool in the **[SEO Toolbox](https://github.com/marketing-MEER/seo-toolbox)**, a family of free, single-purpose SEO tools. Related:
- [serp-competitor-finder](https://github.com/marketing-MEER/serp-competitor-finder): find who you really compete with, by share of voice
- **long-tail-revenue-scorer**: score any keyword list by revenue potential
- [seo-workhorse](https://github.com/marketing-MEER/seo-workhorse): audit, clustering, redirects and GSC quick wins in one CLI

<a id="faq"></a>

## ❓ FAQ

<details><summary><b>Isn't a 1–2 word keyword with huge volume still worth chasing?</b></summary>

Sometimes, and the volume column is still there. The revenue score just stops it from crowding out everything else. In the source data, 1–2 word keywords drove under 5% of revenue.
</details>

<details><summary><b>Which competitors should I compare against?</b></summary>

Your *search* competitors, not just business rivals. Run [serp-competitor-finder](https://github.com/marketing-MEER/serp-competitor-finder) first to find the domains with the most share of voice on your keywords.
</details>

<details><summary><b>Can I use my GSC export as "you"?</b></summary>

Yes. Export Performance → Queries; impressions stand in for volume. Use Ahrefs/Semrush exports for competitors, because GSC only shows your own site.
</details>

<details><summary><b>Is my data sent anywhere?</b></summary>

No. It reads your CSV files and writes the report on your computer. It makes no network requests.
</details>

## 🧪 Tests

```bash
python -m unittest discover -s tests -t . -v
```

## 📄 License

[MIT](LICENSE). Free for personal and commercial use. Benchmark figures © their original publishers, quoted with a link to the source.

<a id="author"></a>

## 👤 Author

**Meer Hamza** · SEO Team Lead · Berlin 🇩🇪
10+ years in SEO, AEO and GEO. I build small tools that take the spreadsheet work out of SEO.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)
[![Email](https://img.shields.io/badge/Email-meerhamza5%40gmail.com-D14836?logo=gmail&logoColor=white)](mailto:meerhamza5@gmail.com)

<div align="center">

**If this saved you time, a ⭐ helps other SEOs find it.**

</div>
