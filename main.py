import os
import time
import pathlib
from datetime import datetime


PROPERTY = {
    "address": "Carrer de la Diputacio, 245, 3o 2a",
    "city": "Barcelona",
    "province": "Barcelona",
    "postal_code": "08007",
    "cadastral_ref": "7823014DF3872C0001WX",
    "surface": "65,00",
    "bedrooms": 2,
    "bathrooms": 1,
    "floor": "3a",
    "energy_rating": "C",
    "energy_cert_num": "ECE-2023-00456",
    "energy_cert_expiry": "15/09/2033",
    "habitability_num": "CH-BCN-2022-09812",
    "habitability_expiry": "20/11/2032",
    "monthly_rent": "950,00",
    "deposit": "950,00",
}


def prompt(label, required=True):
    while True:
        value = input("  " + label + ": ").strip()
        if value or not required:
            return value
        print("  This field is required. Please enter a value.")


def collect_inputs():
    print()
    print("=" * 55)
    print("   RENTOO - Contract Generator")
    print("=" * 55)

    print("\n OWNER DETAILS")
    print("-" * 40)
    owner = {
        "name": prompt("Full name"),
        "dni": prompt("DNI / NIE / TIE"),
        "address": prompt("Street address"),
        "city": prompt("City"),
        "province": prompt("Province"),
        "postal_code": prompt("Postal code"),
    }

    print("\n TENANT DETAILS")
    print("-" * 40)
    tenant = {
        "name": prompt("Full name"),
        "dni": prompt("DNI / NIE / TIE"),
        "address": prompt("Street address"),
        "phone": prompt("WhatsApp phone number (e.g. +34612345678)"),
    }

    print("\n CONTRACT DATES")
    print("-" * 40)
    start_date = prompt("Start date (DD/MM/YYYY)")
    end_date = prompt("End date (DD/MM/YYYY)")

    return {
        "owner": owner,
        "tenant": tenant,
        "start_date": start_date,
        "end_date": end_date,
    }


def make_pdf(line_tuples, filename):
    PAGE_W = 595
    PAGE_H = 842
    MARGIN_LEFT = 70
    MARGIN_RIGHT = 70
    MAX_Y = PAGE_H - 70
    MIN_Y = 70
    BASE_LINE_H = 15

    pages_content = []
    current_lines = []
    y = MAX_Y

    for item in line_tuples:
        if item[0] == "__PAGEBREAK__":
            pages_content.append(current_lines[:])
            current_lines.clear()
            y = MAX_Y
            continue

        text, size, bold = item
        line_h = BASE_LINE_H + (3 if size > 10 else 0)

        if y < MIN_Y:
            pages_content.append(current_lines[:])
            current_lines.clear()
            y = MAX_Y

        current_lines.append((text, size, bold, y))
        y -= line_h

    if current_lines:
        pages_content.append(current_lines[:])

    objects = []
    objects.append(None)
    objects.append(None)

    page_obj_ids = []

    for page_lines in pages_content:
        stream_parts = ["BT"]
        prev_y = None

        for (text, size, bold, y_pos) in page_lines:
            font = "F2" if bold else "F1"
            safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            stream_parts.append("/" + font + " " + str(size) + " Tf")
            stream_parts.append(str(MARGIN_LEFT) + " " + str(y_pos) + " Td")
            stream_parts.append("(" + safe + ") Tj")
            line_h = BASE_LINE_H + (3 if size > 10 else 0)
            stream_parts.append("-" + str(MARGIN_LEFT) + " -" + str(line_h) + " Td")

        stream_parts.append("ET")
        stream = "\n".join(stream_parts).encode("latin-1", errors="replace")

        content_id = len(objects) + 1
        objects.append(
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )

        page_id = len(objects) + 1
        objects.append(
            (
                "<< /Type /Page /Parent 2 0 R "
                "/MediaBox [0 0 " + str(PAGE_W) + " " + str(PAGE_H) + "] "
                "/Contents " + str(content_id) + " 0 R "
                "/Resources << /Font << "
                "/F1 << /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >> "
                "/F2 << /Type /Font /Subtype /Type1 /BaseFont /Times-Bold >> "
                ">> >> >>"
            ).encode()
        )
        page_obj_ids.append(page_id)

    kids = " ".join(str(i) + " 0 R" for i in page_obj_ids)
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = (
        "<< /Type /Pages /Kids [" + kids + "] /Count " + str(len(page_obj_ids)) + " >>"
    ).encode()

    buf = bytearray()
    buf += b"%PDF-1.4\n"
    offsets = []

    for i, obj in enumerate(objects):
        offsets.append(len(buf))
        buf += (str(i + 1) + " 0 obj\n").encode()
        buf += obj
        buf += b"\nendobj\n"

    xref_offset = len(buf)
    buf += b"xref\n"
    buf += ("0 " + str(len(objects) + 1) + "\n").encode()
    buf += b"0000000000 65535 f \n"
    for off in offsets:
        buf += (str(off).zfill(10) + " 00000 n \n").encode()

    buf += b"trailer\n"
    buf += ("<< /Size " + str(len(objects) + 1) + " /Root 1 0 R >>\n").encode()
    buf += b"startxref\n"
    buf += (str(xref_offset) + "\n").encode()
    buf += b"%%EOF\n"

    with open(filename, "wb") as f:
        f.write(buf)


