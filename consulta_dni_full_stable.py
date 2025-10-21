#!/usr/bin/env python3
# consulta_dni_full_stable.py

import time
import re
import gzip
import brotli
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

# Instala el driver automáticamente
chromedriver_autoinstaller.install()


def decode_body(raw_bytes, headers):
    """Decodifica posibles respuestas comprimidas."""
    encoding = None
    for k, v in headers.items():
        if k.lower() == "content-encoding":
            encoding = v.lower()
            break
    try:
        if encoding == "br":
            return brotli.decompress(raw_bytes).decode("utf-8", errors="ignore")
        if encoding in ("gzip", "x-gzip"):
            return gzip.decompress(raw_bytes).decode("utf-8", errors="ignore")
        return raw_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return raw_bytes.decode("latin1", errors="ignore")


def clean_value(s: str) -> str:
    if not s:
        return None
    s = str(s).strip()
    s = re.sub(r'(?i)(nombres?:?|apellidos?:?|apellido\s*(paterno|materno)?:?)', '', s)
    s = s.replace("\n", " ").strip()
    s = re.sub(r'(?i)(te puede interesar.*|consulta.*aquí.*|haz clic.*)$', '', s).strip()
    if len(s) <= 1:
        return None
    return s


def parse_fields_from_text(text):
    out = {"dni": None, "nombres": None, "apellido_paterno": None,
           "apellido_materno": None, "fecha_nacimiento": None}
    if not text:
        return out

    text = re.sub(r'\r', '\n', text)
    if m := re.search(r'\b(\d{8})\b', text):
        out["dni"] = m.group(1)
    if m := re.search(r'(?mi)(?:Nombres|Nombre)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑ\s\-]+)', text):
        val = clean_value(m.group(1))
        if val and not re.search(r"(nombres y apellidos|en línea|perú|consulta|busca)", val.lower()):
            out["nombres"] = val
    if m := re.search(r'(?mi)Apellido Paterno\s*[:\-]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ \-]+)', text):
        out["apellido_paterno"] = clean_value(m.group(1))
    if m := re.search(r'(?mi)Apellido Materno\s*[:\-]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ \-]+)', text):
        out["apellido_materno"] = clean_value(m.group(1))
    if m := re.search(r'(?mi)(\d{2}\/\d{2}\/\d{4})', text):
        out["fecha_nacimiento"] = m.group(1).strip()
    return out


def consulta_en_pagina(url, dni, boton_texto, headless=True, timeout_ajax=6):
    chrome_opts = Options()
    if headless:
        chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--disable-extensions")
    chrome_opts.add_argument("--disable-software-rasterizer")
    chrome_opts.add_argument("--renderer-process-limit=2")
    chrome_opts.add_argument("--single-process")
    chrome_opts.add_argument("--no-zygote")
    chrome_opts.add_argument("--disable-logging")
    chrome_opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/141.0 Safari/537.36")
    chrome_opts.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=chrome_opts)

    try:
        driver.get(url)
        input_box = WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//input[@type='text' or @name='dni' or @name='dni4']"))
        )
        input_box.clear()
        input_box.send_keys(dni)
        button = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{boton_texto}')]"))
        )
        driver.execute_script("arguments[0].click();", button)
        result_div = WebDriverWait(driver, timeout_ajax).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(., 'Datos de la Persona') or contains(., 'Información para el DNI')]"
            ))
        )
        parsed = parse_fields_from_text(result_div.text)
        driver.quit()
        return parsed
    except Exception as e:
        try:
            driver.quit()
        except Exception:
            pass
        print("⚠️ Error en consulta:", e)
        return {}


def consulta_completa(dni):
    urls = {
        "nombres": ("https://dniperu.com/buscar-dni-nombres-apellidos/", "Buscar"),
        "fecha": ("https://dniperu.com/fecha-de-nacimiento-con-dni/", "Consultar")
    }

    print(f"🔍 Consultando información completa para DNI {dni}...")
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="DNI") as executor:
        fut_n = executor.submit(consulta_en_pagina, urls["nombres"][0], dni, urls["nombres"][1])
        fut_f = executor.submit(consulta_en_pagina, urls["fecha"][0], dni, urls["fecha"][1])
        data_nombres = fut_n.result() or {}
        data_fecha = fut_f.result() or {}

    result = {}
    for k in ("dni", "nombres", "apellido_paterno", "apellido_materno", "fecha_nacimiento"):
        result[k] = data_nombres.get(k) or data_fecha.get(k) or None

    return result
