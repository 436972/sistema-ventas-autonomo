import os
import json
import anthropic
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEMOS_DIR = os.path.expanduser("~/sistema-ventas-autonomo/demos")
os.makedirs(DEMOS_DIR, exist_ok=True)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

COLORES = {
    "restaurante": {"primario": "#2C1810", "secundario": "#8B4513", "acento": "#D4A853", "fondo": "#FDF6EC"},
    "peluqueria":  {"primario": "#1a1a2e", "secundario": "#16213e", "acento": "#e94560", "fondo": "#f8f8f8"},
    "clinica dental": {"primario": "#0a2342", "secundario": "#1a4a7a", "acento": "#00b4d8", "fondo": "#f0f8ff"},
    "taller mecanico": {"primario": "#1c1c1c", "secundario": "#2d2d2d", "acento": "#ff6b35", "fondo": "#f5f5f5"},
    "tiendas de ropa": {"primario": "#1a1a1a", "secundario": "#333333", "acento": "#c9a96e", "fondo": "#fafafa"},
}

FOTOS_UNSPLASH = {
    "restaurante": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80",
    "peluqueria": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1200&q=80",
    "clinica dental": "https://images.unsplash.com/photo-1629909615957-be38d48fbbe4?w=1200&q=80",
    "taller mecanico": "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?w=1200&q=80",
    "tiendas de ropa": "https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?w=1200&q=80",
}

def get_colores(sector):
    for key in COLORES:
        if key in sector.lower():
            return COLORES[key], FOTOS_UNSPLASH.get(key, FOTOS_UNSPLASH["restaurante"])
    return COLORES["restaurante"], FOTOS_UNSPLASH["restaurante"]

def generar_contenido(nombre, sector, telefono, direccion, rating, resenas):
    print(f"  Generando contenido con IA...")
    prompt = f"""Eres un copywriter experto en marketing local español.
Para el negocio "{nombre}" ({sector}) en Ponferrada, El Bierzo, genera exactamente este JSON:

{{
  "eslogan": "frase corta y atractiva (máx 8 palabras)",
  "descripcion_hero": "texto persuasivo de 2 frases que invite a visitar (máx 25 palabras)",
  "descripcion_experiencia": "párrafo de 3-4 frases describiendo la experiencia emocional del lugar",
  "servicios": [
    {{"icono": "emoji", "titulo": "nombre servicio", "descripcion": "descripción corta 1 frase"}},
    {{"icono": "emoji", "titulo": "nombre servicio", "descripcion": "descripción corta 1 frase"}},
    {{"icono": "emoji", "titulo": "nombre servicio", "descripcion": "descripción corta 1 frase"}},
    {{"icono": "emoji", "titulo": "nombre servicio", "descripcion": "descripción corta 1 frase"}}
  ],
  "resenas": [
    {{"autor": "nombre español", "texto": "reseña positiva realista (2 frases)", "estrellas": 5}},
    {{"autor": "nombre español", "texto": "reseña positiva realista (2 frases)", "estrellas": 5}},
    {{"autor": "nombre español", "texto": "reseña positiva realista (2 frases)", "estrellas": 4}}
  ],
  "horarios": "horario realista para este tipo de negocio",
  "frase_final": "frase CTA emotiva corta",
  "meta_description": "meta description SEO local de 155 caracteres máximo"
}}

Devuelve SOLO el JSON, sin explicaciones."""

    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    texto = msg.content[0].text.strip()
    if "```" in texto:
        texto = texto.split("```json")[-1].split("```")[0].strip()
    return json.loads(texto)

def generar_html(nombre, sector, telefono, direccion, rating, resenas, contenido, colores, foto_url):
    stars = "★" * int(rating) + "☆" * (5 - int(rating))
    servicios_html = ""
    for s in contenido["servicios"]:
        servicios_html += f"""
        <div class="servicio-card">
            <div class="servicio-icono">{s['icono']}</div>
            <h3>{s['titulo']}</h3>
            <p>{s['descripcion']}</p>
        </div>"""

    resenas_html = ""
    for r in contenido["resenas"]:
        resenas_html += f"""
        <div class="resena-card">
            <div class="resena-stars">{"★" * r['estrellas']}</div>
            <p>"{r['texto']}"</p>
            <span class="resena-autor">— {r['autor']}</span>
        </div>"""

    # Google Maps embed con dirección
    direccion_encoded = direccion.replace(" ", "+").replace(",", "%2C")
    maps_embed = f"https://www.google.com/maps?q={direccion_encoded}&output=embed"

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": nombre,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": direccion,
            "addressLocality": "Ponferrada",
            "addressRegion": "León",
            "addressCountry": "ES"
        },
        "telephone": telefono,
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(rating),
            "reviewCount": str(resenas)
        }
    }, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{nombre} | {sector.title()} en Ponferrada, El Bierzo</title>
