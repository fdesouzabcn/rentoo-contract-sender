# Rentoo Contract Sender

A Python terminal application that generates a Spanish rental contract (LAU format) as a PDF and sends it to the tenant via WhatsApp Web.

Built as a final project for [Code in Place 2026](https://codeinplace.stanford.edu/) (Stanford University).

---

## What it does

1. Prompts you for owner details, tenant details, and contract dates
2. Generates a Spanish rental contract as a PDF, structured following LAU (Ley 29/1994 de Arrendamientos Urbanos)
3. Optionally sends the PDF to the tenant's phone via WhatsApp Web automation

**The PDF generator uses zero external libraries** — it writes raw PDF binary using only Python's standard library.


---

## Project Context

This project was inspired by another project, a larger rental property management system, I'm building as part of my Fullstack PHP bootcamp. The contract-generation logic (PDF structure and content) was adapted and simplified from that project to fit this standalone Python script.

**The core focus of this Code in Place submission is the WhatsApp Web automation** (the `send_via_whatsapp` function) — this is the part that was built, tested, and debugged specifically for this final project.

Because the contract generation was reused/simplified rather than being the main focus, the input fields (owner name, ID/DNI, addresses, etc.) **do not include validation**. Any text can be entered in any field. This was an intentional scope decision to prioritize getting the WhatsApp automation working end-to-end within the project deadline.

---

## Setup

### Requirements
- Python 3.10+
- Google Chrome installed
- A WhatsApp account (for sending)

### Install dependencies

```bash
pip install -r requirements.txt
```

The only dependency is `selenium`, used for the WhatsApp Web automation step. Selenium 4+ manages the ChromeDriver automatically — no separate driver download needed.

---

## Usage

```bash
python main.py
```

The script will prompt you for:
- **Owner:** name, DNI/NIE, address
- **Tenant:** name, DNI/NIE, address, WhatsApp phone number (e.g. `+34612345678`)
- **Contract dates:** start and end (DD/MM/YYYY format)

A PDF named `contrato_<tenant_name>_<timestamp>.pdf` will be created in the current directory.

### WhatsApp sending

When prompted to send via WhatsApp:
- A Chrome window opens with WhatsApp Web, taking you directly to the tenant's chat
- **First run:** scan the QR code with your phone to log in
- **Subsequent runs:** the session is cached in `./whatsapp_session/`, so no QR scan is needed
- The script clicks the attach button, selects "Document", attaches the generated PDF, and sends it automatically

If sending fails (e.g. WhatsApp Web's layout has changed), the PDF is still saved locally and can be sent manually.

---

## Project structure
'''
rentoo-contract-sender/
├── main.py            # All application logic
├── requirements.txt   # Python dependencies
└── README.md          # This file
'''

---

## Technical notes

- Property data is hardcoded as a sample Barcelona address for demonstration purposes
- The PDF is generated from scratch using the raw PDF 1.4 specification (no reportlab or other PDF libraries)
- WhatsApp automation uses Selenium with multiple fallback selectors for each UI element, since WhatsApp Web's interface changes periodically
- A persistent Chrome profile (`whatsapp_session/`) avoids repeated QR code scans

---

## Author

Flavio de Souza — Code in Place 2026, Stanford
[github.com/fdesouzabcn](https://github.com/fdesouzabcn)