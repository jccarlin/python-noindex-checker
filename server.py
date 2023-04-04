import os
import pyppeteer
import asyncio
from flask import Flask, request, jsonify

browserless_api_key = os.getenv('BROWSERLESS_API_KEY')
print(browserless_api_key)

app = Flask(__name__)

@app.route('/check_noindex')
def check_noindex():
    url = request.args.get('url')
    if not url:
        return jsonify(error='Missing "url" parameter'), 400

    async def run_check():
        browser = await pyppeteer.launcher.connect(
            browserWSEndpoint='wss://chrome.browserless.io?token='+browserless_api_key
        )
        page = await browser.newPage()
        await page.goto(url)
        try:
            # Get the meta robots value
            meta_robots = await page.evaluate('''() => {
                const tag = document.querySelector('meta[name="robots"]');
                return tag ? tag.getAttribute("content") : null;
            }''')
            # Get the response status code
            await page.waitForNavigation({'waitUntil': 'domcontentloaded'})
            response = await page.goto(url)
            status_code = response.status
        except pyppeteer.errors.NetworkError as e:
            # Handle the NetworkError error here
            print(e)  # print the exception message
            await browser.close()
            return {'error': str(e)}
        finally:
            # Close the Pyppeteer browser
            await browser.close()

        # Return the result in a dictionary format, including the error message if any
        if meta_robots is not None:
            return {'noindex': meta_robots, 'status_code': status_code}
        else:
            return {'error': 'Unable to find the meta robots tag'}

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(run_check())
    return jsonify(result)

if __name__ == '__main__':
    app.run()
