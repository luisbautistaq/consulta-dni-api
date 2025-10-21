import asyncio
from playwright.async_api import async_playwright

async def consulta_dni(dni: str):
    data = {"dni": dni, "nombres": None, "apellido_paterno": None, "apellido_materno": None, "fecha_nacimiento": None}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()

            # Nombres y apellidos
            await page.goto("https://dniperu.com/buscar-dni-nombres-apellidos/", wait_until="networkidle")
            await page.fill("input[name='dni']", dni)
            await page.click("button[type='submit']")
            await page.wait_for_timeout(2000)
            data["nombres"] = await page.input_value("#nombres") or None
            data["apellido_paterno"] = await page.input_value("#apellidop") or None
            data["apellido_materno"] = await page.input_value("#apellidom") or None

            # Fecha de nacimiento
            await page.goto("https://dniperu.com/fecha-de-nacimiento-con-dni/", wait_until="networkidle")
            await page.fill("input[name='dni']", dni)
            await page.click("button[type='submit']")
            await page.wait_for_timeout(2000)
            data["fecha_nacimiento"] = await page.input_value("#fechanac") or None

            await browser.close()
    except Exception as e:
        print(f"Error en consulta: {e}")
    return data
