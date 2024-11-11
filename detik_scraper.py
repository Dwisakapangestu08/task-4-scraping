from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Fungsi untuk melakukan scraping
def scrape_detik_search(query, max_pages=3):
    results = []
    base_url = "https://www.detik.com/search/searchall?query={}&page={}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Looping melalui beberapa halaman
    for page in range(1, max_pages + 1):
        try:
            # Permintaan HTTP
            url = base_url.format(query, page)
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all("article")

            for article in articles:
                try:
                    title = article.find("h3").get_text(strip=True)
                    image_tag = article.find("img")
                    image_link = image_tag["src"] if image_tag else "No image available"
                    body_text = article.select_one("div.media__desc").get_text(strip=True) if article.select_one("div.media__desc") else "No description available"
                    pub_time = article.select_one("div.media__date").get_text(strip=True) if article.select_one("div.media__date") else "No publication time"

                    results.append({
                        "title": title,
                        "image_link": image_link,
                        "body_text": body_text,
                        "publication_time": pub_time
                    })
                except (AttributeError, KeyError):
                    continue

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

    return results

# Endpoint untuk melakukan scraping
@app.route('/scrape', methods=['GET'])
def scrape():
    query = request.args.get('query')
    if not query:
        return "<h3>Error: Query parameter is required</h3>", 400

    results = scrape_detik_search(query)
    # return render_template('template.html', query=query, results=results)
    return results

# Menjalankan aplikasi
if __name__ == "__main__":
    app.run(debug=True)
