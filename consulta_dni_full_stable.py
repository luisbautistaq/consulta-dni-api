# consulta_dni_full_stable.py
import asyncio
import os
import json
import logging
from typing import Dict, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# logging básico (Render muestra stdout/stderr en logs)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("consulta_dni")

# Config
NAV_WAIT = "networkidle"      # "networkidle" o "load"
NAV_TIMEOUT = 15000          # ms
RETRY_ATTEMPTS = 2
RETRY_DELAY = 1.5            # segundos
LAUNCH_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--disable-blink-features=AutomationControlled"
]
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

async def _consulta_playwright(dni: str) -> Dict[str, Optional[str]]:
    data = {"dni": None, "nombres": None, "apellido_paterno": None, "apellido_materno": None, "fecha_nacimiento": None}
    try:
        logger.info("Iniciando Playwright para DNI %s", dni)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=LAUNCH_ARGS)
            context = await browser.new_context(
                user_agent=USER_AGENT,
                locale="es-PE",
                viewport={"width": 1280, "height": 800},
                java_script_enabled=True,
            )
            page = await context.new_page()

            # ---- Consulta nombres/apellidos ----
            try:
                url_nombres = "https://dniperu.com/buscar-dni-nombres-apellidos/"
                logger.info("Cargando página nombres: %s", url_nombres)
                await page.goto(url_nombres, wait_until=NAV_WAIT, timeout=NAV_TIMEOUT)
                # Esperar input DNI
                await page.wait_for_selector("input#dni, input[name*='dni'], input[placeholder*='DNI']", timeout=8000)
                # rellenar
                await page.fill("input#dni, input[name*='dni'], input[placeholder*='DNI']", dni)
                # clickar botón (intenta varios selectores)
                await page.click("button[type='submit'], button:has-text('Buscar'), button:has-text('buscar')", timeout=4000)
                # esperar que carguen campos de resultado
                await page.wait_for_timeout(1200)
                # intentos de leer por varios selectores
                def _eval_selector(sel):
                    return f"document.querySelector('{sel}') ? (document.querySelector('{sel}').value || document.querySelector('{sel}').innerText || '') : ''"
                nombres = await page.evaluate(_eval_selector("#nombres, input#nombres, #nombre, input[name='nombres']"))
                ap1 = await page.evaluate(_eval_selector("#apellidop, input#apellidop, input[name='apellido_paterno']"))
                ap2 = await page.evaluate(_eval_selector("#apellidom, input#apellidom, input[name='apellido_materno']"))
                data["dni"] = dni
                data["nombres"] = nombres.strip() or None
                data["apellido_paterno"] = ap1.strip() or None
                data["apellido_materno"] = ap2.strip() or None
                logger.info("Nombres obtenidos: %s", data["nombres"])
            except PlaywrightTimeoutError as te:
                logger.warning("Timeout/No pudo obtener nombres: %s", te)
            except Exception as e:
                logger.exception("Error leyendo nombres: %s", e)

            # ---- Consulta fecha de nacimiento ----
            try:
                url_fecha = "https://dniperu.com/fecha-de-nacimiento-con-dni/"
                logger.info("Cargando página fecha: %s", url_fecha)
                await page.goto(url_fecha, wait_until=NAV_WAIT, timeout=NAV_TIMEOUT)
                await page.wait_for_selector("input#dni, input[name*='dni']", timeout=8000)
                await page.fill("input#dni, input[name*='dni']", dni)
                await page.click("button[type='submit'], button:has-text('Consultar'), button:has-text('consultar')", timeout=4000)
                await page.wait_for_timeout(1200)
                fecha = await page.evaluate("document.querySelector('#fechanac') ? (document.querySelector('#fechanac').value || '') : (document.querySelector('.fecha') ? document.querySelector('.fecha').innerText : '')")
                data["fecha_nacimiento"] = (fecha or "").strip() or None
                logger.info("Fecha obtenida: %s", data["fecha_nacimiento"])
            except PlaywrightTimeoutError as te:
                logger.warning("Timeout/No pudo obtener fecha: %s", te)
            except Exception as e:
                logger.exception("Error leyendo fecha: %s", e)

            await context.close()
            await browser.close()
            return data
    except Exception as e:
        logger.exception("Error en _consulta_playwright: %s", e)
        return data

def consulta_completa(dni: str) -> Dict[str, Optional[str]]:
    """Wrapper síncrono que realiza retries y timeouts"""
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            result = asyncio.get_event_loop().run_until_complete(_consulta_playwright(dni))
            # si al menos un campo trae valor consideramos éxito parcial
            if any([result.get("nombres"), result.get("fecha_nacimiento")]):
                return result
            else:
                logger.warning("Intento %d: no se obtuvo info, reintentando...", attempt)
        except Exception as e:
            logger.exception("Intento %d falló: %s", attempt, e)
        if attempt < RETRY_ATTEMPTS:
            asyncio.sleep(RETRY_DELAY)
    # si falló todo, devuelve dict con None
    return {"dni": dni, "nombres": None, "apellido_paterno": None, "apellido_materno": None, "fecha_nacimiento": None}
