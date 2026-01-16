import datetime
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from pathlib import Path

import requests
from dotenv import load_dotenv
from epicstore_api import EpicGamesStoreAPI

# Load environment variables from .env file
load_dotenv()

# Global Configuration
SETTINGS_FILE = 'settings.json'
PRICE_THRESHOLD = 10000 # Default
CURRENCY_CODE = "INR"
EMAILS = []
CATEGORIES = []
DEEP_SEARCH_FREE = False

def load_settings():
    """Load configuration from settings.json"""
    global PRICE_THRESHOLD, CURRENCY_CODE, EMAILS, CATEGORIES, DEEP_SEARCH_FREE
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                # settings stores price in major units (e.g. 100), we need minor (10000)
                PRICE_THRESHOLD = int(data.get('price_threshold', 100)) * 100 
                CURRENCY_CODE = data.get('currency', 'INR')
                EMAILS = data.get('emails', [])
                CATEGORIES = data.get('categories', [])
                DEEP_SEARCH_FREE = data.get('deep_search_free', False)
                
                # If deep search is enabled, enforce price = 0
                if DEEP_SEARCH_FREE:
                    PRICE_THRESHOLD = 0
                    
                logging.info(f"Loaded settings: Threshold={PRICE_THRESHOLD}, Emails={len(EMAILS)}, DeepSearch={DEEP_SEARCH_FREE}")
    except Exception as e:
        logging.error(f"Failed to load settings: {e}")

def is_valid_game(game):
    """Filter out invalid/unwanted game entries."""
    title = game.get("title", "").lower()
    
    # Exclude dev/test audiences
    if "audience" in title or "dev " in title or " dev" in title:
        return False
    
    # Exclude DLC/add-ons (look for common patterns)
    dlc_keywords = ["dlc", " pack", "bundle", "skin", "add-on", "expansion"]
    if any(keyword in title for keyword in dlc_keywords):
        return False
    
    # Must have a valid product slug
    url_slug = game.get("urlSlug") or game.get("productSlug")
    if not url_slug or url_slug.strip() == "":
        return False
    
    # Check if game is actually available (not coming soon)
    status = game.get("status", "")
    if status == "COMING_SOON":
        return False
    
    # Additional check: title should not be empty or suspiciously short
    if len(title.strip()) < 3:
        return False
    
    return True

def validate_game_url(url, timeout=3):
    """Verify that a game URL is accessible (not 404)."""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        # Accept 200 OK or 301/302 redirects
        if response.status_code in [200, 301, 302]:
            return True
        return False
    except Exception as e:
        logging.debug(f"URL validation failed for {url}: {e}")
        return False

# Load initially
load_settings()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL = os.getenv("EMAIL")  # This is your SMTP login email
PASSWORD = os.getenv("PASSWORD")
# TO_EMAIL is now handled via EMAILS list from settings.json, but keep env as fallback
TO_EMAIL = os.getenv("TO_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")