<meta name="description" content="{contenido['meta_description']}">
<meta property="og:title" content="{nombre} — {contenido['eslogan']}">
<meta property="og:description" content="{contenido['meta_description']}">
<meta property="og:type" content="business.business">
<script type="application/ld+json">{schema}</script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  :root {{
    --primario: {colores['primario']};
    --secundario: {colores['secundario']};
    --acento: {colores['acento']};
    --fondo: {colores['fondo']};
  }}
  body {{ font-family: 'Georgia', serif; background: var(--fondo); color: #333; }}

  nav {{ position: fixed; top: 0; width: 100%; background: rgba(0,0,0,0.88); backdrop-filter: blur(12px); z-index: 100; padding: 16px 40px; display: flex; justify-content: space-between; align-items: center; }}
  nav .logo {{ color: var(--acento); font-size: 18px; font-weight: bold; letter-spacing: 2px; }}
  nav .nav-links {{ display: flex; align-items: center; gap: 24px; }}
  nav .nav-links a {{ color: rgba(255,255,255,0.8); text-decoration: none; font-size: 13px; letter-spacing: 1px; transition: color 0.3s; font-family: Arial, sans-serif; }}
  nav .nav-links a:hover {{ color: var(--acento); }}
  .nav-tel {{ background: var(--acento); color: var(--primario) !important; padding: 8px 16px; border-radius: 4px; font-weight: bold !important; }}
  .hamburger {{ display: none; flex-direction: column; gap: 5px; cursor: pointer; }}
  .hamburger span {{ width: 24px; height: 2px; background: white; transition: all 0.3s; }}

  .hero {{ height: 100vh; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; text-align: center; }}
  .hero-bg {{ position: absolute; inset: 0; background-image: url('{foto_url}'); background-size: cover; background-position: center; filter: brightness(0.35); }}
  .hero-overlay {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.6) 100%); }}
  .hero-content {{ position: relative; z-index: 1; max-width: 750px; padding: 0 24px; }}
  .hero-badge {{ display: inline-block; background: var(--acento); color: var(--primario); padding: 6px 18px; border-radius: 20px; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; font-weight: bold; margin-bottom: 24px; font-family: Arial, sans-serif; }}
  .hero h1 {{ font-size: clamp(32px, 6vw, 68px); color: white; line-height: 1.1; margin-bottom: 16px; text-shadow: 0 2px 20px rgba(0,0,0,0.5); }}
  .hero h1 span {{ color: var(--acento); }}
  .hero-sub {{ font-size: 18px; color: rgba(255,255,255,0.85); margin-bottom: 16px; font-style: italic; }}
  .hero-tel-visible {{ font-size: 22px; color: var(--acento); font-weight: bold; margin-bottom: 32px; font-family: Arial, sans-serif; }}
  .hero-tel-visible a {{ color: var(--acento); text-decoration: none; }}
  .hero-btns {{ display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; margin-bottom: 32px; }}
  .btn-primary {{ background: var(--acento); color: var(--primario); padding: 14px 32px; border-radius: 4px; text-decoration: none; font-weight: bold; letter-spacing: 1px; font-size: 14px; transition: transform 0.2s, box-shadow 0.2s; font-family: Arial, sans-serif; }}
  .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }}
  .btn-secondary {{ border: 2px solid rgba(255,255,255,0.6); color: white; padding: 14px 32px; border-radius: 4px; text-decoration: none; font-size: 14px; letter-spacing: 1px; transition: background 0.3s; font-family: Arial, sans-serif; }}
  .btn-secondary:hover {{ background: rgba(255,255,255,0.15); }}
  .hero-rating {{ color: var(--acento); font-size: 20px; }}
  .hero-rating span {{ color: rgba(255,255,255,0.6); font-size: 13px; margin-left: 8px; font-family: Arial, sans-serif; }}

  .experiencia {{ background: var(--primario); padding: 80px 40px; }}
  .experiencia-inner {{ max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center; }}
  .section-label {{ font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--acento); margin-bottom: 12px; font-family: Arial, sans-serif; }}
  .section-title {{ font-size: clamp(24px, 4vw, 40px); margin-bottom: 20px; line-height: 1.2; }}
  .experiencia .section-title {{ color: white; }}
  .experiencia p {{ color: rgba(255,255,255,0.72); font-size: 16px; line-height: 1.9; }}
  .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .stat {{ background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); padding: 24px; border-radius: 8px; text-align: center; }}
  .stat-num {{ font-size: 32px; color: var(--acento); font-weight: bold; }}
  .stat-label {{ font-size: 12px; color: rgba(255,255,255,0.55); margin-top: 6px; font-family: Arial, sans-serif; }}

  .servicios-section {{ padding: 80px 40px; max-width: 1100px; margin: 0 auto; }}
  .servicios-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-top: 40px; }}
  .servicio-card {{ background: white; padding: 32px 24px; border-radius: 8px; box-shadow: 0 4px 24px rgba(0,0,0,0.07); border-top: 3px solid var(--acento); transition: transform 0.3s; }}
  .servicio-card:hover {{ transform: translateY(-4px); }}
  .servicio-icono {{ font-size: 36px; margin-bottom: 16px; }}
  .servicio-card h3 {{ font-size: 17px; color: var(--primario); margin-bottom: 10px; }}
  .servicio-card p {{ font-size: 14px; color: #666; line-height: 1.6; }}

  .resenas-section {{ background: #f7f7f7; padding: 80px 40px; }}
  .resenas-header {{ text-align: center; max-width: 1100px; margin: 0 auto 48px; }}
  .rating-grande {{ font-size: 72px; color: var(--acento); font-weight: bold; line-height: 1; }}
  .rating-stars {{ font-size: 28px; color: var(--acento); margin: 8px 0; }}
  .rating-count {{ color: #999; font-size: 14px; font-family: Arial, sans-serif; }}
  .resenas-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1100px; margin: 0 auto; }}
  .resena-card {{ background: white; padding: 28px; border-radius: 8px; box-shadow: 0 2px 16px rgba(0,0,0,0.06); }}
  .resena-stars {{ color: var(--acento); font-size: 18px; margin-bottom: 12px; }}
  .resena-card p {{ font-size: 15px; color: #555; line-height: 1.7; font-style: italic; margin-bottom: 16px; }}
  .resena-autor {{ font-size: 13px; color: #aaa; font-weight: bold; font-family: Arial, sans-serif; }}

  .contacto-section {{ padding: 80px 40px; max-width: 1100px; margin: 0 auto; }}
  .contacto-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 48px; margin-top: 40px; }}
  .contacto-info {{ display: flex; flex-direction: column; gap: 24px; }}
  .contacto-item {{ display: flex; gap: 16px; align-items: flex-start; }}
  .contacto-icon {{ font-size: 28px; }}
  .contacto-item h4 {{ font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: var(--acento); margin-bottom: 4px; font-family: Arial, sans-serif; }}
  .contacto-item p, .contacto-item a {{ font-size: 16px; color: #555; text-decoration: none; }}
  .mapa-container {{ border-radius: 8px; overflow: hidden; height: 300px; border: none; }}
  .mapa-container iframe {{ width: 100%; height: 100%; border: none; }}

  .cta-final {{ background: linear-gradient(135deg, var(--primario), var(--secundario)); padding: 100px 40px; text-align: center; }}
  .cta-final h2 {{ font-size: clamp(26px, 5vw, 52px); color: white; margin-bottom: 16px; }}
  .cta-final p {{ color: rgba(255,255,255,0.7); font-size: 18px; margin-bottom: 40px; font-style: italic; }}

  footer {{ background: #111; color: rgba(255,255,255,0.4); text-align: center; padding: 24px; font-size: 13px; font-family: Arial, sans-serif; }}

  @media (max-width: 768px) {{
    .experiencia-inner, .contacto-grid {{ grid-template-columns: 1fr; }}
    nav .nav-links {{ display: none; flex-direction: column; position: absolute; top: 60px; left: 0; right: 0; background: rgba(0,0,0,0.95); padding: 20px; gap: 16px; }}
    nav .nav-links.open {{ display: flex; }}
    .hamburger {{ display: flex; }}
    nav {{ padding: 16px 20px; }}
    .experiencia, .servicios-section, .resenas-section, .contacto-section {{ padding: 60px 20px; }}
    .hero-tel-visible {{ font-size: 18px; }}
  }}
</style>
</head>
<body>

<nav>
  <div class="logo">{nombre.upper()}</div>
  <div class="nav-links" id="navLinks">
    <a href="#experiencia">Experiencia</a>
    <a href="#servicios">Servicios</a>
    <a href="#resenas">Reseñas</a>
    <a href="#contacto">Contacto</a>
    <a href="tel:{telefono}" class="nav-tel">📞 {telefono}</a>
  </div>
  <div class="hamburger" onclick="document.getElementById('navLinks').classList.toggle('open')">
    <span></span><span></span><span></span>
  </div>
</nav>

<div class="hero">
  <div class="hero-bg"></div>
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="hero-badge">{sector.title()} · Ponferrada, El Bierzo</div>
    <h1>{nombre}<br><span>{contenido['eslogan']}</span></h1>
    <p class="hero-sub">{contenido['descripcion_hero']}</p>
    <div class="hero-tel-visible"><a href="tel:{telefono}">📞 {telefono}</a></div>
    <div class="hero-btns">
      <a href="#contacto" class="btn-primary">Cómo llegar</a>
      <a href="tel:{telefono}" class="btn-secondary">Llamar ahora</a>
      <a href="#servicios" class="btn-secondary">Ver servicios</a>
    </div>
    <div class="hero-rating">{stars}<span>{rating} · {resenas} reseñas en Google</span></div>
  </div>
</div>

<div class="experiencia" id="experiencia">
  <div class="experiencia-inner">
    <div>
      <div class="section-label">Nuestra esencia</div>
      <h2 class="section-title">Una experiencia que querrás repetir</h2>
      <p>{contenido['descripcion_experiencia']}</p>
    </div>
    <div class="stats">
      <div class="stat"><div class="stat-num">{rating}★</div><div class="stat-label">Valoración Google</div></div>
      <div class="stat"><div class="stat-num">{resenas}+</div><div class="stat-label">Clientes satisfechos</div></div>
      <div class="stat"><div class="stat-num">100%</div><div class="stat-label">Dedicación</div></div>
      <div class="stat"><div class="stat-num">♥</div><div class="stat-label">Con pasión</div></div>
    </div>
  </div>
</div>

<section class="servicios-section" id="servicios">
  <div class="section-label">Lo que ofrecemos</div>
  <h2 class="section-title" style="color: var(--primario);">Nuestros servicios</h2>
  <div class="servicios-grid">{servicios_html}</div>
</section>

<div class="resenas-section" id="resenas">
  <div class="resenas-header">
    <div class="section-label">Lo que dicen nuestros clientes</div>
    <div class="rating-grande">{rating}</div>
    <div class="rating-stars">{stars}</div>
    <div class="rating-count">Basado en {resenas} reseñas de Google</div>
  </div>
  <div class="resenas-grid">{resenas_html}</div>
</div>

<section class="contacto-section" id="contacto">
  <div class="section-label">Encuéntranos</div>
  <h2 class="section-title" style="color: var(--primario);">Visítanos</h2>
  <div class="contacto-grid">
    <div class="contacto-info">
      <div class="contacto-item">
        <div class="contacto-icon">📍</div>
        <div><h4>Dirección</h4><p>{direccion}</p></div>
      </div>
      <div class="contacto-item">
        <div class="contacto-icon">📞</div>
        <div><h4>Teléfono</h4><a href="tel:{telefono}">{telefono}</a></div>
      </div>
      <div class="contacto-item">
        <div class="contacto-icon">🕐</div>
        <div><h4>Horario</h4><p>{contenido['horarios']}</p></div>
      </div>
    </div>
    <div class="mapa-container">
      <iframe src="{maps_embed}" allowfullscreen="" loading="lazy"></iframe>
    </div>
  </div>
</section>

<div class="cta-final">
  <h2>{contenido['frase_final']}</h2>
  <p>Te esperamos en {nombre}</p>
  <div class="hero-btns">
    <a href="#contacto" class="btn-primary">Cómo llegar</a>
    <a href="tel:{telefono}" class="btn-secondary">Llamar ahora</a>
  </div>
</div>

<footer>© 2026 {nombre} · {direccion} · Web creada por Hugo Gayo — Agencia Digital El Bierzo</footer>

</body>
</html>"""

def generar_demo(nombre, sector, telefono, direccion, rating, resenas):
    colores, foto_url = get_colores(sector)
    contenido = generar_contenido(nombre, sector, telefono, direccion, rating, resenas)
    html = generar_html(nombre, sector, telefono, direccion, rating, resenas, contenido, colores, foto_url)

    nombre_archivo = nombre.replace(" ", "_").replace("/", "-").lower()
    ruta = os.path.join(DEMOS_DIR, f"{nombre_archivo}.html")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Demo guardada: {ruta}")
    return ruta

if __name__ == "__main__":
    ruta = generar_demo(
        nombre="La Bodega de Godivah",
        sector="restaurante",
        telefono="Sin telefono",
        direccion="Av. el Castillo, 135, 24400 Ponferrada",
        rating=4.5,
        resenas=89
    )
    os.system(f"open '{ruta}'")
