import os
from flask import Flask, request, jsonify
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from scraper_api import ScraperAPIClient

app = Flask(__name__)

@app.route('/')
def check_noindex():
    url = request.args.get('url')

    # Initialize Chrome browser with Scraper API options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    client = ScraperAPIClient(os.environ.get('SCRAPER_API_KEY'))
    client_params = {'url': url, 'render': 'true'}
    print(client," ",client_params)
    if client:
        response = client.get(client_params)
        if response.status_code == 200:
            html = response.content
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
            driver.get('data:text/html;charset=utf-8,' + html)
        else:
            return jsonify({'error': f'Request failed with status code {response.status_code}'})
    else:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(url)

    try:
        # Get the meta robots value
        meta_robots = driver.execute_script('return document.querySelector("meta[name=\'robots\']")?.getAttribute("content")')

        # Get the response status code
        status_code = driver.execute_script('return window.performance.getEntriesByType("navigation")[0]?.response?.status || null')
    except WebDriverException as e:
        # Handle the WebDriverException error here
        driver.quit()
        return jsonify({'error': str(e)})
    finally:
        # Quit the Chrome browser
        driver.quit()

    # Return the result in JSON format, including the error message if any
    if meta_robots is not None:
        return jsonify({'noindex': meta_robots, 'status_code': status_code})
    else:
        return jsonify({'error': 'Unable to find the meta robots tag'})

if __name__ == '__main__':
    app.run()
