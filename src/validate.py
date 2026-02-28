"""
Validation - check required fields, flag low confidence for manual review
Anti-hallucination guardrail: don't silently use wrong numbers
"""
from typing import List
from .models import ExtractionResult, ValidationResult

REQUIRED_FIELDS = ["number", "date", "vendor", "total", "currency"]

def validate_extraction(result: ExtractionResult) -> ValidationResult:
    invoice = result.invoice
    missing = []
    low_conf = []
    errors = []
    warnings = []
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        value = getattr(invoice, field, None)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    
    # Check confidence scores
    for field, conf in result.confidence_scores.items():
        if conf == "low":
            low_conf.append(field)
    
    # Specific validations
    # Total should be >= tax if both present
    if invoice.total is not None and invoice.tax is not None:
        if invoice.total < invoice.tax:
            errors.append(f"Total {invoice.total} less than tax {invoice.tax} - likely extraction error")
    
    # Date format check (should be YYYY-MM-DD)
    if invoice.date:
        try:
            # Simple check: should contain - and year 2020-2030
            if len(invoice.date) != 10 or invoice.date[4] != '-' or invoice.date[7] != '-':
                warnings.append(f"Date format unusual: {invoice.date}, expected YYYY-MM-DD")
        except:
            warnings.append(f"Date parsing issue: {invoice.date}")
    
    # Currency check
    valid_currencies = ["EUR", "USD", "GBP", "RUB", "CAD", "AUD"]
    if invoice.currency and invoice.currency not in valid_currencies:
        warnings.append(f"Unusual currency: {invoice.currency}, expected one of {valid_currencies}")
    
    # Line items sum check
    if invoice.line_items and invoice.subtotal is not None:
        line_sum = sum(item.amount for item in invoice.line_items)
        # Allow small rounding diff
        if abs(line_sum - invoice.subtotal) > 0.05:
            warnings.append(f"Line items sum {line_sum} != subtotal {invoice.subtotal}")
    
    # Low quality handling
    needs_review = result.needs_review or len(missing) > 0 or len(low_conf) > 0 or len(errors) > 0
    
    if result.confidence == "low":
        needs_review = True
    
    # If total is None, definitely needs review (anti-hallucination)
    if invoice.total is None:
        needs_review = True
        if "total" not in missing:
            missing.append("total")
        warnings.append("Total is null - low quality scan, requires manual review instead of guessing")
    
    is_valid = len(missing) == 0 and len(errors) == 0 and not needs_review
    
    return ValidationResult(
        is_valid=is_valid,
        missing_fields=missing,
        low_confidence_fields=low_conf,
        errors=errors,
        warnings=warnings,
        needs_review=needs_review
    )

def format_validation_report(result: ExtractionResult, validation: ValidationResult) -> str:
    lines = []
    lines.append(f"Invoice: {result.invoice.number or 'N/A'}")
    lines.append(f"Vendor: {result.invoice.vendor or 'N/A'}")
    lines.append(f"Total: {result.invoice.total} {result.invoice.currency or ''}")
    lines.append(f"Confidence: {result.confidence}")
    lines.append(f"Needs Review: {validation.needs_review}")
    if validation.missing_fields:
        lines.append(f"Missing: {', '.join(validation.missing_fields)}")
    if validation.low_confidence_fields:
        lines.append(f"Low confidence: {', '.join(validation.low_confidence_fields)}")
    if validation.errors:
        lines.append(f"Errors: {'; '.join(validation.errors)}")
    if validation.warnings:
        lines.append(f"Warnings: {'; '.join(validation.warnings)}")
    if result.review_reasons:
        lines.append(f"Review reasons: {'; '.join(result.review_reasons)}")
    return "\n".join(lines)

if __name__ == "__main__":
    # Test validation
    from .models import InvoiceData, ExtractionResult
    
    # Good invoice
    good = ExtractionResult(
        invoice=InvoiceData(number="INV-001", date="2024-03-15", vendor="Test GmbH", total=100.0, currency="EUR"),
        confidence="high",
        confidence_scores={},
        needs_review=False,
        review_reasons=[]
    )
    print("Good invoice validation:")
    print(validate_extraction(good))
    
    # Low quality
    bad = ExtractionResult(
        invoice=InvoiceData(number="INV-099", date="2024-09-01", vendor="Blurry Ltd", total=None, currency="EUR"),
        confidence="low",
        confidence_scores={"total": "low"},
        needs_review=True,
        review_reasons=["Total not readable"]
    )
    print("\nLow quality validation:")
    print(validate_extraction(bad))
