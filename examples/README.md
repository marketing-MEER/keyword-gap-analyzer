# 📂 Sample data

Three **made-up** organic keyword exports for a fictional CRM market:

| File | Format | Site |
|---|---|---|
| `brightcrm_keywords.csv` | Ahrefs style (`Keyword`, `Volume`, `Current position`, `Current URL`) | brightcrm.io ("you") |
| `pipelinehq_keywords.csv` | Semrush style (`Keyword`, `Position`, `Search Volume`, `URL`) | pipelinehq.com |
| `salesdeck_keywords.csv` | Ahrefs style | salesdeck.io |

The sites and rankings are fictional. Keywords that mention real products are only search terms.

```bash
keyword-gap-analyzer examples/brightcrm_keywords.csv examples/pipelinehq_keywords.csv examples/salesdeck_keywords.csv
```
