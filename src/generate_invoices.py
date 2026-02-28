"""
Generate 8 synthetic invoices as images + PDFs + ground truth JSON
No real personal/financial data - all fictional

Includes 1 intentionally low quality invoice for review flag test
"""
import json
import random
from pathlib import Path
from datetime import date, timedelta
from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "demo-data" / "invoices"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Try to load a font, fallback to default
def get_font(size=20):
    try:
        # Try common fonts
        for font_path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]:
            if Path(font_path).exists():
                return ImageFont.truetype(font_path, size)
    except:
        pass
    return ImageFont.load_default()

INVOICES = [
    {
        "id": "invoice_001",
        "number": "INV-2024-001",
        "date": "2024-03-15",
        "due_date": "2024-04-15",
        "vendor": "Tech Solutions GmbH",
        "vendor_address": "Berliner Str. 123, 10115 Berlin, Germany",
        "client": "Anna Schmidt, Berlin Startup Hub",
        "currency": "EUR",
        "subtotal": 2500.00,
        "tax": 475.00,
        "total": 2975.00,
        "payment_terms": "Net 30",
        "line_items": [
            {"description": "Website Development - Frontend", "quantity": 1, "unit_price": 1500.00, "amount": 1500.00},
            {"description": "API Integration", "quantity": 1, "unit_price": 1000.00, "amount": 1000.00}
        ],
        "notes": "Thank you for your business!",
        "format": "EU standard, comma decimal in image but dot in JSON ground truth"
    },
    {
        "id": "invoice_002",
        "number": "INV-US-2024-042",
        "date": "2024-05-20",
        "due_date": "2024-06-20",
        "vendor": "Digital Agency NYC Inc.",
        "vendor_address": "123 Broadway, New York, NY 10001, USA",
        "client": "David Kim, Marketing Agency NY",
        "currency": "USD",
        "subtotal": 5000.00,
        "tax": 0.00,
        "total": 5000.00,
        "payment_terms": "Due on receipt",
        "line_items": [
            {"description": "AI Automation Setup", "quantity": 1, "unit_price": 3000.00, "amount": 3000.00},
            {"description": "WhatsApp Bot Development", "quantity": 1, "unit_price": 2000.00, "amount": 2000.00}
        ],
        "notes": "Payment via wire transfer",
        "format": "US format, dot decimal, $ symbol"
    },
    {
        "id": "invoice_003",
        "number": "INV-UK-2024-015",
        "date": "2024-02-10",
        "due_date": "2024-03-10",
        "vendor": "London Creative Studio Ltd",
        "vendor_address": "45 Oxford Street, London W1D 2DZ, UK",
        "client": "Mark Johnson, Dental Clinic UK",
        "currency": "GBP",
        "subtotal": 1200.00,
        "tax": 240.00,
        "total": 1440.00,
        "payment_terms": "Net 14",
        "line_items": [
            {"description": "Logo Design", "quantity": 1, "unit_price": 500.00, "amount": 500.00},
            {"description": "Brand Guidelines", "quantity": 1, "unit_price": 700.00, "amount": 700.00}
        ],
        "notes": "VAT 20% included",
        "format": "UK format, GBP"
    },
    {
        "id": "invoice_004",
        "number": "INV-2024-078",
        "date": "2024-07-01",
        "due_date": "2024-07-31",
        "vendor": "E-commerce Solutions OÜ",
        "vendor_address": "Narva mnt 5, 10117 Tallinn, Estonia",
        "client": "Elena Petrova, Ecom Store",
        "currency": "EUR",
        "subtotal": 890.00,
        "tax": 178.00,
        "total": 1068.00,
        "payment_terms": "Net 30",
        "line_items": [
            {"description": "Wildberries Price Monitor Setup", "quantity": 1, "unit_price": 400.00, "amount": 400.00},
            {"description": "Monthly Monitoring (3 months)", "quantity": 3, "unit_price": 100.00, "amount": 300.00},
            {"description": "Telegram Alerts Integration", "quantity": 1, "unit_price": 190.00, "amount": 190.00}
        ],
        "notes": "Includes 3 months support",
        "format": "Multiple line items, EU"
    },
    {
        "id": "invoice_005",
        "number": "INV-2024-102",
        "date": "2024-08-12",
        "due_date": "2024-09-12",
        "vendor": "Wellness Tech Berlin",
        "vendor_address": "Friedrichstr. 123, 10117 Berlin, Germany",
        "client": "Linda Müller, Wellness Berlin",
        "currency": "EUR",
        "subtotal": 3000.00,
        "tax": 570.00,
        "total": 3570.00,
        "payment_terms": "50% upfront, 50% on delivery",
        "line_items": [
            {"description": "WhatsApp Booking Bot", "quantity": 1, "unit_price": 3000.00, "amount": 3000.00}
        ],
        "notes": "VAT 19% - German rate",
        "format": "EU with VAT 19%"
    },
    {
        "id": "invoice_006",
        "number": "INV-RU-2024-033",
        "date": "2024-04-05",
        "due_date": "2024-05-05",
        "vendor": "ООО Ромашка",
        "vendor_address": "ул. Тверская 10, Москва, Россия",
        "client": "ИП Иванов, Магазин на WB",
        "currency": "RUB",
        "subtotal": 50000.00,
        "tax": 10000.00,
        "total": 60000.00,
        "payment_terms": "Предоплата 100%",
        "line_items": [
            {"description": "Настройка мониторинга цен WB", "quantity": 1, "unit_price": 30000.00, "amount": 30000.00},
            {"description": "Интеграция с Google Sheets", "quantity": 1, "unit_price": 20000.00, "amount": 20000.00}
        ],
        "notes": "НДС 20%",
        "format": "RUB, Russian vendor"
    },
    {
        "id": "invoice_007_low_quality",
        "number": "INV-2024-099",
        "date": "2024-09-01",
        "due_date": None,
        "vendor": "Blurry Scans Ltd",
        "vendor_address": None,
        "client": "Test Client",
        "currency": "EUR",
        "subtotal": None,  # Intentionally unclear
        "tax": None,
        "total": None,  # Low quality - should be flagged for review, not guessed
        "payment_terms": None,
        "line_items": [
            {"description": "Consulting Services - unreadable", "quantity": 1, "unit_price": 0, "amount": 0}
        ],
        "notes": "Low quality scan - intentionally blurry, total amount not readable",
        "format": "LOW QUALITY - should trigger needs_review, not hallucinate total",
        "low_quality": True
    },
    {
        "id": "invoice_008",
        "number": "INV-2024-115",
        "date": "2024-09-20",
        "due_date": "2024-10-20",
        "vendor": "AI Automation Specialists",
        "vendor_address": "Telliskivi 60, 10412 Tallinn, Estonia",
        "client": "Sophie Laurent, Salon Paris",
        "currency": "EUR",
        "subtotal": 4500.00,
        "tax": 900.00,
        "total": 5400.00,
        "payment_terms": "Net 30",
        "line_items": [
            {"description": "CRM Integration + Lead Qualification", "quantity": 1, "unit_price": 2500.00, "amount": 2500.00},
            {"description": "Eval Harness Setup", "quantity": 1, "unit_price": 1500.00, "amount": 1500.00},
            {"description": "Documentation & Training", "quantity": 1, "unit_price": 500.00, "amount": 500.00}
        ],
        "notes": "Project 5 & 6 from portfolio",
        "format": "EU, multiple items, references portfolio projects"
    }
]

