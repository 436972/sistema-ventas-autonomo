import requests
import csv
from datetime import datetime

API_KEY = "AIzaSyAmy_1UJJAUHiAkwzfh2y-OXHbWa4AcZnc"

SECTORES = [
    "restaurantes",
    "peluquerias",
    "clinicas dentales",
    "talleres mecanicos",
    "tiendas de ropa"
]

CIUDAD = "Ponferrada"

def buscar_negocios(tipo, ciudad):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.nationalPhoneNumber,places.websiteUri,places.userRatingCount,places.photos"
    }
    data = {"textQuery": f"{tipo} en {ciudad}", "languageCode": "es"}
    response = requests.post(url, headers=headers, json=data)
    return response.json().get("places", [])

def puntuar(negocio):
    score = 0
    detalles = []
    web = negocio.get("websiteUri", "")
    rating = negocio.get("rating", 0)
    resenas = negocio.get("userRatingCount", 0)
    fotos = negocio.get("photos", [])

    if not web:
        score += 40
        detalles.append("Sin web (+40)")
    elif any(r in web for r in ["facebook", "instagram", "jimdosite", "wix", "wordpress.com"]):
        score += 20
        detalles.append("Web precaria (+20)")

    if resenas < 50:
        score += 25
        detalles.append(f"Pocas resenas {resenas} (+25)")
    elif resenas < 200:
        score += 10
        detalles.append(f"Resenas medias {resenas} (+10)")

    if len(fotos) == 0:
        score += 20
        detalles.append("Sin fotos (+20)")

    if rating and rating < 4.0:
        score += 15
        detalles.append(f"Rating bajo {rating} (+15)")
    elif rating and rating < 4.5:
        score += 10
        detalles.append(f"Rating medio {rating} (+10)")
    else:
        score += 5
        detalles.append(f"Buen rating {rating} (+5)")

    return score, detalles

todos = []

for sector in SECTORES:
    print(f"Buscando: {sector}...")
    negocios = buscar_negocios(sector, CIUDAD)
    for n in negocios:
        n["sector"] = sector
    todos.extend(negocios)
    print(f"  -> {len(negocios)} encontrados")

vistos = set()
unicos = []
for n in todos:
    nombre = n.get("displayName", {}).get("text", "")
    if nombre not in vistos:
        vistos.add(nombre)
        unicos.append(n)

unicos.sort(key=lambda n: puntuar(n)[0], reverse=True)

fecha = datetime.now().strftime("%Y%m%d")
filename = f"prospectos_ElBierzo_{fecha}.csv"

with open(filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Puntuacion", "Prioridad", "Sector", "Nombre", "Telefono", "Rating", "Resenas", "Fotos", "Web", "Direccion", "Motivos"])
    for n in unicos:
        score, detalles = puntuar(n)
        prioridad = "ALTA" if score >= 70 else "MEDIA" if score >= 40 else "BAJA"
        writer.writerow([
            score, prioridad,
            n.get("sector", ""),
            n.get("displayName", {}).get("text", ""),
            n.get("nationalPhoneNumber", "Sin telefono"),
            n.get("rating", ""),
            n.get("userRatingCount", 0),
            len(n.get("photos", [])),
            n.get("websiteUri", "Sin web"),
            n.get("formattedAddress", ""),
            " | ".join(detalles)
        ])

alta = sum(1 for n in unicos if puntuar(n)[0] >= 70)
media = sum(1 for n in unicos if 40 <= puntuar(n)[0] < 70)
baja = sum(1 for n in unicos if puntuar(n)[0] < 40)

print(f"\nTotal prospectos unicos: {len(unicos)}")
print(f"ALTA prioridad: {alta}")
print(f"MEDIA prioridad: {media}")
print(f"BAJA prioridad: {baja}")
print(f"\nExportado a: {filename}")
