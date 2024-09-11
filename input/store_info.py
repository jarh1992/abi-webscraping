import json
from pathlib import Path
from settings.settings import BASE_DIR

from src.models.models import Store
from src.scrapers.carulla import scraper as carulla_scraper
from src.scrapers.exito import scraper as exito_scraper
from src.scrapers.jumbo import scraper as jumbo_scraper
from src.scrapers.makro import scraper as makro_scraper
from src.scrapers.metro import scraper as metro_scraper
from src.scrapers.olimpica import scraper as olimpica_scraper
from src.scrapers.rappi import scraper as rappi_scraper


STORES = {
    "carulla": Store(
        'carulla',
        'https://www.carulla.com/{prod}?_q={prod}&map=ft',
        carulla_scraper
    ),
    "exito": Store(
        'exito',
        'https://www.exito.com/s?q={prod}&map=ft',
        exito_scraper
    ),
    "jumbo": Store(
        'jumbo',
        'https://www.tiendasjumbo.co/{prod}?_q={prod}&map=ft',
        jumbo_scraper
    ),
    "makro": Store(
        'makro',
        'https://tienda.makro.com.co/search?name={prod}',
        makro_scraper
    ),
    "metro": Store(
        'metro',
        'https://www.tiendasmetro.co/{prod}?_q={prod}&map=ft',
        metro_scraper
    ),
    "olimpica": Store(
        'olimpica',
        'https://www.olimpica.com/{prod}?_q={prod}&map=ft',
        olimpica_scraper
    ),
    "rappi": Store(
        'rappi',
        'https://www.rappi.com.co/search?query={prod}',
        rappi_scraper
    )
}

brand_input = Path(BASE_DIR / "input/brands_test.json")
with brand_input.open(encoding='utf8') as f:
    BRANDS = json.load(f)