def create_invoice_image(invoice_data, output_path, low_quality=False):
    # Create image 800x1000 white background
    width, height = 800, 1100
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(24)
    font_normal = get_font(16)
    font_small = get_font(12)
    
    y = 20
    
    # Title
    draw.text((20, y), "INVOICE", font=font_title, fill='black')
    y += 40
    
    # Invoice details
    draw.text((20, y), f"Invoice Number: {invoice_data.get('number', 'N/A')}", font=font_normal, fill='black')
    y += 25
    draw.text((20, y), f"Date: {invoice_data.get('date', 'N/A')}", font=font_normal, fill='black')
    y += 25
    if invoice_data.get('due_date'):
        draw.text((20, y), f"Due Date: {invoice_data['due_date']}", font=font_normal, fill='black')
        y += 25
    
    y += 10
    draw.line((20, y, width-20, y), fill='gray', width=1)
    y += 15
    
    # Vendor
    draw.text((20, y), "From:", font=font_normal, fill='black')
    y += 20
    draw.text((20, y), f"{invoice_data.get('vendor', 'N/A')}", font=font_normal, fill='black')
    y += 20
    if invoice_data.get('vendor_address'):
        # Wrap address
        addr = invoice_data['vendor_address']
        draw.text((20, y), addr[:60], font=font_small, fill='black')
        y += 15
        if len(addr) > 60:
            draw.text((20, y), addr[60:120], font=font_small, fill='black')
            y += 15
    
    y += 10
    # Client
    draw.text((20, y), "Bill To:", font=font_normal, fill='black')
    y += 20
    draw.text((20, y), f"{invoice_data.get('client', 'N/A')}", font=font_normal, fill='black')
    y += 30
    
    draw.line((20, y, width-20, y), fill='gray', width=1)
    y += 15
    
    # Line items header
    draw.text((20, y), "Description", font=font_normal, fill='black')
    draw.text((400, y), "Qty", font=font_normal, fill='black')
    draw.text((500, y), "Unit Price", font=font_normal, fill='black')
    draw.text((650, y), "Amount", font=font_normal, fill='black')
    y += 20
    draw.line((20, y, width-20, y), fill='gray', width=1)
    y += 10
    
    # Line items
    for item in invoice_data.get('line_items', []):
        desc = item.get('description', '')[:40]
        qty = str(item.get('quantity', ''))
        unit = f"{item.get('unit_price', 0):.2f}"
        amount = f"{item.get('amount', 0):.2f}"
        
        draw.text((20, y), desc, font=font_small, fill='black')
        draw.text((400, y), qty, font=font_small, fill='black')
        draw.text((500, y), unit, font=font_small, fill='black')
        draw.text((650, y), amount, font=font_small, fill='black')
        y += 20
        if y > height - 150:
            break
    
    y += 10
    draw.line((20, y, width-20, y), fill='gray', width=1)
    y += 15
    
    # Totals
    currency = invoice_data.get('currency', 'EUR')
    # Format with comma for EU style for some invoices
    use_comma = invoice_data['id'] in ['invoice_001', 'invoice_005']  # EU comma style
    
    def format_amount(val):
        if val is None:
            return "N/A - unreadable" if low_quality else "N/A"
        if use_comma:
            # EU style: 2.975,00
            return f"{val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') + f" {currency}"
        else:
            return f"{val:,.2f} {currency}"
    
    if invoice_data.get('subtotal') is not None:
        draw.text((500, y), f"Subtotal: {format_amount(invoice_data['subtotal'])}", font=font_normal, fill='black')
        y += 25
    if invoice_data.get('tax') is not None:
        draw.text((500, y), f"Tax: {format_amount(invoice_data['tax'])}", font=font_normal, fill='black')
        y += 25
    
    # Total - make it bold-ish
    total_text = f"TOTAL: {format_amount(invoice_data.get('total'))}"
    if low_quality:
        # Make total blurry/unreadable for low quality test
        draw.text((500, y), "TOTAL: [UNREADABLE - BLURRY SCAN]", font=font_normal, fill='gray')
    else:
        draw.text((500, y), total_text, font=font_title, fill='black')
    y += 35
    
    if invoice_data.get('payment_terms'):
        draw.text((20, y), f"Payment Terms: {invoice_data['payment_terms']}", font=font_small, fill='black')
        y += 20
    
    if invoice_data.get('notes'):
        draw.text((20, y), f"Notes: {invoice_data['notes'][:70]}", font=font_small, fill='black')
        y += 20
    
    # If low quality, add blur effect by drawing semi-transparent overlay and noise
    if low_quality:
        # Add noise
        for _ in range(500):
            x = random.randint(0, width-1)
            y_noise = random.randint(0, height-1)
            draw.point((x, y_noise), fill=(random.randint(150,200), random.randint(150,200), random.randint(150,200)))
        # Add blur text
        draw.text((20, height-50), "!!! LOW QUALITY SCAN - REQUIRES MANUAL REVIEW !!!", font=font_normal, fill='red')
    
    img.save(output_path)
    print(f"Created {output_path} (low_quality={low_quality})")

