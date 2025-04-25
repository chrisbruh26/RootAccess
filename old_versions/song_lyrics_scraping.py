import requests
from bs4 import BeautifulSoup

def get_song_stats(song_url):
    """
    Scrape BPM, valence, and energy information from a stats.fm song page.
    Args:
        song_url (str): URL of the song page on stats.fm
    Returns:
        dict: Dictionary with keys 'bpm', 'valence', 'energy' and their values as floats or None if not found
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
    }
    response = requests.get(song_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: status code {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    stats = {
        'bpm': None,
        'valence': None,
        'energy': None
    }

    # Extract BPM from the ul with class "mt-12 grid w-full grid-cols-2 gap-4 lg:grid-cols-3"
    bpm_ul = soup.find('ul', class_='mt-12 grid w-full grid-cols-2 gap-4 lg:grid-cols-3')
    if bpm_ul:
        # Find the li where the span text is "BPM"
        for li in bpm_ul.find_all('li'):
            span = li.find('span')
            h1 = li.find('h1')
            if span and h1 and span.get_text(strip=True).lower() == 'bpm':
                try:
                    stats['bpm'] = float(h1.get_text(strip=True))
                except ValueError:
                    stats['bpm'] = None
                break

    # Extract valence and energy from the ul with class "mt-8 grid w-full grid-cols-2 items-stretch gap-4 gap-y-5"
    stats_ul = soup.find('ul', class_='mt-8 grid w-full grid-cols-2 items-stretch gap-4 gap-y-5')
    if stats_ul:
        for li in stats_ul.find_all('li'):
            span_label = li.find('span', class_='mb-1 capitalize')
            div_outer = li.find('div', class_='h-2 appearance-none overflow-hidden rounded-full bg-foreground')
            if span_label and div_outer:
                label_text = span_label.get_text(strip=True).lower()
                div_inner = div_outer.find('span', class_='block h-full rounded-full bg-primary')
                if div_inner and 'style' in div_inner.attrs:
                    style = div_inner['style']
                    # style example: "width: 42.3%;"
                    try:
                        width_percent = float(style.split('width:')[1].split('%')[0].strip())
                        value = width_percent / 100.0
                    except (IndexError, ValueError):
                        value = None
                    if label_text == 'valence':
                        stats['valence'] = value
                    elif label_text == 'energy':
                        stats['energy'] = value

    return stats

def get_lyrics(song_url):
    """
    Scrape lyrics from an azlyrics.com song page.
    Args:
        song_url (str): URL of the song page on azlyrics.com
    Returns:
        str: The lyrics as a string, or None if not found
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
    }
    response = requests.get(song_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: status code {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the <body> element with class "az-song-text" # class="Lyrics__Container-sc-78fb6627-1 hiRbsH"
    lyrics_body = soup.find('div', class_='Lyrics__Container-sc-78fb6627-1 hiRbsH')
    if lyrics_body:
        return lyrics_body.get_text(strip=True, separator='\n')  # Extract text with line breaks
    else:
        return None

if __name__ == "__main__":
    # Example usage: replace with a real song URL from Genius.com
    example_song_url = "https://genius.com/Ice-nine-kills-stabbing-in-the-dark-lyrics"
    try:
        lyrics = get_lyrics(example_song_url)
        if lyrics:
            print(f"Lyrics for {example_song_url}:\n")
            print(lyrics)
            
            # Append lyrics to a text file
            with open("scraped_lyrics.txt", "a", encoding="utf-8") as lyrics_file:
                lyrics_file.write(lyrics + "\n\n")  # Add a newline for separation
            print("Lyrics successfully appended to 'scraped_lyrics.txt'.")
        else:
            print(f"No lyrics found for {example_song_url}.")
    except Exception as e:
        print(f"Error: {e}")