def build_contract_lines(data):
    p = PROPERTY
    o = data["owner"]
    t = data["tenant"]
    start = data["start_date"]
    end = data["end_date"]

    def body(text):
        return (text, 10, False)

    def heading(text):
        return (text, 11, True)

    def title(text):
        return (text, 14, True)

    def subtitle(text):
        return (text, 9, False)

    def blank():
        return ("", 10, False)

    def bold(text):
        return (text, 10, True)

    def clause(text):
        return (text, 10, True)

    lines = []

    lines.append(blank())
    lines.append(title("CONTRATO DE ARRENDAMIENTO DE VIVIENDA"))
    lines.append(subtitle("Ley 29/1994, de 24 de noviembre, de Arrendamientos Urbanos (LAU)"))
    lines.append(blank())

    lines.append(heading("REUNIDOS"))
    lines.append(body("De una parte, " + o["name"] + ", mayor de edad, con DNI/NIE/TIE"))
    lines.append(body("numero " + o["dni"] + ", con domicilio en " + o["address"] + ","))
    lines.append(body(o["city"] + ", " + o["postal_code"] + ", " + o["province"] + ","))
    lines.append(body("en su condicion de ARRENDADOR."))
    lines.append(blank())
    lines.append(body("Y de otra parte, " + t["name"] + ", mayor de edad, con DNI/NIE/TIE"))
    lines.append(body("numero " + t["dni"] + ", con domicilio en " + t["address"] + ","))
    lines.append(body("en su condicion de ARRENDATARIO."))
    lines.append(blank())
    lines.append(body("Ambas partes se reconocen mutuamente capacidad legal suficiente para"))
    lines.append(body("formalizar el presente contrato y, a tal efecto,"))
    lines.append(blank())

    lines.append(heading("EXPONEN"))
    lines.append(body("PRIMERO. Que el ARRENDADOR es propietario de la vivienda sita en"))
    lines.append(body(p["address"] + ", " + p["city"] + ", " + p["postal_code"] + ", " + p["province"] + ","))
    lines.append(body("ref. catastral " + p["cadastral_ref"] + ", superficie " + p["surface"] + " m2,"))
    lines.append(body(str(p["bedrooms"]) + " habitaciones, " + str(p["bathrooms"]) + " bano, planta " + p["floor"] + "."))
    lines.append(blank())
    lines.append(body("SEGUNDO. Certificado de Eficiencia Energetica: calificacion " + p["energy_rating"] + ","))
    lines.append(body("num. " + p["energy_cert_num"] + ", caduca " + p["energy_cert_expiry"] + "."))
    lines.append(body("Cedula de Habitabilidad num. " + p["habitability_num"] + ", caduca " + p["habitability_expiry"] + "."))
    lines.append(blank())
    lines.append(body("TERCERO. Es voluntad de ambas partes formalizar el arrendamiento de"))
    lines.append(body("la vivienda descrita para uso de vivienda habitual, conforme a las siguientes"))
    lines.append(blank())

    lines.append(heading("ESTIPULACIONES"))
    lines.append(blank())

    lines.append(clause("PRIMERA.- OBJETO Y DURACION DEL CONTRATO"))
    lines.append(body("El ARRENDADOR arrienda al ARRENDATARIO la vivienda descrita para uso"))
    lines.append(body("exclusivo como vivienda habitual. Duracion: UN ANYO, desde el " + start))
    lines.append(body("hasta el " + end + ". El contrato se prorrogara por plazos anuales"))
    lines.append(body("hasta alcanzar cinco anyos, salvo que el arrendatario notifique lo contrario"))
    lines.append(body("con treinta dias de antelacion."))
    lines.append(blank())

    lines.append(clause("SEGUNDA.- DESTINO DE LA VIVIENDA"))
    lines.append(body("La vivienda se destinara exclusivamente a satisfacer la necesidad permanente"))
    lines.append(body("de vivienda del arrendatario. Queda prohibido el subarrendamiento total o"))
    lines.append(body("parcial sin consentimiento expreso y por escrito del arrendador."))
    lines.append(blank())

    lines.append(clause("TERCERA.- RENTA"))
    lines.append(body("El arrendatario se obliga a pagar " + p["monthly_rent"] + " EUR mensuales,"))
    lines.append(body("dentro de los primeros siete dias de cada mes."))
    lines.append(blank())

    lines.append(clause("CUARTA.- FIANZA"))
    lines.append(body("El arrendatario entrega en concepto de fianza legal " + p["deposit"] + " EUR,"))
    lines.append(body("equivalente a una mensualidad de renta. La fianza sera depositada por el"))
    lines.append(body("arrendador en el organismo autonomico competente."))
    lines.append(blank())

    lines.append(clause("QUINTA.- GASTOS Y SUMINISTROS"))
    lines.append(body("A cargo del arrendatario: suministros individuales (agua, luz, gas, internet)."))
    lines.append(body("A cargo del arrendador: IBI, gastos de comunidad, reparaciones estructurales."))
    lines.append(blank())

    lines.append(clause("SEXTA.- OBRAS Y REPARACIONES"))
    lines.append(body("El arrendatario realizara las pequenyas reparaciones por desgaste ordinario."))
    lines.append(body("Las reparaciones de habitabilidad son a cargo del arrendador."))
    lines.append(blank())

    lines.append(clause("SEPTIMA.- CONSERVACION Y USO"))
    lines.append(body("El arrendatario se obliga a utilizar la vivienda con diligencia y a"))
    lines.append(body("mantenerla en buen estado de conservacion."))
    lines.append(blank())

    lines.append(clause("OCTAVA.- RESOLUCION DEL CONTRATO"))
    lines.append(body("Causas de resolucion: impago de renta o fianza, danyos dolosamente"))
    lines.append(body("causados, uso indebido de la vivienda, subarrendamiento no autorizado."))
    lines.append(blank())

    lines.append(clause("NOVENA.- NOTIFICACIONES"))
    lines.append(body("Las notificaciones se realizaran en los domicilios del encabezamiento,"))
    lines.append(body("salvo comunicacion fehaciente de cambio de domicilio."))
    lines.append(blank())

    lines.append(clause("DECIMA.- LEGISLACION APLICABLE Y JURISDICCION"))
    lines.append(body("Este contrato se rige por la Ley 29/1994 de Arrendamientos Urbanos."))
    lines.append(body("Las partes se someten a los Juzgados y Tribunales de " + p["city"] + "."))
    lines.append(blank())

    lines.append(("__PAGEBREAK__", 0, False))

    lines.append(heading("FIRMAS"))
    lines.append(blank())
    lines.append(body("En " + p["city"] + ", a " + start + "."))
    lines.append(blank())
    lines.append(blank())
    lines.append(blank())

    lines.append(body("EL ARRENDADOR                              EL ARRENDATARIO"))
    lines.append(blank())
    lines.append(blank())
    lines.append(blank())
    lines.append(blank())
    lines.append(blank())
    lines.append(body("_____________________________              _____________________________"))
    lines.append(body(o["name"] + "              " + t["name"]))
    lines.append(body("DNI: " + o["dni"] + "              DNI: " + t["dni"]))

    return lines


