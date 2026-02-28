"""
Google Sheets writer with fallback to CSV
Reuses gspread experience from Fares Korea case
"""
import csv
import logging
from pathlib import Path
from typing import List
from datetime import datetime, timezone

from .config import GOOGLE_SHEETS_CREDENTIALS_PATH, GOOGLE_SHEETS_SPREADSHEET_ID, USE_MOCK_SHEETS, BASE_DIR
from .models import ExtractionResult
from .validate import ValidationResult

logger = logging.getLogger(__name__)

OUTPUT_CSV = BASE_DIR / "output" / "invoices_extracted.csv"
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

class SheetsWriter:
    def __init__(self, credentials_path: str = GOOGLE_SHEETS_CREDENTIALS_PATH, spreadsheet_id: str = GOOGLE_SHEETS_SPREADSHEET_ID):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.use_mock = USE_MOCK_SHEETS
        self.client = None
        
        if not self.use_mock:
            try:
                import gspread
                from google.oauth2.service_account import Credentials
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
                self.client = gspread.authorize(creds)
                logger.info(f"Google Sheets client initialized for {spreadsheet_id}")
            except Exception as e:
                logger.error(f"Failed to init gspread, fallback to CSV: {e}")
                self.use_mock = True
    
    def write_to_csv(self, results: List[tuple[ExtractionResult, ValidationResult]], output_path: Path = OUTPUT_CSV):
        """
        Write to local CSV - mock for portfolio demo without Google Sheets
        """
        fieldnames = [
            "invoice_id", "number", "date", "due_date", "vendor", "client", "currency",
            "subtotal", "tax", "total", "payment_terms",
            "line_items_count", "line_items_json",
            "confidence", "needs_review", "review_reasons",
            "missing_fields", "errors", "warnings",
            "extracted_at", "source_file"
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for extraction, validation in results:
                inv = extraction.invoice
                writer.writerow({
                    "invoice_id": inv.number or "N/A",
                    "number": inv.number,
                    "date": inv.date,
                    "due_date": inv.due_date,
                    "vendor": inv.vendor,
                    "client": inv.client,
                    "currency": inv.currency,
                    "subtotal": inv.subtotal,
                    "tax": inv.tax,
                    "total": inv.total,
                    "payment_terms": inv.payment_terms,
                    "line_items_count": len(inv.line_items),
                    "line_items_json": str([item.model_dump() for item in inv.line_items]),
                    "confidence": extraction.confidence,
                    "needs_review": validation.needs_review,
                    "review_reasons": "; ".join(extraction.review_reasons),
                    "missing_fields": "; ".join(validation.missing_fields),
                    "errors": "; ".join(validation.errors),
                    "warnings": "; ".join(validation.warnings),
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                    "source_file": getattr(extraction, 'source_file', 'unknown')
                })
        
        logger.info(f"Wrote {len(results)} invoices to CSV {output_path}")
        return str(output_path)
    
    def write_to_google_sheets(self, results: List[tuple[ExtractionResult, ValidationResult]]):
        """
        Write to Google Sheets - real implementation
        """
        if self.use_mock:
            return self.write_to_csv(results)
        
        try:
            import gspread
            sheet = self.client.open_by_key(self.spreadsheet_id).sheet1
            
            # Header
            headers = ["Invoice Number", "Date", "Vendor", "Client", "Currency", "Subtotal", "Tax", "Total", "Confidence", "Needs Review", "Review Reasons", "Source File", "Extracted At"]
            # Check if sheet is empty, add header
            if not sheet.get_all_values():
                sheet.append_row(headers)
            
            for extraction, validation in results:
                inv = extraction.invoice
                row = [
                    inv.number or "",
                    inv.date or "",
                    inv.vendor or "",
                    inv.client or "",
                    inv.currency or "",
                    inv.subtotal or "",
                    inv.tax or "",
                    inv.total or "",
                    extraction.confidence,
                    "YES" if validation.needs_review else "NO",
                    "; ".join(extraction.review_reasons),
                    getattr(extraction, 'source_file', ''),
                    datetime.now(timezone.utc).isoformat()
                ]
                sheet.append_row(row)
            
            logger.info(f"Wrote {len(results)} rows to Google Sheets {self.spreadsheet_id}")
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
        
        except Exception as e:
            logger.error(f"Google Sheets write failed, fallback to CSV: {e}")
            return self.write_to_csv(results)
    
    def write(self, results: List[tuple[ExtractionResult, ValidationResult]]):
        if self.use_mock:
            return self.write_to_csv(results)
        else:
            return self.write_to_google_sheets(results)

if __name__ == "__main__":
    # Test CSV writer
    from .models import InvoiceData, ExtractionResult
    from .validate import ValidationResult
    
    extraction = ExtractionResult(
        invoice=InvoiceData(number="INV-001", date="2024-03-15", vendor="Test GmbH", total=100.0, currency="EUR", tax=19.0),
        confidence="high",
        confidence_scores={},
        needs_review=False,
        review_reasons=[]
    )
    validation = ValidationResult(is_valid=True, missing_fields=[], low_confidence_fields=[], errors=[], warnings=[], needs_review=False)
    
    writer = SheetsWriter()
    path = writer.write([(extraction, validation)])
    print(f"Wrote to {path}")
