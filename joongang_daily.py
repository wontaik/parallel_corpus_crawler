import sys, time, codecs, re

from selenium import webdriver
from bs4 import BeautifulSoup

INTERVAL = 3

BASE_URL = 'http://koreajoongangdaily.joins.com'
URL = BASE_URL + '/news/list/List.aspx?gCat=060201&pgi=%d'
ARTICLE_SELECTOR = 'div > ul > li > dl > dd > a'
DATE_SELECTOR = 'div > ul > li > dl > dd > span'
TITLE_SELECTOR = '#sTitle_a'
CONTENT_SELECTOR = 'div > div.article_content'
ALT_CONTENT_SELECTOR = 'div.article_dvleft > div > table > tbody > tr > td > font'

def get_content(url, driver_path):
    driver = webdriver.PhantomJS(driver_path)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.close()
    time.sleep(INTERVAL)

    title = soup.select(TITLE_SELECTOR)[0].text.strip()
    en_content = soup.select(CONTENT_SELECTOR)[0].text.strip()
    ko_content = soup.select(CONTENT_SELECTOR)[1].text.strip()

    if ko_content == '':
        en_content = soup.select(ALT_CONTENT_SELECTOR)[0].text.strip()
        ko_content = soup.select(ALT_CONTENT_SELECTOR)[-1].text.strip()

    en_content = re.sub('\\n', '', en_content)
    ko_content = re.sub('\\n', '', ko_content)

    print(title)
    print(en_content)
    print(ko_content)

    return title, en_content, ko_content

def get_article_urls(url, driver_path):
    driver = webdriver.PhantomJS(driver_path)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    articles = [s.get('href').strip() for s in soup.select(ARTICLE_SELECTOR)][-10:]
    
    driver.close()
    time.sleep(INTERVAL)

    return articles

def write(title, en, ko, output_fn):
    f = open(output_fn, 'a')

    f.write("%s\t%s\t%s\n" % (title, en, ko))

    f.close()

if __name__ == "__main__":
    output_fn = sys.argv[1]
    driver_path = './phantomjs'

    memory = []
    page_index = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    while True:
        url = URL % page_index
        print(url)
        article_urls = get_article_urls(url, driver_path)

        if len(article_urls) == 0:
            break
        
        for a_url in article_urls:
            try:
                title, en, ko = get_content(BASE_URL + a_url, driver_path)

                if title not in memory:
                    write(title, en, ko, output_fn)
            except:
                print('Error.')

        page_index += 1
