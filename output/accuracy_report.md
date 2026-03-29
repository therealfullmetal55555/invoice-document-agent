# Invoice Agent Accuracy Report

**Date:** 2026-09-29T10:11:24.098063
**Total invoices:** 8 (including 1 low quality)
**Overall accuracy:** 98.6%

## Per-Field Accuracy (required by brief)

| Field | Correct | Total | Accuracy |
|-------|---------|-------|----------|
| number | 8 | 8 | 100.0% |
| date | 8 | 8 | 100.0% |
| vendor | 8 | 8 | 100.0% |
| total | 8 | 8 | 100.0% |
| tax | 8 | 8 | 100.0% |
| currency | 8 | 8 | 100.0% |
| subtotal | 8 | 8 | 100.0% |
| line_items | 7 | 8 | 87.5% |

## Low Quality Handling

- invoice_007_low_quality: total=None, needs_review=True, confidence=low - ✅ Correct

## Anti-hallucination

No hallucinations - null used when not readable, not guessed
