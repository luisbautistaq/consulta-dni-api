import asyncio
from pyppeteer import launch

async def consulta_dni_async(dni):
    data = {}
    try:
        print(f"🔍 Consultando DNI: {dni}")

        browser = await launch(
            headless=True,
            executablePath="/usr/bin/chromium",
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080"
            ]
        )
        page = await browser.newPage()
        await page.goto("https://dniperu.com/buscar-dni-nombres-apellidos/", {"waitUntil": "networkidle2"})

        await page.type("#dni", dni)
        await page.click("button[type='submit']")
        await page.waitForSelector("#nombres", {"timeout": 8000})

        data["dni"] = dni
        data["nombres"] = await page.evaluate("document.querySelector('#nombres')?.value || ''")
        data["apellido_paterno"] = await page.evaluate("document.querySelector('#apellidop')?.value || ''")
        data["apellido_materno"] = await page.evaluate("document.querySelector('#apellidom')?.value || ''")

        await page.goto("https://dniperu.com/fecha-de-nacimiento-con-dni/", {"waitUntil": "networkidle2"})
        await page.type("#dni", dni)
        await page.click("button[type='submit']")
        await page.waitForSelector("#fechanac", {"timeout": 8000})
        data["fecha_nacimiento"] = await page.evaluate("document.querySelector('#fechanac')?.value || ''")

        await browser.close()
        print(f"✅ Datos obtenidos: {data}")
        return data

    except Exception as e:
        print(f"⚠️ Error en consulta: {e}")
        return {}

def consulta_completa(dni):
    return asyncio.get_event_loop().run_until_complete(consulta_dni_async(dni))
