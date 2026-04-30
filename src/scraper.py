"""Web scraper for the Alfred Lab website."""

import json
import logging
from collections import deque
from typing import List, Dict
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from src.config import COMPANY_URL, MAX_PAGES, SCRAPED_DATA_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """Scrapes readable text from a company website."""
    
    def __init__(self, url: str = COMPANY_URL, max_pages: int = MAX_PAGES):
        self.url = url.rstrip("/") + "/"
        self.max_pages = max_pages
        self.domain = urlparse(self.url).netloc.lower()
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        }
    
    def scrape(self) -> List[Dict[str, str]]:
        """
        Scrape all relevant content from the company website.
        
        Returns:
            List of dictionaries containing page content and metadata.
        """
        logger.info("Starting scrape of: %s", self.url)
        documents = []
        seen = set()
        queue = deque([self.url])

        while queue and len(documents) < self.max_pages:
            current_url = queue.popleft()
            if current_url in seen:
                continue
            seen.add(current_url)

            try:
                soup = self._fetch_soup(current_url)
            except Exception as exc:
                logger.warning("Failed to scrape %s: %s", current_url, exc)
                continue

            content = self._extract_main_content(soup)
            if content:
                documents.append({
                    "url": current_url,
                    "title": self._get_title(soup),
                    "content": content,
                    "source": "website",
                })

            for link in self._extract_internal_links(soup, current_url):
                if link not in seen:
                    queue.append(link)

        self._save_scraped_documents(documents)
        logger.info("Scraped %s documents", len(documents))
        return documents

    def _fetch_soup(self, url: str) -> BeautifulSoup:
        """Fetch a page and return parsed HTML."""
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            raise ValueError(f"Skipping non-HTML content: {content_type}")
        return BeautifulSoup(response.text, "lxml")
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract readable page text without repeated navigation chrome."""
        content_parts = []
        seen_text = set()
        
        for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "header"]):
            tag.decompose()
        
        main = soup.find("main") or soup.body or soup
        for tag in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th"]):
            text = " ".join(tag.get_text(" ", strip=True).split())
            if len(text) >= 25 and text.lower() not in seen_text:
                content_parts.append(text)
                seen_text.add(text.lower())
        
        return "\n\n".join(content_parts)
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else "Alfred Lab"
    
    def _extract_internal_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract internal links from the page."""
        links = []
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith(("mailto:", "tel:", "javascript:")):
                continue

            absolute_url = urljoin(current_url, href)
            absolute_url = urldefrag(absolute_url)[0].rstrip("/") + "/"
            parsed = urlparse(absolute_url)

            if parsed.scheme in {"http", "https"} and parsed.netloc.lower() == self.domain:
                if absolute_url not in links:
                    links.append(absolute_url)
        
        return links

    def _save_scraped_documents(self, documents: List[Dict[str, str]]) -> None:
        """Keep a local JSON copy so users can inspect what went into FAISS."""
        SCRAPED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with SCRAPED_DATA_PATH.open("w", encoding="utf-8") as file:
            json.dump(documents, file, indent=2, ensure_ascii=False)


def scrape_company_data() -> List[Dict[str, str]]:
    """
    Convenience function to scrape company data.
    
    Returns:
        List of documents with company information.
    """
    scraper = WebScraper()
    return scraper.scrape()


if __name__ == "__main__":
    docs = scrape_company_data()
    for i, doc in enumerate(docs):
        print(f"\n--- Document {i+1} ---")
        print(f"Title: {doc['title']}")
        print(f"URL: {doc['url']}")
        print(f"Content preview: {doc['content'][:500]}...")
