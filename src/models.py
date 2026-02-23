"""
Pydantic schemas for invoice extraction - structured output
Forces model to return valid JSON, not text
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import date

class LineItem(BaseModel):
    description: str = Field(description="Description of item/service")
    quantity: float = Field(description="Quantity")
    unit_price: float = Field(description="Unit price")
    amount: float = Field(description="Line total amount (quantity * unit_price)")

class InvoiceData(BaseModel):
    number: Optional[str] = Field(default=None, description="Invoice number, e.g., INV-2024-001. Null if not found, DO NOT hallucinate.")
    date: Optional[str] = Field(default=None, description="Invoice date in YYYY-MM-DD format. Null if not found.")
    due_date: Optional[str] = Field(default=None, description="Due date in YYYY-MM-DD, null if not mentioned")
    vendor: Optional[str] = Field(default=None, description="Vendor/supplier company name. Null if not found.")
    vendor_address: Optional[str] = Field(default=None, description="Vendor address, null if not mentioned")
    client: Optional[str] = Field(default=None, description="Client/customer name, null if not mentioned")
    total: Optional[float] = Field(default=None, description="Total amount including tax. Null if not confidently readable - DO NOT guess.")
    tax: Optional[float] = Field(default=None, description="Tax/VAT amount. Null if not mentioned or not readable.")
    currency: Optional[str] = Field(default=None, description="Currency code: EUR, USD, GBP, RUB, etc. Null if not mentioned.")
    subtotal: Optional[float] = Field(default=None, description="Subtotal before tax, null if not mentioned")
    line_items: List[LineItem] = Field(default_factory=list, description="List of line items, empty if not found")
    payment_terms: Optional[str] = Field(default=None, description="Payment terms, null if not mentioned")
    notes: Optional[str] = Field(default=None, description="Additional notes")

class ExtractionResult(BaseModel):
    invoice: InvoiceData
    confidence: Literal["high", "medium", "low"] = Field(description="Overall confidence")
    confidence_scores: dict = Field(default_factory=dict, description="Confidence per field: high/medium/low")
    needs_review: bool = Field(description="True if needs human review due to low confidence")
    review_reasons: List[str] = Field(default_factory=list, description="Reasons for review")
    raw_text: Optional[str] = Field(default=None, description="Raw OCR text if available")
    source_file: Optional[str] = Field(default=None, description="Source file path")

class ValidationResult(BaseModel):
    is_valid: bool
    missing_fields: List[str] = Field(default_factory=list)
    low_confidence_fields: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    needs_review: bool
