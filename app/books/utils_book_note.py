import requests
from bs4 import BeautifulSoup
import logging
import re
from time import sleep

# Configure logging
logger = logging.getLogger("liboo.app.books.utils_book_note")


def fetch_goodreads_rating_by_isbn(isbn: str) -> float | None:
    """
    Fetches the average rating for a book from Goodreads using its ISBN.

    Args:
        isbn: The ISBN number of the book (can be ISBN-10 or ISBN-13)

    Returns:
        float: The book's average rating on Goodreads (scale 0-5)
        None: If the rating couldn't be retrieved
    """
    if not isbn or not isinstance(isbn, str):
        logger.warning("Invalid ISBN provided")
        return None

    # Clean ISBN - remove hyphens, spaces, etc.
    clean_isbn = re.sub(r"[^0-9X]", "", isbn)

    if not clean_isbn:
        logger.warning(f"ISBN '{isbn}' is not valid after cleaning")
        return None

    # Goodreads URL pattern for ISBN lookup
    url = f"https://www.goodreads.com/book/isbn/{clean_isbn}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        logger.info(f"Requesting Goodreads data for ISBN: {clean_isbn}")
        response = requests.get(url, headers=headers, timeout=10)

        # Check if request was successful
        if response.status_code != 200:
            logger.warning(
                f"Failed to fetch data from Goodreads: HTTP {response.status_code}"
            )
            return None

        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Method 1: Look for the rating in the JSON-LD script (most reliable method)
        script_tags = soup.find_all("script", {"type": "application/ld+json"})
        for script in script_tags:
            try:
                import json

                data = json.loads(script.string)
                if "aggregateRating" in data:
                    rating = float(data["aggregateRating"]["ratingValue"])
                    logger.info(
                        f"Found rating {rating} for ISBN {clean_isbn} via JSON-LD"
                    )
                    return rating
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.debug(f"Error parsing JSON-LD: {e}")
                continue

        # Method 2: Check for the rating in the meta tags
        meta_rating = soup.find("meta", {"itemprop": "ratingValue"})
        if meta_rating and meta_rating.get("content"):
            try:
                rating = float(meta_rating["content"])
                logger.info(
                    f"Found rating {rating} for ISBN {clean_isbn} via meta tags"
                )
                return rating
            except (ValueError, TypeError) as e:
                logger.debug(f"Error parsing meta rating: {e}")

        # Method 3: Try to find the rating in the page content
        # This is the most fragile method as it depends on the page structure
        # Several potential selectors based on Goodreads' HTML structure
        selectors = [
            "div.RatingStatistics__rating",
            "span.RatingStatistics__rating",
            "div[data-testid='averageRating']",
            "span.average",
        ]

        for selector in selectors:
            rating_element = soup.select_one(selector)
            if rating_element:
                rating_text = rating_element.get_text().strip()
                try:
                    # Extract the numeric part and convert to float
                    rating_match = re.search(r"([0-9]\.[0-9]+)", rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        if 0 <= rating <= 5:
                            logger.info(
                                f"Found rating {rating} for ISBN {clean_isbn} via selector: {selector}"
                            )
                            return rating
                except (ValueError, AttributeError) as e:
                    logger.debug(
                        f"Error extracting rating from text '{rating_text}': {e}"
                    )

        logger.warning(f"Could not find rating for ISBN {clean_isbn} on Goodreads")
        return None

    except requests.exceptions.Timeout:
        logger.error(f"Request to Goodreads timed out for ISBN {clean_isbn}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Goodreads failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching Goodreads rating: {e}")

    return None


def fetch_with_retry(
    isbn: str, max_retries: int = 3, delay: float = 2.0
) -> float | None:
    """
    Attempts to fetch the Goodreads rating with retries.

    Args:
        isbn: The book ISBN
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds

    Returns:
        The book rating or None if unavailable
    """
    for attempt in range(max_retries):
        if attempt > 0:
            logger.info(f"Retry attempt {attempt + 1}/{max_retries} for ISBN {isbn}")
            sleep(delay)  # Wait before retrying

        rating = fetch_goodreads_rating_by_isbn(isbn)
        if rating is not None:
            return rating

    logger.warning(f"All {max_retries} attempts to fetch rating for ISBN {isbn} failed")
    return None

if __name__ == "__main__":
    # Example usage
    isbn = "9780451490827"  # Replace with a valid ISBN
    rating = fetch_with_retry(isbn)
    if rating:
        print(f"Rating for ISBN {isbn}: {rating}")
    else:
        print(f"Could not fetch rating for ISBN {isbn}")