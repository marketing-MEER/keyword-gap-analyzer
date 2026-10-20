"""Command line entry point: `keyword-gap-analyzer YOU.csv COMPETITOR.csv [COMPETITOR.csv ...]`."""
from pathlib import Path

import click

from . import __version__, core
from .benchmark import STATS
from .report import Report, write_excel


@click.command()
@click.argument("your_csv", type=click.Path(exists=True))
@click.argument("competitor_csv", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--max-position", default=100, show_default=True, help="Ignore rankings below this position.")
@click.option("-o", "--output", default="keyword_gap", show_default=True,
              help="Report name; writes <name>.html and <name>.xlsx")
@click.version_option(__version__)
def main(your_csv, competitor_csv, max_position, output):
    """Compare YOUR_CSV with 1-5 COMPETITOR_CSV keyword exports and rank the gaps by revenue potential.

    Built by Meer Hamza - linkedin.com/in/meerhamza-seo
    """
    if len(competitor_csv) > 5:
        raise click.BadParameter("use up to 5 competitor files")
    table, me, names = core.analyze(your_csv, competitor_csv, max_position)
    summ = core.summary(table).set_index("gap")
    lengths = core.by_length(table)

    report = Report(title="Keyword gap report", subtitle=f"{me} vs {', '.join(names)}", tool="keyword-gap-analyzer")
    report.add_cards([
        ("Missing keywords", int(summ.at["missing", "keywords"]), "bad"),
        ("Weak keywords", int(summ.at["weak", "keywords"]), "warn"),
        ("Untapped keywords", int(summ.at["untapped", "keywords"]), "warn"),
        ("Shared", int(summ.at["shared", "keywords"])),
        ("Strong", int(summ.at["strong", "keywords"]), "good"),
    ])
    report.add_benchmark(STATS[0], how_used="Each keyword's revenue score is its volume weighted by these revenue "
                                            "shares (1-2 words ≈ 0.1x, 3-6 words 1x, 7+ words ≈ 1.06x).")
    report.add_benchmark(STATS[1], how_used="Keywords with best/top/vs/review/alternative are flagged as "
                                            "comparison intent: build pages with a clear verdict for them.")
    report.add_table("Summary by gap type", summ.reset_index(), sheet="Summary")
    report.add_table("Where the revenue in your gap sits", lengths,
                     note="Missing + untapped keywords split by length.", sheet="Gap by length")
    for gap, note in [
        ("missing", "Two or more competitors rank, you don't. Highest revenue score first."),
        ("untapped", "Exactly one competitor ranks. Often easier wins."),
        ("weak", "You rank, but below every competitor that ranks."),
        ("strong", "You beat every competitor that ranks. Protect these."),
    ]:
        report.add_table(f"{gap.title()} keywords", table[table["gap"] == gap].drop(columns="gap"), note=note, sheet=gap.title())
    report.add_table("All keywords", table, sheet="All keywords")

    html_path = report.save_html(Path(output).with_suffix(".html"))
    xlsx_path = write_excel(report.sheets, Path(output).with_suffix(".xlsx"))
    click.secho(f"Report: {html_path}\nData:   {xlsx_path}", fg="green", bold=True)
    click.echo(summ.to_string())


if __name__ == "__main__":
    main()
