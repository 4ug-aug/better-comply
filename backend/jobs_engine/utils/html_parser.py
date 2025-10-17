"""HTML parsing utilities using trafilatura for regulation content extraction."""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import chardet
import trafilatura
from bs4 import BeautifulSoup

from jobs_engine.schemas.parse_schemas import ParsedDocument, ParsedSection

logger = logging.getLogger(__name__)


def detect_encoding(headers: Dict[str, str], content_bytes: bytes) -> Tuple[str, str, float]:
    """Detect encoding from content-type header or chardet fallback.

    Args:
        headers: HTTP response headers
        content_bytes: Raw content bytes

    Returns:
        Tuple of (encoding, method, confidence)
    """
    # Try content-type charset first
    content_type = headers.get("content-type", "").lower()
    if "charset=" in content_type:
        charset = content_type.split("charset=")[-1].split(";")[0].strip()
        try:
            # Validate encoding by attempting to decode
            content_bytes.decode(charset)
            logger.info(f"Detected encoding from content-type: {charset}")
            return charset, "content-type", 1.0
        except (LookupError, UnicodeDecodeError):
            logger.warning(f"Invalid charset in content-type: {charset}")

    # Fallback to chardet
    try:
        detected = chardet.detect(content_bytes)
        encoding = detected.get("encoding", "utf-8")
        confidence = detected.get("confidence", 0.0)
        logger.info(f"Detected encoding via chardet: {encoding} (confidence: {confidence})")
        return encoding, "chardet", confidence
    except Exception as e:
        logger.warning(f"Chardet detection failed: {e}, defaulting to utf-8")
        return "utf-8", "fallback", 0.0


def parse_html_to_sections(
    html_text: str, source_url: str, content_bytes: bytes
) -> ParsedDocument:
    """Parse HTML to structured sections using trafilatura.

    Args:
        html_text: Decoded HTML text
        source_url: Source URL for reference
        content_bytes: Original bytes for byte offset calculation

    Returns:
        ParsedDocument with sections and metadata

    Raises:
        ValueError: If parsing fails
    """
    try:
        logger.info(f"Parsing HTML from {source_url}")
        logger.debug(f"HTML content length: {len(html_text)} chars, first 200 chars: {html_text[:200]}")
        
        # Extract main content using trafilatura
        extracted = trafilatura.extract(
            html_text,
            include_comments=False,
            favor_precision=True,
            include_tables=True,
        )
        
        if not extracted:
            logger.warning(
                f"Trafilatura extraction returned empty for {source_url}, "
                "attempting fallback extraction"
            )
            # Fallback: use BeautifulSoup to extract any text
            soup = BeautifulSoup(html_text, "html.parser")
            extracted = soup.get_text(separator="\n", strip=True)
            
            if not extracted:
                raise ValueError(
                    "Could not extract any content from HTML - "
                    "possibly malformed or non-HTML content"
                )

        # Parse with BeautifulSoup for structure
        soup = BeautifulSoup(html_text, "html.parser")

        # Extract metadata
        published_date = None
        try:
            metadata = trafilatura.extract_metadata(html_text)
            if metadata:
                # trafilatura.extract_metadata returns a metadata object
                # Try to get the date attribute
                if hasattr(metadata, 'date'):
                    published_date = str(metadata.date) if metadata.date else None
                elif hasattr(metadata, 'modified'):
                    published_date = str(metadata.modified) if metadata.modified else None
                else:
                    # If metadata is already a string/datetime, convert it
                    published_date = str(metadata)
        except Exception as e:
            logger.debug(f"Could not extract published date: {e}")
        
        # Extract language (trafilatura's guess_language might not be available)
        language = "en"  # Default to English for regulations

        # Build section tree from headings (H1-H4)
        sections = _extract_sections(soup, extracted, content_bytes)

        # Create parsed document
        parsed_doc = ParsedDocument(
            source_url=source_url,
            published_date=published_date,
            language=language,
            fetch_timestamp=datetime.now(timezone.utc).isoformat(),
            sections=sections,
        )

        logger.info(f"Parsed HTML: {len(sections)} sections extracted from {source_url}")
        return parsed_doc

    except Exception as e:
        logger.exception(f"Error parsing HTML from {source_url}: {e}")
        raise ValueError(f"Failed to parse HTML: {e}")


def _extract_sections(
    soup: BeautifulSoup, extracted_text: str, content_bytes: bytes
) -> List[ParsedSection]:
    """Extract sections from BeautifulSoup parsed HTML.

    Args:
        soup: BeautifulSoup parsed HTML
        extracted_text: Trafilatura extracted text
        content_bytes: Original bytes for offset calculation

    Returns:
        List of ParsedSection objects
    """
    sections: List[ParsedSection] = []
    section_id = 1

    # Find all headings (H1-H4)
    headings = soup.find_all(["h1", "h2", "h3", "h4"])

    for heading in headings:
        try:
            level = int(heading.name[1])  # h1 -> 1, h2 -> 2, etc.
            heading_text = heading.get_text().strip()

            if not heading_text:
                continue

            # Collect text until next heading
            content_parts = []
            current = heading.next_sibling

            while current:
                if current.name in ("h1", "h2", "h3", "h4"):
                    break

                if isinstance(current, str):
                    text = current.strip()
                    if text:
                        content_parts.append(text)
                elif hasattr(current, "get_text"):
                    text = current.get_text().strip()
                    if text and current.name not in ("script", "style", "meta"):
                        content_parts.append(text)

                current = current.next_sibling

            section_text = "\n".join(content_parts).strip()
            if not section_text:
                section_text = heading_text

            # Compute SHA256
            section_hash = hashlib.sha256(section_text.encode()).hexdigest()

            # Estimate byte offsets (approximate)
            byte_start = extracted_text.find(heading_text)
            byte_end = byte_start + len(heading_text) + len(section_text)

            # Create section
            section = ParsedSection(
                id=section_id,
                level=level,
                heading=heading_text,
                text=section_text,
                sha256=section_hash,
                byte_offset_start=max(0, byte_start),
                byte_offset_end=byte_end,
                tables=[],
                language="en",
            )
            sections.append(section)
            section_id += 1

        except Exception as e:
            logger.warning(f"Error extracting section from heading {heading}: {e}")
            continue

    # If no headings found, create single section from extracted text
    if not sections and extracted_text:
        section_hash = hashlib.sha256(extracted_text.encode()).hexdigest()
        section = ParsedSection(
            id=1,
            level=1,
            heading="Content",
            text=extracted_text,
            sha256=section_hash,
            byte_offset_start=0,
            byte_offset_end=len(extracted_text),
            tables=[],
            language="en",
        )
        sections.append(section)

    return sections