def check_env_variables():
    """Check if all required environment variables are set."""
    required_vars = {
        "SMTP_SERVER": os.getenv("SMTP_SERVER"),
        "SMTP_PORT": os.getenv("SMTP_PORT"),
        "EMAIL": os.getenv("EMAIL"),
        "PASSWORD": os.getenv("PASSWORD"),
        "TO_EMAIL": os.getenv("TO_EMAIL"),
        "FROM_EMAIL": os.getenv("FROM_EMAIL")
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Validate SMTP_PORT is a valid integer
    try:
        int(required_vars["SMTP_PORT"])
    except ValueError:
        raise ValueError(f"SMTP_PORT must be a valid number, got: {required_vars['SMTP_PORT']}")


def format_date(date_string):
    """Format the date string to a more readable format."""
    try:
        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.000Z")
        return date_obj.strftime(
            "%B %d, %Y at %I:%M %p"
        )  # Example: January 09, 2025 at 04:00 PM
    except ValueError:
        logging.error(f"Error parsing date: {date_string}")
        return date_string  # Return the original string if parsing fails


def fetch_free_games():
    """Fetch free and discounted games under the threshold from the Epic Games Store."""
    url = f"https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=IN&allowCountries=IN"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching free games: {e}")
        return None

    free_games = []
    try:
        games: list[dict] = data["data"]["Catalog"]["searchStore"]["elements"]
    except (KeyError, TypeError) as e:
        logging.error(f"Error parsing API response: {e}")
        return None

    for game in games:
        # Check title to avoid duplicates if necessary, but API usually handles it.
        if not game.get("promotions"):
            continue

        # Check for promotional offers (current)
        promotions = game["promotions"].get("promotionalOffers", [])
        if not promotions:
             continue

        for promo in promotions:
            for offer in promo.get("promotionalOffers", []):
                # Retrieve price information
                price_info = game.get("price", {}).get("totalPrice", {})
                discounted_price = price_info.get("discountPrice", 0)
                original_price = price_info.get("originalPrice", 0)
                fmt_price = price_info.get("fmtPrice", {})
                
                # Logic: Free (0) OR Under Threshold (100 INR = 10000)
                # Ensure we only pick items that are actually discounted or free
                if discounted_price > PRICE_THRESHOLD:
                    continue
                
                # Check if it's free
                is_free = discounted_price == 0
                is_cheap = 0 < discounted_price <= PRICE_THRESHOLD

                if not (is_free or is_cheap):
                    continue

                # Extracting the correct urlSlug from catalogNs.mappings
                url_slug = next(
                    (
                        mapping.get("pageSlug")
                        for mapping in game.get("catalogNs", {}).get("mappings", [])
                        if mapping.get("pageSlug")
                    ),
                    None,
                )
                
                # Fallback to urlSlug or productSlug if mapping fails
                if not url_slug:
                    url_slug = game.get("urlSlug") or game.get("productSlug")

                # Ensure url_slug is not None
                if not url_slug:
                     continue

                # Format Price Strings
                original_price_str = fmt_price.get("originalPrice", "N/A")
                discounted_price_str = fmt_price.get("discountPrice", "Free" if is_free else "N/A")
                
                if is_free:
                    discounted_price_str = "Free"
                
                free_games.append(
                    {
                        "title": game.get("title"),
                        "description": game.get(
                            "description", "No description available."
                        ),
                        "original_price": original_price_str,
                        "discounted_price": discounted_price_str,
                        "image_url": game.get("keyImages", [{}])[0].get("url", ""),
                        "url": f"https://store.epicgames.com/en-US/p/{url_slug}",
                        "start_date": offer.get("startDate"),
                        "end_date": offer.get("endDate"),
                        "is_free": is_free
                    }
                )
                # Break inner loop to avoid duplicate entries for the same game
                break
            # Break outer loop
            break
            
    return free_games




def fetch_cheap_games(emit_callback=None):
    """Fetch games available under the price threshold using epicstore-api."""
    msg = f"Fetching cheap games under {PRICE_THRESHOLD/100} {CURRENCY_CODE}..."
    if emit_callback:
        emit_callback({'type': 'log', 'message': msg})
    else:
        logging.info(msg)

    try:
        api = EpicGamesStoreAPI(locale='en-US', country='IN')
        
        # 1. Fetch count
        # To show progress, we need to know total. But searching provides paging. 
        # We process a fixed amount (e.g. 1000) or pages.
        count_to_fetch = 1000
        
        games_batch = api.fetch_store_games(
            count=count_to_fetch,
            sort_by='currentPrice', 
            sort_dir='ASC',
            allow_countries='IN'
        )
        
        cheap_games = []
        elements = games_batch.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])
        total_elements = len(elements)
        
        if emit_callback:
            emit_callback({'type': 'log', 'message': f"Fetched {total_elements} items. Processing filters..."})
        
        processed_count = 0
        
        # Initial Progress
        if emit_callback:
            emit_callback({'type': 'progress', 'processed': 0, 'total': total_elements})

        for game in elements:
            processed_count += 1
            # Emit progress more frequently (every 10 items)
            if emit_callback and processed_count % 10 == 0:
                 emit_callback({'type': 'progress', 'processed': processed_count, 'total': total_elements})
            
            price_info = game.get('price', {}).get('totalPrice', {})
            discount_price = price_info.get('discountPrice', 0)
            original_price = price_info.get('originalPrice', 0)
            
            # ... (Category Filtering code remains same, omitted for brevity, logic assumed intact)
            # We must be careful not to delete existing code if I use replace_file_content poorly.
            # I will use a larger context or ensure I copy the inner loop logic back if I am replacing the loop.
            
            # To be safe and precise with replace_file_content, I will target the specific progress lines only.
            
    # RETRYING WITH PRECISE TARGETING IN NEXT TOOL CALL since I can't conditionally omit code blocks here.
    # Actually I will just replace the loop start and progress emission part.
    
        processed_count = 0
        if emit_callback:
             emit_callback({'type': 'progress', 'processed': 0, 'total': total_elements})

        for game in elements:
            processed_count += 1
            if emit_callback and processed_count % 10 == 0:
                 emit_callback({'type': 'progress', 'processed': processed_count, 'total': total_elements})
            
            # Apply validation filter first
            if not is_valid_game(game):
                continue
            
            price_info = game.get('price', {}).get('totalPrice', {})
            discount_price = price_info.get('discountPrice', 0)
            original_price = price_info.get('originalPrice', 0)
            
            # Skip if price info is missing or invalid
            if price_info is None or discount_price is None:
                continue
            
            # Category Filtering
            game_categories = [c.get('path', '').lower() for c in game.get('categories', [])]
            
            if CATEGORIES and "All" not in CATEGORIES:
                search_terms = [c.lower() for c in CATEGORIES]
                match_found = False
                for term in search_terms:
                    for cat_path in game_categories:
                        if term in cat_path:
                            match_found = True
                            break
                    if match_found:
                        break
                
                if not match_found:
                    continue

            # Filter logic:
            # If DEEP_SEARCH_FREE is on, ONLY include games with price == 0
            # Otherwise, we look for cheap discounted games (price > 0)
            
            is_free_game = (discount_price == 0)
            is_cheap_game = (0 < discount_price <= PRICE_THRESHOLD and discount_price < original_price)
            
            should_include = False
            if DEEP_SEARCH_FREE:
                # Strict: only truly free games
                if is_free_game:
                    should_include = True
            else:
                # Normal mode: include cheap or free games
                if is_cheap_game or is_free_game:
                    should_include = True
                
            if should_include:
                url_slug = game.get("urlSlug") or game.get("productSlug")
                if not url_slug:
                    continue
                
                # Build the URL
                game_url = f"https://store.epicgames.com/en-US/p/{url_slug}"
                
                # CRITICAL: Validate URL before adding to results
                if not validate_game_url(game_url):
                    if emit_callback:
                        emit_callback({'type': 'log', 'level': 'warning', 'message': f"Skipped invalid URL: {game.get('title')}"})
                    continue
                    
                fmt_price = price_info.get('fmtPrice', {})
                
                # Determine display price
                d_price = fmt_price.get('discountPrice')
                if is_free_game:
                    d_price = "Free"
                
                # Safely extract image
                key_images = game.get("keyImages", [])
                image_url = ""
                if key_images and isinstance(key_images, list):
                    for img in key_images:
                        if img.get("type") == "Thumbnail" or img.get("type") == "DieselStoreFrontWide":
                            image_url = img.get("url", "")
                            break
                    if not image_url and key_images:
                         image_url = key_images[0].get("url", "")
                
                # Determine display price labels
                original_price_str = fmt_price.get('originalPrice')
                discounted_price_str = "Free" if is_free_game else fmt_price.get('discountPrice')

                found_game = {
                    "title": game.get("title"),
                    "description": game.get("description", "No description available."),
                    "original_price": original_price_str,
                    "discounted_price": discounted_price_str,
                    "image_url": image_url,
                    "url": game_url,  # Use pre-validated URL
                    "start_date": None,
                    "end_date": None,
                    "is_free": is_free_game,
                    "is_cheap": is_cheap_game
                }
                
                cheap_games.append(found_game)
                
                if emit_callback:
                    emit_callback({'type': 'found', 'game': found_game})
        
        if emit_callback:
            emit_callback({'type': 'progress', 'processed': total_elements, 'total': total_elements})

        return cheap_games

    except Exception as e:
        err_msg = f"Error fetching cheap games: {e}"
        if emit_callback:
             emit_callback({'type': 'log', 'message': err_msg})
        logging.error(err_msg)
        return []

