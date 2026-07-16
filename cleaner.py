import os
import regex as re
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from config import DATA_DIR


class WikiCleaner:
    """Parses Wikipedia HTML and extracts clean Markdown + plain text."""

    def __init__(self, output_dir=DATA_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def clean_and_save(self, raw_html, page_name, lang, count):
        if not raw_html:
            return False

        soup = BeautifulSoup(raw_html, "html.parser")

        # 1. Extract main article content
        content_div = (
            soup.find(id="mw-content-text")
            or soup.find("main")
            or soup.find("article")
        )

        if content_div:
            soup = content_div
        else:
            print(f"Warning: Could not find main content div for {page_name}")

        # 2. Remove obvious non-content tags
        for tag in soup([
            "script",
            "style",
            "meta",
            "noscript",
            "iframe"
        ]):
            tag.decompose()

        # 3. Remove Wikipedia-specific noise
        REMOVE_CLASSES = re.compile(
            r"mw-editsection|"
            r"navbox|"
            r"vertical-navbox|"
            r"sidebar|"
            r"infobox|"
            r"toc|"
            r"reference|"
            r"reflist|"
            r"hatnote|"
            r"thumb|"
            r"metadata|"
            r"ambox|"
            r"mw-empty-elt"
        )

        for tag in soup.find_all(class_=REMOVE_CLASSES):
            tag.decompose()

        # Remove tables (infoboxes, nav tables, etc.)
        for table in soup.find_all("table"):
            table.decompose()

        # Remove References / External links sections
        for heading in soup.find_all(["h2", "h3"]):
            title = heading.get_text(" ", strip=True).lower()

            if any(section in title for section in [
                "references",
                "external links",
                "see also",
                "further reading",
                "notes",
                "sources"
            ]):
                sibling = heading.find_next_sibling()

                while sibling and sibling.name not in ["h2", "h3"]:
                    next_sibling = sibling.find_next_sibling()
                    sibling.decompose()
                    sibling = next_sibling

                heading.decompose()

        # 4. Strip links and keep text
        for link in soup.find_all("a"):
            link.replace_with(link.get_text(" ", strip=True))

        # 5. Generate faithful Markdown
        faithful_md = md(
            str(soup),
            heading_style="ATX",
            autolinks=True,
            strip=["sub", "sup"]
        )

        faithful_md = re.sub(r"\n{3,}", "\n\n", faithful_md)
        faithful_md = "\n".join(
            line.rstrip() for line in faithful_md.splitlines()
        )

        # 6. Prepare clean text extraction
        for tag in soup.find_all([
            "p", "div",
            "h1", "h2", "h3", "h4", "h5", "h6",
            "li", "br"
        ]):
            tag.append("\n")

        clean_text = soup.get_text(separator=" ", strip=True)

        # Remove URLs
        clean_text = re.sub(r"https?://\S+", "", clean_text)

        # Remove citation markers
        clean_text = re.sub(r"\[\d+\]", "", clean_text)

        # Remove common wiki artifacts
        clean_text = re.sub(
            r"\b(edit|citation needed|listen)\b",
            "",
            clean_text,
            flags=re.IGNORECASE
        )

        # Remove unicode junk
        clean_text = re.sub(r"[\u200b-\u200d\uFEFF]", "", clean_text)

        # Remove empty brackets
        clean_text = re.sub(r"\(\s*\)", "", clean_text)

        # 1. Collapse whitespace
        clean_text = re.sub(r"\s+", " ", clean_text)

        # 2. Collapse repeated punctuation
        clean_text = re.sub(r"([.,!?;:।॥]){2,}", r"\1", clean_text)

        # 3. Remove spaces BEFORE punctuation
        clean_text = re.sub(r'\s+([.,!?;:।॥،])', r'\1', clean_text)

        # 4. Add a single space AFTER punctuation, BUT explicitly IGNORE digits
        clean_text = re.sub(r'([.,!?;:।॥،])([^\s\d.,!?;:।॥،])', r'\1 \2', clean_text)

        # 5. Fix fragmented numbers: stitch "1, 428" or "1 ,428" back into "1,428"
        clean_text = re.sub(r'(\d)\s*,\s*(\d)', r'\1,\2', clean_text)

        # 6. Remove spaces around hyphens and dashes
        clean_text = re.sub(r'\s*([-–—])\s*', r'\1', clean_text)

        # 7. Fix bracket spacing
        clean_text = re.sub(r'\(\s+', '(', clean_text)
        clean_text = re.sub(r'\s+\)', ')', clean_text)

        clean_text = clean_text.strip()

        # 7. Save files
        safe_name = (
            page_name.replace(" ", "_")
            .replace("/", "_")
        )

        base_path = os.path.join(
            self.output_dir,
            f"{lang}_{safe_name}"
        )

        # BUG FIX: Changed "a" (append) to "w" (write) to prevent duplication
        with open(
            f"{base_path}_faithful.md",
            "a", 
            encoding="utf-8"
        ) as f:
            f.write(faithful_md + "\n\n")

        with open(
            f"{base_path}_clean.txt",
            "a",
            encoding="utf-8"
        ) as f:
            f.write(clean_text + "\n")

        print(
            f"-> Saved data to: "
            f"{lang}_{safe_name}_faithful.md "
            f"and _clean.txt (Download #{count})"
        )

        return True