import requests
from bs4 import BeautifulSoup
import re


class DescriptionScraper:
    def __init__(self):
        pass

    def jd_scraper(self, desc_link: str) -> str:
        """Scrapes the job description text from the provided URL"""
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            }
            response = requests.get(desc_link, headers=headers)
            if response.status_code != 200:
                print(f"Failed to retrieve content. Status code: {response.status_code}")
                return ""
            
            soup = BeautifulSoup(response.text, "html.parser")

            possible_selectors = [
                "div.jobDescriptionText",
                "div.description",
                "section.jobDescription",
                "div[data-job-description]",
                "div#jobDescriptionText",
            ]

            text_blocks = []
            for selector in possible_selectors:
                elements = soup.select(selector)
                if elements:
                    for el in elements:
                        text_blocks.append(el.get_text(separator=" ", strip=True))
                    break

            if not text_blocks:
                candidates = soup.find_all(
                    lambda tag: tag.name == "div"
                    and tag.get("class")
                    and any("description" in c.lower() for c in tag["class"])
                )
                for c in candidates:
                    text_blocks.append(c.get_text(separator=" ", strip=True))

            # --- Final fallback: grab all paragraphs ---
            if not text_blocks:
                text_blocks = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]

            jd_text = " ".join(text_blocks)
            jd_text = re.sub(r"\s+", " ", jd_text).strip()

            print(f"✅ Extracted JD length: {len(jd_text)} chars")  # debug
            return jd_text[:5000]

        except Exception as e:
            print(f"An error occurred while scraping: {e}")
            return ""