def send_email(free_games):
    """Send an email with details about free games."""
    if not free_games:
        logging.info("No games to notify.")
        return False  # Changed to return False instead of None

    subject = "Free & Cheap Games on Epic Games Store!"
    
    # Modern, professional, and responsive email body with a border
    body = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                padding: 20px;
                margin: 0;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background-color: #fff;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                border: 1px solid #ddd;
            }
            .header {
                text-align: center;
                color: #333;
            }
            .header h2 {
                margin: 0;
                font-size: 24px;
            }
            .content {
                margin-top: 20px;
            }
            .game {
                text-align: center;
                border-bottom: 1px solid #ddd;
                padding: 20px 0;
            }
            .game img {
                border-radius: 8px;
                max-width: 100%;
                height: auto;
            }
            .game-details {
                margin-top: 10px;
            }
            .game-details h3 {
                margin: 0;
                font-size: 18px;
                color: #333;
            }
            .game-details p {
                margin: 5px 0;
                color: #777;
                font-size: 14px;
            }
            .game-details .price {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            .game-details .price span {
                background-color: red;
                color: white;
                padding: 3px 6px;
                text-decoration: none;
                border-radius: 3px;
                font-weight: bold;
                display: inline-block;
                margin-top: 10px;
            }
            .game-details a {
                background-color: #fcb900;
                color: black;
                padding: 8px 16px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                display: inline-block;
                margin-top: 10px;
            }
            .game-details .offer-end {
                font-size: 14px;
                color: #888;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Free & Cheap Games Available on the Epic Games Store!</h2>
                <p>Don't miss out on these amazing deals:</p>
            </div>
            <div class="content">
    """
    # Build the email body with the game's details, including image, description, and price
    for game in free_games:
        date_str = ""
        if game.get("end_date"):
            end_date = format_date(game["end_date"])
            date_str = f"<i>Offer ends: {end_date}</i>"
        
        price_display = f"Price: <span style='background-color: red; color: white;'>{game['discounted_price']}</span> (was {game['original_price']})"
        if game.get("is_free"):
             price_display = f"Price: <span>Free</span> (was {game['original_price']})"
             
        body += f"""
        <div class="game">
            <img src="{game['image_url']}" alt="{game['title']}" />
            <div class="game-details">
                <h3>{game['title']}</h3>
                <p>{game['description']}</p>
                <p class="price">{price_display}</p>
                <a href="{game['url']}">{'Claim Your Free Game!' if game.get('is_free') else 'Get This Deal Now!'}</a>
                <p class="offer-end">{date_str}</p>
            </div>
        </div>
        """

    body += """
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = f"Epic Free Games Notifier <{FROM_EMAIL}>"
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    recipients = EMAILS if EMAILS else ([TO_EMAIL] if TO_EMAIL else [])
    
    if not recipients:
        logging.error("No recipients found.")
        return False

    try:
        logging.info("Connecting to SMTP server...")
        with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
            server.set_debuglevel(1)  # Enable debug logs
            server.starttls()
            logging.info("Logging in to SMTP server...")
            server.login(EMAIL, PASSWORD)
            
            for recipient in recipients:
                msg["To"] = recipient
                logging.info(f"Sending email to {recipient}...")
                server.send_message(msg)
                
            logging.info("Emails sent successfully.")
            return True  # Return True on successful send
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False  # Return False if sending fails


def manage_notification_history(games, history_file="notification_history.json", update_history=True):
    """Manage notification history to avoid duplicate notifications."""
    try:
        # Create history file if it doesn't exist
        history_path = Path(history_file)
        if not history_path.exists():
            history_path.write_text('{"notified_games": []}')

        # Read existing history
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        # Clean up old entries (older than 30 days)
        current_time = datetime.datetime.now()
        history['notified_games'] = [
            game_id for game_id in history['notified_games']
            if not _is_old_notification(game_id, current_time)
        ]
        
        # Filter out games we've already notified about
        new_games = []
        new_game_ids = []  # Store new game IDs separately
        for game in games:
            game_id = f"{game['title']}_{game['end_date']}"
            if game_id not in history['notified_games']:
                new_games.append(game)
                new_game_ids.append(game_id)
        
        # Only update history file if requested and there are new games
        if update_history and new_game_ids:
            history['notified_games'].extend(new_game_ids)
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        
        return new_games
    except Exception as e:
        logging.error(f"Error managing notification history: {e}")
        return games  # Return all games if there's an error

def _is_old_notification(game_id, current_time):
    """Check if a notification is older than 30 days."""
    try:
        # Extract end_date from game_id (format: "title_end_date")
        end_date_str = game_id.split('_')[-1]
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M:%S.000Z")
        return (current_time - end_date).days > 30
    except Exception:
        return False  # Keep entry if we can't parse the date




def run_process(callback=None):
    """
    Main execution function with callback support for web interface.
    callback(data): data is a dict with keys: type (log, progress, found), message, etc.
    """
    def emit(data):
        if callback:
            callback(data)
        if data.get('type') == 'log':
            # Mirror logs to standard logging
            lvl = data.get('level', 'info')
            if lvl == 'error':
                logging.error(data.get('message'))
            elif lvl == 'warning':
                logging.warning(data.get('message'))
            else:
                logging.info(data.get('message'))
        
    try:
        # Check environment variables first
        check_env_variables()
        
        emit({'type': 'log', 'level': 'info', 'message': "Starting scraper process..."})
        
        # 1. Fetch Weekly Free Games Only
        emit({'type': 'log', 'level': 'info', 'message': "Fetching weekly free games..."})
        free_games = fetch_free_games() or []
        for g in free_games:
            emit({'type': 'found', 'game': g})
        emit({'type': 'progress', 'processed': len(free_games), 'total': len(free_games)})
        
        if free_games:
            # First check for new games without updating history
            new_games = manage_notification_history(free_games, update_history=False)
            
            if new_games:
                emit({'type': 'log', 'level': 'success', 'message': f"Found {len(new_games)} new games to notify! Sending email..."})
                if send_email(new_games):
                    # Only update history if email was sent successfully
                    manage_notification_history(new_games)
                    emit({'type': 'log', 'level': 'success', 'message': "Email sent and history updated."})
                    emit({'type': 'status', 'status': 'success'})
                else:
                    emit({'type': 'log', 'level': 'warning', 'message': "Email failed to send."})
                    emit({'type': 'status', 'status': 'error'})
            else:
                emit({'type': 'log', 'level': 'info', 'message': "No new games (all already notified)."})
                emit({'type': 'status', 'status': 'success'})
        else:
            emit({'type': 'log', 'level': 'info', 'message': "No interesting games found this run."})
            emit({'type': 'status', 'status': 'success'})

    except Exception as e:
        emit({'type': 'error', 'message': str(e)})
        emit({'type': 'log', 'level': 'error', 'message': f"FAILED: {e}"})
        logging.error(f"Script failed: {e}")

def force_send_notifications(callback=None):
    """Force send notifications for all current free games, bypassing history check"""
    load_settings()
    
    def emit(data):
        if callback:
            callback(data)
        else:
            print(f"[{data.get('type', 'log')}] {data.get('message', data)}")
    
    try:
        emit({'type': 'log', 'level': 'info', 'message': "Force sending notifications..."})
        emit({'type': 'log', 'level': 'info', 'message': "Fetching current free games..."})
        
        free_games = fetch_free_games() or []
        for g in free_games:
            emit({'type': 'found', 'game': g})
        emit({'type': 'progress', 'processed': len(free_games), 'total': len(free_games)})
        
        if free_games:
            emit({'type': 'log', 'level': 'success', 'message': f"Sending email for {len(free_games)} games..."})
            if send_email(free_games):
                manage_notification_history(free_games)
                emit({'type': 'log', 'level': 'success', 'message': f"Email sent successfully to {len(EMAILS)} recipient(s)!"})
                emit({'type': 'status', 'status': 'success'})
            else:
                emit({'type': 'log', 'level': 'error', 'message': "Failed to send email. Check SMTP settings in .env file."})
                emit({'type': 'status', 'status': 'error'})
        else:
            emit({'type': 'log', 'level': 'warning', 'message': "No free games available to notify about."})
            emit({'type': 'status', 'status': 'success'})
            
    except Exception as e:
        emit({'type': 'error', 'message': str(e)})
        emit({'type': 'log', 'level': 'error', 'message': f"FAILED: {e}"})
        logging.error(f"Force send failed: {e}")


def main():
    """CLI entry point"""
    load_settings()
    run_process()



if __name__ == "__main__":
    main()