def send_via_whatsapp(phone, pdf_path):
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("\n  selenium not installed.")
        print("  Run: pip install selenium")
        return

    abs_pdf_path = os.path.abspath(pdf_path)
    # Remove + and spaces from phone number for the URL
    clean_phone = phone.replace("+", "").replace(" ", "")
    url = "https://web.whatsapp.com/send?phone=" + clean_phone

    print("\n Opening WhatsApp Web in Chrome...")
    print("  Scan the QR code if prompted (first time only).")

    options = Options()
    options.add_argument("--start-maximized")
    session_dir = str(pathlib.Path("./whatsapp_session").resolve())
    options.add_argument(f"--user-data-dir={session_dir}")
    # Prevent Chrome from flagging automation
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 90)  # 90s gives time for QR scan
        print("  Waiting for chat to load (up to 90s — scan QR if prompted)...")

        # Wait for the chat input box — confirms the chat is open and ready
        time.sleep(8)  # Let WhatsApp Web fully initialize after QR scan
        # Try multiple selectors for the chat input box
        chat_input_selectors = [
            '//div[@data-testid="conversation-compose-box-input"]',
            '//div[@contenteditable="true"][@data-tab="10"]',
            '//div[@contenteditable="true"][@data-tab="1"]',
            '//div[@contenteditable="true"][contains(@class,"selectable-text")]',
            '//footer//div[@contenteditable="true"]',
        ]
        chat_loaded = False
        for selector in chat_input_selectors:
            try:
                wait.until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                chat_loaded = True
                break
            except Exception:
                continue
        if not chat_loaded:
            raise Exception("Chat input not found — WhatsApp Web may not have loaded the conversation.")
        # print("  DEBUG: Chat input found!")
        time.sleep(3) # Let the page fully settle

        # print("  DEBUG: Looking for attach button...")  

        # --- Attach button (current WhatsApp Web uses a "+" / clip icon) ---
        # Try multiple known selectors — WhatsApp changes these periodically
        attach_selectors = [
            '//span[@data-testid="plus-rounded"]',
            '//span[@data-icon="plus-rounded"]',
            '//button[@title="Attach"]',
            '//div[@title="Attach"]',
            '//span[@data-icon="attach-menu-plus"]',
            '//span[@data-icon="clip"]',
        ]

        attach_btn = None
        for selector in attach_selectors:
            try:
                attach_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                break
            except Exception:
                continue

        if not attach_btn:
            raise Exception("Could not find the Attach button.")
        # print("  DEBUG: Attach button found! Clicking...")
        attach_btn.click()
        time.sleep(1.5)
        # print("  DEBUG: Attach button clicked, clicking Document option...")

        # Click the Document option from the attach menu
        document_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Document"]'))
        )
        document_btn.click()
        time.sleep(2)
        # print("  DEBUG: Document clicked, looking for file input...")

        # --- File input: appears after clicking attach ---
        # WhatsApp renders hidden file inputs — send_keys works without clicking
        file_input_selectors = [
            '//input[@accept="*"]',
            '//input[@type="file"]',
            '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]/../../..//input[@type="file"]',
        ]

        doc_input = None
        for selector in file_input_selectors:
            try:
                # Use presence_of, not clickable — file inputs are often invisible
                doc_input = driver.find_element(By.XPATH, selector)
                break
            except Exception:
                continue

        if not doc_input:
            raise Exception("Could not find the file input element.")

        doc_input.send_keys(abs_pdf_path)
        time.sleep(4)  # Wait for upload preview to appear

        # --- Send button ---
        # send_selectors = [
        #     '//span[@data-icon="send"]',
        #     '//button[@aria-label="Send"]',
        #     '//div[@aria-label="Send"]',
        # ]
        send_selectors = [
            '//span[@data-testid="wds-ic-send-filled"]',
            '//div[@aria-label="Send 1 selected"]',
            '//span[@data-icon="send"]',
            '//button[@aria-label="Send"]',
            '//div[@aria-label="Send"]',
        ]

        send_btn = None
        for selector in send_selectors:
            try:
                send_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                break
            except Exception:
                continue

        if not send_btn:
            raise Exception("Could not find the Send button after file upload.")

        send_btn.click()
        print("\n  Contract sent successfully to " + phone + "!")
        time.sleep(4)

    except Exception as e:
        print("\n  WhatsApp sending failed: " + str(e))
        print("  Your PDF was generated: " + pdf_path)
        print("  You can send it manually.")

    finally:
        driver.quit()


def main():
    data = collect_inputs()

    tenant_slug = data["tenant"]["name"].replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = "contrato_" + tenant_slug + "_" + timestamp + ".pdf"

    print("\n Generating contract PDF: " + pdf_filename)
    lines = build_contract_lines(data)
    make_pdf(lines, pdf_filename)
    print("  PDF created successfully.")

    print("\n Send PDF to " + data["tenant"]["name"] + " (" + data["tenant"]["phone"] + ") via WhatsApp?")
    confirm = input("  Type 'yes' to send, or press Enter to skip: ").strip().lower()

    if confirm == "yes":
        send_via_whatsapp(data["tenant"]["phone"], pdf_filename)
    else:
        print("\n  WhatsApp sending skipped.")
        print("  PDF saved as: " + pdf_filename)

    print("\n Done!\n")


main()