from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from decouple import config
import time
from flask import Flask, request, jsonify
from flask import make_response
from flask import abort

app = Flask(__name__)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Jobs not found'}), 404)

@app.route('/joker/api/v1.0/job', methods=['GET'])
def search_job():
    if not 'title' in request.args or not 'place' in request.args or not request.args:
        abort(400)
    try:
        title = request.args['title']
        place = request.args['place']
        
        driver = webdriver.Chrome(config("CHROME_WEBDRIVER_PATH"), chrome_options=chrome_options)
        driver.get("https://www.linkedin.com/home")

        job = driver.find_elements_by_css_selector("input[name='keywords']")
        job_text = [f.get_attribute("aria-label") for f in job]
        print(job_text)
        
        location = driver.find_elements_by_css_selector("input[name='location']")
        location_text = [f.get_attribute("aria-label") for f in location]
        print(location_text)

        driver.execute_script("arguments[0].value='%s'" % title, job[1])
        driver.execute_script("arguments[0].value='%s'" % place, location[1])

        btn = driver.find_elements_by_css_selector("button.search__button")
        driver.execute_script("arguments[0].click()", btn[1])

        #scroll(driver, 2)

        jobs = scrap_job(driver)
        return jsonify(jobs), 200
    except IndexError as e:
        return jsonify(e), 500

def scroll(driver, timeout):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(timeout)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if last_height == new_height:
            break

        last_height = new_height

def scrap_job(driver):
    jobs = driver.find_elements_by_css_selector("li.result-card")
    jobs_data = []
    
    for job in jobs:
        job_title = job.find_element_by_css_selector("h3.result-card__title").text
        company = job.find_element_by_css_selector("h4.result-card__subtitle").text
        location = job.find_element_by_css_selector("div.result-card__meta > span").text
        link = job.find_element_by_css_selector("a").get_attribute("href")
        time_posted = job.find_element_by_css_selector("div.result-card__meta > time").text
        #img = job.find_element_by_css_selector("a + img").get_attribute("src")

        dict_job = {
            "title": job_title,
            "company": company,
            "location": location,
            "url": link,
            "time_posted": time_posted,
            #"img": img
        }
        jobs_data.append(dict_job)

    return jobs_data

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)