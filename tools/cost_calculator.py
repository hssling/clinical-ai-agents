"""What would this actually cost us? -- the calculator behind the cost slide.

Run:  python cost_calculator.py
      python cost_calculator.py --inr-per-usd 88 --budget-in 0.10 --budget-out 0.40

Answers the question every HOD asks after an AI talk, in rupees, with the
assumptions visible instead of buried.

Costs are shown as a RANGE across two model tiers, because "what does AI cost"
has no single answer -- it depends entirely on which model you point it at, and
that is a choice you make per use case.

Prices change. Override the rates at the command line rather than trusting
numbers printed months ago.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

# Rough word-to-token ratio for English clinical text.
TOKENS_PER_WORD = 1.35


@dataclass
class Scenario:
    name: str
    runs_per_month: int
    input_words: int
    output_words: int
    note: str


SCENARIOS = [
    Scenario("Guideline Q&A — one department", 2_000, 900, 150,
             "Question plus retrieved guideline sections in, short cited answer out"),
    Scenario("Guideline Q&A — whole hospital", 20_000, 900, 150,
             "Same, at ten times the volume"),
    Scenario("Discharge summaries — one ward", 600, 700, 450,
             "Ward notes in, structured summary out"),
    Scenario("Discharge summaries — whole hospital", 10_000, 700, 450,
             "Every discharge, every ward"),
    Scenario("Abstract screening — 5,000 abstracts", 5_000, 350, 40,
             "One systematic review, one-off — not monthly"),
    Scenario("Triage support — one PHC", 3_000, 400, 120,
             "Multi-turn, so counted as ~3 calls per case"),
]


def cost_inr(runs: int, in_words: int, out_words: int,
             in_rate: float, out_rate: float, fx: float) -> float:
    """Cost in rupees. Rates are USD per million tokens."""
    in_tokens = runs * in_words * TOKENS_PER_WORD
    out_tokens = runs * out_words * TOKENS_PER_WORD
    usd = (in_tokens / 1_000_000) * in_rate + (out_tokens / 1_000_000) * out_rate
    return usd * fx


def _rupees(amount: float) -> str:
    return "<Rs 1" if amount < 1 else f"Rs {amount:,.0f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--budget-in", type=float, default=0.10,
                        help="Budget model: USD per million INPUT tokens (default 0.10)")
    parser.add_argument("--budget-out", type=float, default=0.40,
                        help="Budget model: USD per million OUTPUT tokens (default 0.40)")
    parser.add_argument("--premium-in", type=float, default=1.25,
                        help="Premium model: USD per million INPUT tokens (default 1.25)")
    parser.add_argument("--premium-out", type=float, default=5.00,
                        help="Premium model: USD per million OUTPUT tokens (default 5.00)")
    parser.add_argument("--inr-per-usd", type=float, default=88.0,
                        help="Exchange rate (default 88)")
    parser.add_argument("--free-tier", type=int, default=1_500,
                        help="Free requests per day (default 1500)")
    args = parser.parse_args()

    free_monthly = args.free_tier * 30

    print("\n  WHAT WOULD THIS COST US?")
    print("  " + "=" * 84)
    print(f"  Budget model:   ${args.budget_in}/M in, ${args.budget_out}/M out"
          "     (Gemini Flash / GPT-mini tier)")
    print(f"  Premium model:  ${args.premium_in}/M in, ${args.premium_out}/M out"
          "     (frontier tier)")
    print(f"  Exchange rate:  Rs {args.inr_per_usd:.0f} = $1"
          f"   |   Free tier: {free_monthly:,} calls/month")
    print("  " + "=" * 84)
    print(f"\n  {'Scenario':<40}{'Runs/mo':>9}{'Budget':>12}{'Premium':>12}{'Free?':>8}")
    print("  " + "-" * 84)

    for s in SCENARIOS:
        low = cost_inr(s.runs_per_month, s.input_words, s.output_words,
                       args.budget_in, args.budget_out, args.inr_per_usd)
        high = cost_inr(s.runs_per_month, s.input_words, s.output_words,
                        args.premium_in, args.premium_out, args.inr_per_usd)
        fits = "yes" if s.runs_per_month <= free_monthly else "no"
        print(f"  {s.name:<40}{s.runs_per_month:>9,}"
              f"{_rupees(low):>12}{_rupees(high):>12}{fits:>8}")
        print(f"      {s.note}")

    print("  " + "-" * 84)
    print("""
  ABOUT THAT "Free?" COLUMN -- read this before quoting it

    "Fits the free tier" means the VOLUME fits. It does not mean you should
    run a clinical service on a free tier. Free tiers carry per-minute rate
    limits, no uptime guarantee, no data-processing agreement, and terms that
    often permit the provider to train on your inputs.

    Free tier is for prototyping. The moment real users depend on it, pay.
    The paid figures above are what that actually costs -- which is the point.

  WHAT THIS DOES NOT INCLUDE -- and these are the real costs

    * Staff time to build, test and validate           (the largest single cost)
    * Clinical time to review outputs                  (ongoing, forever)
    * Governance: ethics approval, audit, review       (before launch, then annually)
    * Hosting, if you self-host inside hospital IT
    * Re-validation whenever the model or the guideline changes

  The model bill is almost never why a clinical AI project fails. Budget for
  the five lines above and the arithmetic here becomes a rounding error.
""")


if __name__ == "__main__":
    main()