def main():
    all_ground_truth = []
    
    for inv in INVOICES:
        inv_id = inv["id"]
        low_quality = inv.get("low_quality", False)
        
        # Save ground truth JSON
        json_path = OUTPUT_DIR / f"{inv_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(inv, f, indent=2, ensure_ascii=False)
        
        # Create image
        img_path = OUTPUT_DIR / f"{inv_id}.png"
        create_invoice_image(inv, img_path, low_quality=low_quality)
        
        # Create simple text version as well (for OCR fallback)
        txt_path = OUTPUT_DIR / f"{inv_id}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"INVOICE\n")
            f.write(f"Number: {inv.get('number')}\n")
            f.write(f"Date: {inv.get('date')}\n")
            f.write(f"Vendor: {inv.get('vendor')}\n")
            f.write(f"Client: {inv.get('client')}\n")
            f.write(f"Currency: {inv.get('currency')}\n")
            f.write(f"Total: {inv.get('total')}\n")
            f.write(f"Tax: {inv.get('tax')}\n")
            for item in inv.get('line_items', []):
                f.write(f"Item: {item['description']} Qty:{item['quantity']} Price:{item['unit_price']} Amount:{item['amount']}\n")
        
        all_ground_truth.append(inv)
    
    # Save combined ground truth
    combined_path = OUTPUT_DIR.parent / "ground_truth.json"
    with open(combined_path, 'w', encoding='utf-8') as f:
        json.dump(all_ground_truth, f, indent=2, ensure_ascii=False)
    
    print(f"\nGenerated {len(INVOICES)} invoices in {OUTPUT_DIR}")
    print(f"Ground truth combined: {combined_path}")
    print(f"Includes 1 low quality invoice (invoice_007_low_quality) for review flag test")

if __name__ == "__main__":
    main()
