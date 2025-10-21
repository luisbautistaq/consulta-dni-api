import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor

# =========================
# ✅ Configurar Chrome para Render
# =========================
def iniciar_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Render instala Chrome en esta ruta
    chrome_path = os.getenv("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome")
    options.binary_location = chrome_path

    driver = uc.Chrome(options=options)
    return driver

# =========================
# ✅ Función que consulta en la web
# =========================
def consulta_en_pagina(url, boton_texto, dni, accion):
    try:
        driver = iniciar_driver()
        driver.get(url)
        time.sleep(2)
        input_box = driver.find_element(By.ID, "dni")
        input_box.send_keys(dni)
        driver.find_element(By.XPATH, f"//button[contains(text(),'{boton_texto}')]").click()
        time.sleep(2)

        data = {}
        if accion == "Buscar":
            data["dni"] = dni
            data["nombres"] = driver.find_element(By.ID, "nombres").get_attribute("value")
            data["apellido_paterno"] = driver.find_element(By.ID, "apellidop").get_attribute("value")
            data["apellido_materno"] = driver.find_element(By.ID, "apellidom").get_attribute("value")
        elif accion == "Consultar":
            data["fecha_nacimiento"] = driver.find_element(By.ID, "fechanac").get_attribute("value")

        driver.quit()
        return data
    except Exception as e:
        print("⚠️ Error en consulta:", e)
        return {}

# =========================
# ✅ Función principal
# =========================
def consulta_completa(dni):
    urls = {
        "nombres": ("https://dniperu.com/buscar-dni-nombres-apellidos/", "Buscar"),
        "fecha": ("https://dniperu.com/fecha-de-nacimiento-con-dni/", "Consultar")
    }

    print(f"🧠 Consultando información completa para DNI {dni}...")

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="DNI") as executor:
        fut_n = executor.submit(consulta_en_pagina, urls["nombres"][0], urls["nombres"][1], dni, "Buscar")
        fut_f = executor.submit(consulta_en_pagina, urls["fecha"][0], urls["fecha"][1], dni, "Consultar")

        data_nombres = fut_n.result() or {}
        data_fecha = fut_f.result() or {}

    result = {}
    for k in ("dni", "nombres", "apellido_paterno", "apellido_materno", "fecha_nacimiento"):
        result[k] = data_nombres.get(k) or data_fecha.get(k) or None

    return result
