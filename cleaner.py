import os
import copy
import regex as re
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from config import DATA_DIR


class WikiCleaner:
    """Parses Wikipedia HTML and extracts clean Markdown + plain text.
       Markdown (.md) retains all structural words/citations.
       Plain text (_clean.txt) utilizes a strict vocabulary space guard to
       prevent "Link:" and "Reference:" from merging into single BPE tokens."""

    def __init__(self, output_dir=DATA_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def clean_and_save(self, raw_html, page_name, lang, count):
        if not raw_html:
            return False

        soup = BeautifulSoup(raw_html, "html.parser")

        # Condition to determine if we keep URLs and References in the plain text file
        keep_urls = (lang == "en" and count == 0)
        extracted_urls = []

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
            return False

        # 2. Remove absolute layout/system noise from the root soup
        for tag in soup(["script", "style", "meta", "noscript", "iframe"]):
            tag.decompose()

        # Create an independent clone of the soup specifically for the plain text pipeline
        soup_for_txt = copy.deepcopy(soup)

        # =================================================================
        # PHASE A: GENERATE FAITHFUL MARKDOWN (Preserves all words & citations)
        # =================================================================
        md_classes_to_remove = re.compile(
            r"mw-editsection|navbox|vertical-navbox|sidebar|infobox|toc|hatnote|thumb|metadata|ambox|mw-empty-elt"
        )
        for tag in soup.find_all(class_=md_classes_to_remove):
            tag.decompose()

        for table in soup.find_all("table"):
            table.decompose()

        faithful_md = md(
            str(soup),
            heading_style="ATX",
            autolinks=True,
            strip=["sub", "sup"]
        )
        faithful_md = re.sub(r"\n{3,}", "\n\n", faithful_md)
        faithful_md = "\n".join(line.rstrip() for line in faithful_md.splitlines())

        # =================================================================
        # PHASE B: PROCESS CLEAN TEXT
        # =================================================================
        soup = soup_for_txt  # Switch processing context to the text clone

        classes_to_remove = [
            "mw-editsection", "navbox", "vertical-navbox", "sidebar", 
            "infobox", "toc", "hatnote", "thumb", "metadata", "ambox", "mw-empty-elt"
        ]
        
        if not keep_urls:
            classes_to_remove.extend(["reference", "reflist"])
            
        REMOVE_CLASSES = re.compile("|".join(classes_to_remove))
        for tag in soup.find_all(class_=REMOVE_CLASSES):
            tag.decompose()

        for table in soup.find_all("table"):
            table.decompose()

        sections_to_remove = ["external links", "see also", "further reading"]
        if not keep_urls:
            sections_to_remove.extend(["references", "notes", "sources"])

        for heading in soup.find_all(["h2", "h3"]):
            title = heading.get_text(" ", strip=True).lower()
            if any(section in title for section in sections_to_remove):
                sibling = heading.find_next_sibling()
                while sibling and sibling.name not in ["h2", "h3"]:
                    next_sibling = sibling.find_next_sibling()
                    sibling.decompose()
                    sibling = next_sibling
                heading.decompose()

        # Link parsing via Unified Matrix Token assignment
        cite_counter = 0
        for link in soup.find_all("a"):
            link_text = link.get_text(" ", strip=True)
            href = link.get('href', '')
            
            if keep_urls:
                if href and ("cite_ref" in href or "cite_note" in href):
                    # Throttler: Keep every 5th citation anchor context to limit clutter
                    if cite_counter % 5 == 0:
                        url_id = len(extracted_urls)
                        extracted_urls.append({"url": href})
                        link.replace_with(f" {link_text} (Reference:__MTRX_{url_id}__) ")
                    else:
                        link.replace_with(f" {link_text} ")
                    cite_counter += 1
                elif href and href.startswith("http"):
                    url_id = len(extracted_urls)
                    extracted_urls.append({"url": href})
                    if link_text == href:
                        link.replace_with(f" __MTRX_{url_id}__ ")
                    else:
                        link.replace_with(f" {link_text} (Link:__MTRX_{url_id}__) ")
                else:
                    link.replace_with(f" {link_text} ")
            else:
                link.replace_with(f" {link_text} ")

        # Block text layout separation formatting
        for tag in soup.find_all(["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "br"]):
            tag.append("\n")

        clean_text = soup.get_text(separator=" ", strip=True)

        # Standard artifact cleanups
        clean_text = re.sub(r"\b(edit|citation needed|listen)\b", "", clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r"[\u200b-\u200d\uFEFF]", "", clean_text)
        
        if keep_urls:
            clean_text = re.sub(r"\[\s*\]", "", clean_text)
            
            # Catch raw unhandled text URLs/Citations, isolating trailing sentence punctuation
            def url_replacer(match):
                full_match = match.group(0)
                actual_url = re.sub(r"[.,!?;:\"\'।॥،\]\}]+$", "", full_match)
                trailing_punc = full_match[len(actual_url):]
                
                url_id = len(extracted_urls)
                extracted_urls.append({"url": actual_url})
                return f" __MTRX_{url_id}__ {trailing_punc} "
            
            clean_text = re.sub(r"https?://[^\s()]+|#cite[^\s()]+", url_replacer, clean_text)
        else:
            clean_text = re.sub(r"https?://\S+", "", clean_text)
            clean_text = re.sub(r"\[\d+\]", "", clean_text)
            clean_text = re.sub(r"\(\s*\)", "", clean_text)

        # Core Punctuation & Typography Formatting Engine
        clean_text = re.sub(r"\s+", " ", clean_text)
        clean_text = re.sub(r"([.,!?;:।॥،]){2,}", r"\1", clean_text)
        clean_text = re.sub(r'\s+([.,!?;:।॥،])', r'\1', clean_text)
        clean_text = re.sub(r'([.,!?;:।॥،])([^\s\d.,!?;:।॥लय])', r"\1 \2", clean_text)
        clean_text = re.sub(r'(\d)\s*,\s*(\d)', r'\1,\2', clean_text)
        clean_text = re.sub(r'\s*([-–—])\s*', r'\1', clean_text)
        clean_text = re.sub(r'\(\s+', '(', clean_text)
        clean_text = re.sub(r'\s+\)', ')', clean_text)

        # =================================================================
        # PHASE C: PRE-RESTORATION SPACE GUARD & EXPANSION
        # =================================================================
        if keep_urls:
            # 1. PRE-RESTORATION SPACE GUARD: Forces crisp boundaries on placeholders 
            clean_text = re.sub(r"\s*(\(Link:__MTRX_\d+__\))\s*", r" \1 ", clean_text)
            clean_text = re.sub(r"\s*(\(Reference:__MTRX_\d+__\))\s*", r" \1 ", clean_text)
            clean_text = re.sub(r"\s*(__MTRX_\d+__)\s*", r" \1 ", clean_text)

            # 2. Matrix Expansion
            for i, item in enumerate(extracted_urls):
                url = item["url"]
                if "id=" in url:
                    url = re.sub(r"[?&]id=.*$", "", url)
                if "web.archive.org/web/" in url:
                    url = re.sub(r"https?://web\.archive\.org/web/\d+(?:if_)?/", "", url)
                
                clean_text = clean_text.replace(f"__MTRX_{i}__", url)

            # 3. VOCABULARY PROTECTION: Forces an explicit space after the colons 
            # so the tokenizer treats "Link:" and "https://" as separate tokens!
            clean_text = re.sub(r"\(Link:\s*(https?://[^\s)]+)\)", r"(Link: \1)", clean_text)
            clean_text = re.sub(r"\(Reference:\s*([^\s)]+)\)", r"(Reference: \1)", clean_text)

            # 4. Padding isolation check around parenthetical blocks
            clean_text = re.sub(r"\s*(\(Link:[^\s)]+\))\s*", r" \1 ", clean_text)
            clean_text = re.sub(r"\s*(\(Reference:[^\s)]+\))\s*", r" \1 ", clean_text)
            clean_text = re.sub(r"\s+", " ", clean_text)

        clean_text = clean_text.strip()

        # 7. File Writing Operations
        safe_name = page_name.replace(" ", "_").replace("/", "_")
        base_path = os.path.join(self.output_dir, f"{lang}_{safe_name}")

        with open(f"{base_path}_faithful.md", "a", encoding="utf-8") as f:
            f.write(faithful_md + "\n\n")

        with open(f"{base_path}_clean.txt", "a", encoding="utf-8") as f:
            f.write(clean_text + "\n")

        print(
            f"-> Saved data to: {lang}_{safe_name}_faithful.md "
            f"and _clean.txt (Download #{count})"
        )

        return True