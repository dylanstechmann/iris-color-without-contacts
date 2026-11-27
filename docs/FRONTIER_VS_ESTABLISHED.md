# Frontier versus established

**Date:** 2026-11-27

This boundary applies only to the archived synthetic washout analysis and its
software checks. It does not promote descriptive simulation output into
biological or clinical evidence.

## Established within that limited scope

- The full top-level analysis suite passed **124 tests** on 2026-11-27.
- The read-only paired archived verifier passed: it verified the receipted
  results and report, frozen assumptions, and four runtime sources before
  computing the nested-design comparison.
- The general read-only archived verifier passed for **120 selected artifacts**,
  with analysis scripts matching their receipts. These checks establish the
  tested software behavior and archived file identity, not scientific validity.
- The archived scenarios contain descriptive per-design counts of distinct
  synthetic system/replicate pairs. `observed_pairs`, `absent_pairs`, and
  `observed_outside_match` distinguish pairs present in a design, absent from
  it relative to the union, and present outside the shared three-design
  intersection. `unevaluable_in_one_or_more` separately counts shared pairs
  with an unevaluable fit.
- In each archived scenario, full/reduced/minimal observed 9/4/4 pairs; full
  had 0 absent and 5 outside the shared intersection, while reduced and minimal
  each had 5 absent and 0 outside. Four pairs were shared and evaluable in all
  three designs, and zero shared pairs were unevaluable. The focused synthetic
  fixture separately exercises an unevaluable fit within the shared
  intersection.

## Frontier and not established

- **Scientific interpretation:** the synthetic ratios, proposed cutoffs,
  recovery diagnostics, and design comparisons do not establish a biological
  mechanism, a preferred experimental design, or an iris-color effect.
- **Independence and generalization:** within-system replicates are correlated;
  nested designs reuse observations; and ratio scenarios reuse random streams.
  These records are not independent observations or independent confirmations.
  Counts remain descriptive within one scenario and design. No Wilson intervals,
  pooled-scenario significance tests, inflated sample sizes, donor-population
  inference, or generalization to other systems are supported.
- **Treatment and human outcomes:** treatment efficacy, safety, dosing, and real
  human outcomes—including iris-color change, recovery, and preserved visual
  function—remain unestablished. Nothing here is a treatment instruction or a
  clinical recommendation.

## Update when evidence changes

Revisit this document when new evidence, data, analysis, or independent review
changes these boundaries. Record the date and validation scope, preserve the
distinction between software/archive checks and scientific evidence, and move
an item only when the new evidence directly supports that change.
