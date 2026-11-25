import json
import logging
import re
from typing import Any
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

ECI_BASE_URL = "https://www.elcorteingles.es"
ECI_SEARCH_URL = f"{ECI_BASE_URL}/electronica/search/"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


def _parse_price(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("€", "").replace("\xa0", "").replace(" ", "")
    match = re.search(r"(\d+(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:\.\d{1,2})?)", text)
    if not match:
        return None
    raw = match.group(1)
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        raw = raw.replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _extract_jsonld_products(soup: BeautifulSoup) -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or script.get_text() or ""
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        blocks = data if isinstance(data, list) else [data]
        for block in blocks:
            if not isinstance(block, dict):
                continue
            item_list = block.get("itemListElement")
            if isinstance(item_list, list):
                for entry in item_list:
                    item = entry.get("item") if isinstance(entry, dict) else None
                    if isinstance(item, dict) and item.get("name"):
                        offers = item.get("offers") or {}
                        if isinstance(offers, list) and offers:
                            offers = offers[0]
                        brand = item.get("brand")
                        brand_name = brand.get("name") if isinstance(brand, dict) else brand
                        products.append(
                            {
                                "sku": str(item.get("sku") or "")[:64] or None,
                                "title": str(item.get("name"))[:255],
                                "brand": str(brand_name)[:100] if brand_name else None,
                                "category": "Electrónica",
                                "price_eur": _parse_price(
                                    offers.get("price") if isinstance(offers, dict) else None
                                ),
                                "summary": str(item.get("description") or "")[:400] or None,
                                "source_url": urljoin(ECI_BASE_URL, str(item.get("url") or ""))
                                if item.get("url")
                                else None,
                                "image_url": str(item.get("image"))
                                if isinstance(item.get("image"), str)
                                else None,
                            }
                        )
            elif block.get("@type") == "Product" and block.get("name"):
                offers = block.get("offers") or {}
                if isinstance(offers, list) and offers:
                    offers = offers[0]
                brand = block.get("brand")
                brand_name = brand.get("name") if isinstance(brand, dict) else brand
                products.append(
                    {
                        "sku": str(block.get("sku") or "")[:64] or None,
                        "title": str(block.get("name"))[:255],
                        "brand": str(brand_name)[:100] if brand_name else None,
                        "category": "Electrónica",
                        "price_eur": _parse_price(
                            offers.get("price") if isinstance(offers, dict) else None
                        ),
                        "summary": str(block.get("description") or "")[:400] or None,
                        "source_url": urljoin(ECI_BASE_URL, str(block.get("url") or ""))
                        if block.get("url")
                        else None,
                        "image_url": str(block.get("image"))
                        if isinstance(block.get("image"), str)
                        else None,
                    }
                )
    return products


class EciClient:
    """Conector respetuoso para consultar catálogo público de electrónica de El Corte Inglés."""

    async def search_live(self, query: str, limit: int = 6) -> dict[str, Any]:
        url = f"{ECI_SEARCH_URL}?s={quote_plus(query.strip())}"
        try:
            async with httpx.AsyncClient(
                timeout=8.0, follow_redirects=True, headers=DEFAULT_HEADERS
            ) as client:
                resp = await client.get(url)

            if resp.status_code in (403, 429, 503):
                logger.info("ECI devolvió HTTP %s para '%s' (protección anti-bot/límite).", resp.status_code, query)
                return {
                    "status": "blocked",
                    "http_status": resp.status_code,
                    "items": [],
                    "search_url": url,
                }

            resp.raise_for_status()
            html = resp.text

            lower_html = html[:4000].lower()
            if "captcha" in lower_html or "access denied" in lower_html or "akamai" in lower_html:
                return {
                    "status": "blocked",
                    "http_status": resp.status_code,
                    "items": [],
                    "search_url": url,
                }

            soup = BeautifulSoup(html, "html.parser")
            items = _extract_jsonld_products(soup)

            # Fallback a enlaces de tarjetas de producto si no hay JSON-LD
            if not items:
                for card in soup.select("[data-product-id], article.product_preview, .product_preview")[:limit]:
                    title_el = card.select_one("h2, h3, .product_preview-title, a[title]")
                    if not title_el:
                        continue
                    title = title_el.get_text(" ", strip=True) or title_el.get("title", "")
                    if not title:
                        continue
                    link_el = card.select_one("a[href]")
                    price_el = card.select_one(".price, .product_preview-price, [class*='price']")
                    items.append(
                        {
                            "sku": card.get("data-product-id"),
                            "title": title[:255],
                            "brand": None,
                            "category": "Electrónica",
                            "price_eur": _parse_price(price_el.get_text(" ", strip=True) if price_el else None),
                            "summary": None,
                            "source_url": urljoin(ECI_BASE_URL, link_el["href"]) if link_el else url,
                            "image_url": None,
                        }
                    )

            return {
                "status": "ok" if items else "empty",
                "http_status": resp.status_code,
                "items": items[:limit],
                "search_url": url,
            }
        except Exception as exc:
            logger.warning("Error consultando ECI para '%s': %s: %s", query, type(exc).__name__, exc)
            return {
                "status": "error",
                "http_status": None,
                "items": [],
                "search_url": url,
            }


eci_client = EciClient()
