import os
import requests
import mwclient
from datetime import datetime
import re
import time

# Configuration
STEAM_GAME_ID = '1022980'  # Ostranauts game ID
MEDIAWIKI_URL = 'ostranauts.wiki.gg/api.php'  # Full MediaWiki URL with /api.php
MEDIAWIKI_USERNAME = os.getenv('WIKI_USERNAME')  # Retrieve from environment variable
MEDIAWIKI_PASSWORD = os.getenv('WIKI_PASSWORD')  # Retrieve from environment variable
WIKI_PAGE_TEMPLATE = 'Updates/{title}'  # Use title for page template

# Delay between API requests
DELAY_BETWEEN_REQUESTS = 2  # 2 seconds delay between requests to Steam API

# Function to get Steam updates with pagination (single request at a time)
def get_steam_updates(game_id, count=100, skip=0):
    url = f'https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/'
    params = {
        'appid': game_id,
        'count': count,  # Fetch multiple updates
        'offset': skip,  # Offset for pagination
        'format': 'json'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check for HTTP errors
        print(f"Steam API responded with status code {response.status_code}")

        news_data = response.json().get('appnews', {}).get('newsitems', [])
        if news_data:
            return news_data
        else:
            print("No updates found.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching updates from Steam: {e}")
    return []

# Function to extract and format sections in the update
def extract_sections(contents, section_title="New Stuff"):
    sections = re.findall(r'\[list\](.*?)\[/list\]', contents, re.DOTALL)
    if sections:
        formatted_sections = ""
        for section in sections:
            list_items = section.split('[*]')
            formatted_items = "\n".join(f"* {item.strip()}" for item in list_items if item.strip())
            formatted_sections += f"{{{{Section|{section_title}|\n{formatted_items}\n}}}}\n"
        return formatted_sections
    return ""

# Function to replace Steam images with MediaWiki images and update section title if needed
def replace_images(content):
    # Define the Steam image reference for "General Changes"
    steam_general_changes_image = "[img]{STEAM_CLAN_IMAGE}/34518042/30853f662c2747b1366e56ad5f761393180fa43e.png[/img]"
    wiki_general_changes_image = "[[File:General_changes.png]]"
    section_title = "New Stuff"

    # Check if the Steam image matches the "General Changes" image
    if steam_general_changes_image in content:
        content = content.replace(steam_general_changes_image, wiki_general_changes_image)
        section_title = "General Changes"

    return content, section_title

# Function to clean up line breaks but preserve paragraphs
def remove_extra_line_breaks(content):
    # Preserve single line breaks while avoiding multiple blank lines
    content = re.sub(r'\n\s*\n', '\n\n', content)
    return content.strip()

# Function to format the update for MediaWiki
def format_for_mediawiki(update, previous_version, next_version):
    title = update.get('title', 'Update')
    contents = update.get('contents', '').strip()

    # Convert Unix timestamp to human-readable date
    release_timestamp = update.get('date', 0)  # Extract the Unix timestamp from the Steam API response
    release_date = datetime.utcfromtimestamp(release_timestamp).strftime('%Y-%m-%d')  # Convert to YYYY-MM-DD

    # Check if the update is a hotfix
    hotfix = is_hotfix(title, contents)

    # Extract the version from the title, fallback to the date if version is missing
    version_match = re.search(r'\((.*?)\)', title)
    version_or_date = version_match.group(1) if version_match else release_date

    # Extract the Steam URL for the reference
    steam_url = update.get('url', '#')  

    # Replace image references and get section title
    formatted_content, section_title = replace_images(contents)

    # Extract and format sections with the correct section title
    new_stuff_sections = extract_sections(formatted_content, section_title)
    
    # Insert the new stuff section in the same place it appears in the Steam announcement
    formatted_content = re.sub(r'\[list\](.*?)\[/list\]', new_stuff_sections, formatted_content, flags=re.DOTALL)

    # Clean up line breaks but preserve paragraph structure
    formatted_content = remove_extra_line_breaks(formatted_content)

    # Conditionally include the name in the infobox if it's NOT a hotfix
    name_field = f"|Name = {title}\n" if not hotfix else f"|Name ="

    # Handle the "None" case for the Previous/Next versions properly
    previous_version = previous_version if previous_version else "???"
    next_version = next_version if next_version else ""

    # Format the update content for MediaWiki
    formatted_text = f"""{{{{DISPLAYTITLE:Update {version_or_date}}}}}
{{{{Infobox Update|
|Release = {release_date}
{name_field}|Hotfix={str(hotfix).lower()}
|Next = {previous_version}
|Previous = {next_version}
|updateid = {update.get('gid', 'Unknown')}
}}}}

The Update {version_or_date} <ref>{steam_url}</ref> was released on {{{{#dateformat:{release_date}|mdy}}}}.

{formatted_content}
"""
    return formatted_text

# Function to check if the update is a hotfix
def is_hotfix(title, contents):
    keywords = ["hotfix", "patch"]
    for keyword in keywords:
        if keyword.lower() in title.lower() or keyword.lower() in contents.lower():
            return True
    return False

# Function to post updates to MediaWiki (now only authenticating once and checking if the page exists)
def post_update_to_mediawiki(site, update, previous_version, next_version):
    try:
        title = update.get('title', 'Update')
        version_match = re.search(r'\((.*?)\)', title)
        version_or_date = version_match.group(1) if version_match else datetime.utcfromtimestamp(update.get('date')).strftime('%Y-%m-%d')
        page_name = WIKI_PAGE_TEMPLATE.format(title=version_or_date)

        # Check if the page already exists
        page = site.pages[page_name]
        if page.exists:
            print(f"Page {page_name} already exists, skipping...")
            return True  # Return True to indicate the page exists and the script should stop

        # Create the new page with the formatted update text
        formatted_update_text = format_for_mediawiki(update, previous_version, next_version)
        page.save(formatted_update_text, summary='Automatic update from Steam')
        print(f"Successfully posted update to {page_name}")
        return False  # Return False to indicate the script should continue
    except mwclient.errors.LoginError as e:
        print(f"MediaWiki login failed: {e}")
        return False
    except Exception as e:
        print(f"Error posting to MediaWiki: {e}")
        return False

# Function to check and update all available updates from Steam, processing them one by one
def check_and_update_all():
    offset = 0
    count = 100  # Fetch 100 updates at a time
    previous_version = None  # To store the previous version for the next update
    next_version = None  # To store the version of the next update
    following_version = None  # Store the version after the next update (second update in the future)

    # Authenticate with MediaWiki once
    try:
        site = mwclient.Site(MEDIAWIKI_URL)
        site.login(MEDIAWIKI_USERNAME, MEDIAWIKI_PASSWORD)
        print("Logged into MediaWiki")
    except mwclient.errors.LoginError as e:
        print(f"MediaWiki login failed: {e}")
        return

    while True:
        updates = get_steam_updates(STEAM_GAME_ID, count=count, skip=offset)
        if not updates:
            break  # No more updates to process

        # Process each update individually before making the next API request
        for idx, update in enumerate(updates):
            # Extract the version from the current update
            version_match = re.search(r'\((.*?)\)', update.get('title', ''))
            current_version = version_match.group(1) if version_match else datetime.utcfromtimestamp(update.get('date')).strftime('%Y-%m-%d')

            # Check the next two updates for their versions (if available)
            if idx + 1 < len(updates):
                next_version_match = re.search(r'\((.*?)\)', updates[idx + 1].get('title', ''))
                next_version = next_version_match.group(1) if next_version_match else ""

            if idx + 2 < len(updates):
                following_version_match = re.search(r'\((.*?)\)', updates[idx + 2].get('title', ''))
                following_version = following_version_match.group(1) if following_version_match else ""

            # Post the update to MediaWiki using the existing authenticated session
            if post_update_to_mediawiki(site, update, previous_version, next_version):
                print(f"Update {current_version} already exists. Ending script.")
                return  # Terminate the script if a page already exists

            # After posting, set current_version as the previous_version for the next iteration
            previous_version = current_version

        # Increment the offset and delay before the next request
        offset += count
        time.sleep(DELAY_BETWEEN_REQUESTS)  # Respectful delay between API requests

# Run the script on-demand
if __name__ == '__main__':
    check_and_update_all()

