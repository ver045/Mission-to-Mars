from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import time 
import re

def mars_news(browser):
    try:
        url = "https://mars.nasa.gov/news/"
        browser.visit(url)

        #get first list item adn wait half a second if not immediately presented 
        browser.is_element_present_by_css("ul.item_list li.slide", wait_time = 5)

        html = browser.html
        news_soup = BeautifulSoup(html, "html.parser")

        news_title = news_soup.find("div", class_ = "content_title").text
        news_p = news_soup.find("div", class_ = "article_teaser_body").text

    except AttributeError:
        return None, None
        
    return news_title, news_p

def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    #find and click the full images button 
    full_image_button = browser.find_by_css('.button.fancybox')
    full_image_button.click()

    #find the more info button and click that 
    more_info_button = browser.links.find_by_partial_text('more info')
    more_info_button.click()

    #parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, "html.parser")

    #find the relative image urls 
    img = img_soup.find('img', class_='main_image')['src']
    
    img_url = f'https://www.jpl.nasa.gov{img}'
    return img_url 

def hemisphere(browser):
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)

    hemisphere_image_urls = []
    links = browser.find_by_css('a.product-item h3')
    print(links)

    for i in range(len(links)):
        hemisphere = {}
        browser.find_by_css("a.product-item h3")[i].click()
        sample_elem = browser.find_link_by_text('Sample').first
        hemisphere['img_url'] = sample_elem['href']
        hemisphere['title'] = browser.find_by_css('h2.title').text
    
        hemisphere_image_urls.append(hemisphere)
        browser.back()

    return hemisphere_image_urls

def twitter_weather(browser):
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    time.sleep(5)

    html = browser.html
    weather_soup = BeautifulSoup(html, 'html.parser')

    mars_weather_tweet = weather_soup.find('div', attrs={'class':'tweets','data-name':'Mars Weather'})

    try:
        mars_weather = mars_weather_tweet.find('p', 'tweet-text').get_text()
    except AttributeError:
        pattern = re.compile(r'sol')
        mars_weather = weather_soup.find('span', text=pattern).text

    return mars_weather

def mars_facts():
    try:
        df = pd.read_html("https://space-facts.com/mars/")[0]
    except BaseException:
        return None
    df.columns=["description", "value"]
    df.set_index("description", inplace=True)

    return df.to_html(classes="table table-striped")

def scrape_all():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph = mars_news(browser)
    
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemisphere": hemisphere(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    browser.quit()

    return data
    

if __name__ == "__main__":
    # if running has a script print scraped data
    print (scrape_all())

