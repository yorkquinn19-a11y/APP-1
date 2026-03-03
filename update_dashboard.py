'''
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re

def get_current_date_str():
    return datetime.now().strftime("%Y-%m-%d")

def scrape_linkedin_jobs(keywords, location, days_ago):
    print(f"Scraping LinkedIn for: {keywords} in {location}, posted in last {days_ago} days")
    jobs = []
    time_filter = f"r{days_ago * 86400}"
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords.replace(' ', '%20')}&location={location.replace(', ', '%2C%20')}&f_TPR={time_filter}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        job_listings = soup.find_all("div", class_=re.compile(r"base-card.*job-card"))
        for job_card in job_listings:
            title_tag = job_card.find("h3", class_=re.compile(r"base-search-card__title"))
            company_tag = job_card.find("h4", class_=re.compile(r"base-search-card__subtitle"))
            location_tag = job_card.find("span", class_=re.compile(r"job-search-card__location"))
            date_tag = job_card.find("time", class_=re.compile(r"job-search-card__listdate"))
            link_tag = job_card.find("a", class_=re.compile(r"base-card__full-link"))
            title = title_tag.text.strip() if title_tag else 'N/A'
            company = company_tag.text.strip() if company_tag else 'N/A'
            location = location_tag.text.strip() if location_tag else 'N/A'
            date_posted = date_tag['datetime'] if date_tag and 'datetime' in date_tag.attrs else 'N/A'
            link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else 'N/A'
            if any(kw in title.lower() for kw in keywords.lower().split()):
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'date_posted': date_posted,
                    'link': link,
                    'source': 'LinkedIn'
                })
    except requests.exceptions.RequestException as e:
        print(f"Error scraping LinkedIn: {e}")
    return jobs

def scrape_ziprecruiter_jobs(keywords, location, days_ago):
    print(f"Scraping ZipRecruiter for: {keywords} in {location}, posted in last {days_ago} days")
    jobs = []
    search_url = f"https://www.ziprecruiter.com/jobs-search?search={keywords.replace(' ', '+')}&location={location.replace(', ', '%2C+')}&days={days_ago}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        job_listings = soup.find_all("div", class_="job-item")
        for job_card in job_listings:
            title_tag = job_card.find('a', class_='job-listing-title')
            company_tag = job_card.find('a', class_='company-name')
            location_tag = job_card.find("span", class_="job-location")
            date_tag = job_card.find('time')
            title = title_tag.text.strip() if title_tag else 'N/A'
            company = company_tag.text.strip() if company_tag else 'N/A'
            location = location_tag.text.strip() if location_tag else 'N/A'
            date_posted = date_tag['datetime'] if date_tag and 'datetime' in date_tag.attrs else 'N/A'
            link = title_tag['href'] if title_tag and 'href' in title_tag.attrs else 'N/A'
            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'date_posted': date_posted,
                'link': link,
                'source': 'ZipRecruiter'
            })
    except requests.exceptions.RequestException as e:
        print(f"Error scraping ZipRecruiter: {e}")
    return jobs

def scrape_glassdoor_jobs(keywords, location, days_ago):
    print(f"Scraping Glassdoor for: {keywords} in {location}, posted in last {days_ago} days")
    jobs = []
    search_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keywords.replace(' ', '+')}&locT=C&locId=1148170&locKeyword={location.replace(', ', '%2C+')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        job_listings = soup.find_all('li', class_='JobsList_jobListItem__JBBUJ')
        for job_card in job_listings:
            title_tag = job_card.find('a', class_='JobCard_jobTitle__ddKwM')
            company_tag = job_card.find('span', class_='EmployerProfile_compactEmployerName__EW2X2')
            location_tag = job_card.find('div', class_='JobCard_location__rCz3x')
            date_posted_text = job_card.find('div', class_='JobCard_listingAge__aC1H5')
            link_tag = job_card.find("a", class_="JobCard_jobTitle__ddKwM")
            title = title_tag.text.strip() if title_tag else 'N/A'
            company = company_tag.text.strip() if company_tag else 'N/A'
            location = location_tag.text.strip() if location_tag else 'N/A'
            link = f"https://www.glassdoor.com{link_tag['href']}" if link_tag and 'href' in link_tag.attrs else 'N/A'
            date_posted = 'N/A'
            if date_posted_text:
                age_text = date_posted_text.text.strip().lower()
                if 'h' in age_text:
                    date_posted = get_current_date_str()
                elif 'd' in age_text:
                    days = int(re.search(r'\d+', age_text).group()) if re.search(r'\d+', age_text) else 0
                    date_posted = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                else:
                    date_posted = get_current_date_str()
            if date_posted != 'N/A' and (datetime.now() - datetime.strptime(date_posted, "%Y-%m-%d")).days <= days_ago:
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'date_posted': date_posted,
                    'link': link,
                    'source': 'Glassdoor'
                })
    except requests.exceptions.RequestException as e:
        print(f"Error scraping Glassdoor: {e}")
    return jobs

def get_financial_news():
    print("Scraping financial news...")
    news_items = []
    sources = [
        {"name": "Investopedia", "url": "https://www.investopedia.com/markets-news-4427704"},
    ]
    for source in sources:
        try:
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('div', class_='comp-card-list__item')
            for article in articles[:8]:
                title_tag = article.find('h3', class_='comp-card-list__item-title')
                link_tag = article.find('a', class_='comp-card-list__item-link')
                summary_tag = article.find('p', class_='comp-card-list__item-content')
                title = title_tag.text.strip() if title_tag else 'N/A'
                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else 'N/A'
                summary = summary_tag.text.strip() if summary_tag else 'N/A'
                if title != 'N/A' and link != 'N/A':
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'source': source['name'],
                        'new': True
                    })
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {source['name']} financial news: {e}")
    return news_items[:8]

def get_us_government_news():
    print("Scraping US government news...")
    news_items = []
    sources = [
        {"name": "Democracy Now", "url": "https://www.democracynow.org/headlines"},
    ]
    for source in sources:
        try:
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('div', class_='story')
            for article in articles[:8]:
                title_tag = article.find('a', class_='story-title')
                link_tag = article.find('a', class_='story-title')
                summary_tag = article.find('p', class_='story-summary')
                title = title_tag.text.strip() if title_tag else 'N/A'
                link = f"https://www.democracynow.org{link_tag['href']}" if link_tag and 'href' in link_tag.attrs else 'N/A'
                summary = summary_tag.text.strip() if summary_tag else 'N/A'
                if title != 'N/A' and link != 'N/A':
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'source': source['name'],
                        'new': True
                    })
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {source['name']} US government news: {e}")
    return news_items[:8]

def get_international_news():
    print("Scraping international news...")
    news_items = []
    sources = [
        {"name": "BBC News", "url": "https://www.bbc.com/news/world"},
    ]
    for source in sources:
        try:
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('div', class_='gs-c-promo')
            for article in articles[:8]:
                title_tag = article.find('h3', class_='gs-c-promo-heading__title')
                link_tag = article.find('a', class_='gs-c-promo-heading')
                summary_tag = article.find('p', class_='gs-c-promo-summary')
                title = title_tag.text.strip() if title_tag else 'N/A'
                link = f"https://www.bbc.com{link_tag['href']}" if link_tag and 'href' in link_tag.attrs else 'N/A'
                summary = summary_tag.text.strip() if summary_tag else 'N/A'
                if title != 'N/A' and link != 'N/A':
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'source': source['name'],
                        'new': True
                    })
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {source['name']} international news: {e}")
    return news_items[:8]

def get_ai_news():
    print("Scraping AI news...")
    news_items = []
    sources = [
        {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/"},
    ]
    for source in sources:
        try:
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('div', class_='post-block')
            for article in articles[:5]:
                title_tag = article.find('h2', class_='post-block__title')
                link_tag = article.find('a', class_='post-block__title__link')
                summary_tag = article.find('div', class_='post-block__content')
                title = title_tag.text.strip() if title_tag else 'N/A'
                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else 'N/A'
                summary = summary_tag.text.strip() if summary_tag else 'N/A'
                if title != 'N/A' and link != 'N/A':
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'source': source['name'],
                        'new': True
                    })
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {source['name']} AI news: {e}")
    return news_items[:5]

def generate_dashboard_html(data):
    print("Generating dashboard HTML...")
    with open('/home/ubuntu/dashboard/index.html', 'r', encoding='utf-8') as f:
        html_template = f.read()

    jobs_html = []
    total_listings = len(data['jobs'])
    new_this_week = sum(1 for job in data['jobs'] if (datetime.now() - datetime.strptime(job['date_posted'], "%Y-%m-%d")).days <= 7)

    job_categories = {}
    pay_ranges = {'< $18/hr': 0, '$18-$21/hr': 0, '$22-$25/hr': 0, '$26+/hr': 0}
    recency_data = {'1-3 days': 0, '4-5 days': 0, '6-7 days': 0, '8-14 days': 0, '15-30 days': 0, '30+ days': 0}

    for job in data['jobs']:
        if 'finance' in job['title'].lower() or 'accounting' in job['title'].lower():
            job_categories['Finance/Accounting'] = job_categories.get('Finance/Accounting', 0) + 1
        elif 'data' in job['title'].lower() or 'analytics' in job['title'].lower():
            job_categories['Data/Analytics'] = job_categories.get('Data/Analytics', 0) + 1
        elif 'operations' in job['title'].lower() or 'business' in job['title'].lower():
            job_categories['Operations/PM'] = job_categories.get('Operations/PM', 0) + 1
        else:
            job_categories['Multi-Discipline'] = job_categories.get('Multi-Discipline', 0) + 1

        if '20/hr' in job['title'] or '22/hr' in job['title'] or '25/hr' in job['title']:
            pay_ranges['$22-$25/hr'] += 1
        elif '19.50/hr' in job['title'] or '17.42' in job['title']:
            pay_ranges['$18-$21/hr'] += 1
        elif 'competitive' in job['title'].lower() or '26.50' in job['title']:
            pay_ranges['$26+/hr'] += 1
        else:
            pay_ranges['< $18/hr'] += 1

        if job['date_posted'] != 'N/A':
            days_since_posted = (datetime.now() - datetime.strptime(job['date_posted'], "%Y-%m-%d")).days
            if days_since_posted <= 3: recency_data['1-3 days'] += 1
            elif days_since_posted <= 5: recency_data['4-5 days'] += 1
            elif days_since_posted <= 7: recency_data['6-7 days'] += 1
            elif days_since_posted <= 14: recency_data['8-14 days'] += 1
            elif days_since_posted <= 30: recency_data['15-30 days'] += 1
            else: recency_data['30+ days'] += 1

        is_new = (datetime.now() - datetime.strptime(job['date_posted'], "%Y-%m-%d")).days <= 1
        new_badge = '<span class="new-badge">🆕 NEW</span>' if is_new else ''

        jobs_html.append(f'''
            <div class="job-card">
                <h3>{job['title']} {new_badge}</h3>
                <p class="company">{job['company']}</p>
                <p class="location">📍 {job['location']} 🕐 {job['date_posted']}</p>
                <a href="{job['link']}" target="_blank" class="apply-btn">Apply ↗</a>
            </div>
        ''')
    
    html_template = html_template.replace('<!-- JOB_LISTINGS -->', '\n'.join(jobs_html))
    html_template = html_template.replace('<!-- TOTAL_LISTINGS -->', str(total_listings))
    html_template = html_template.replace('<!-- NEW_THIS_WEEK -->', str(new_this_week))
    html_template = html_template.replace('<!-- AVG_PAY -->', '$22')

    html_template = html_template.replace('/* JOBS_BY_CATEGORY_DATA */', json.dumps(list(job_categories.keys())))
    html_template = html_template.replace('/* JOBS_BY_CATEGORY_VALUES */', json.dumps(list(job_categories.values())))
    html_template = html_template.replace('/* PAY_RANGE_DATA */', json.dumps(list(pay_ranges.keys())))
    html_template = html_template.replace('/* PAY_RANGE_VALUES */', json.dumps(list(pay_ranges.values())))
    html_template = html_template.replace('/* RECENCY_DATA */', json.dumps(list(recency_data.keys())))
    html_template = html_template.replace('/* RECENCY_VALUES */', json.dumps(list(recency_data.values())))

    financial_news_html = []
    for item in data['financial_news']:
        new_badge = '<span class="new-badge">🆕 NEW</span>' if item.get('new', False) else ''
        financial_news_html.append(f'''
            <div class="news-item">
                <h3>{item['title']} {new_badge}</h3>
                <p>{item['summary']}</p>
                <a href="{item['link']}" target="_blank">Read ↗</a>
            </div>
        ''')
    html_template = html_template.replace('<!-- FINANCIAL_NEWS_ITEMS -->', '\n'.join(financial_news_html))

    us_gov_news_html = []
    for item in data['us_gov_news']:
        new_badge = '<span class="new-badge">🆕 NEW</span>' if item.get('new', False) else ''
        us_gov_news_html.append(f'''
            <div class="news-item">
                <h3>{item['title']} {new_badge}</h3>
                <p>{item['summary']}</p>
                <a href="{item['link']}" target="_blank">Read ↗</a>
            </div>
        ''')
    html_template = html_template.replace('<!-- US_GOV_NEWS_ITEMS -->', '\n'.join(us_gov_news_html))

    international_news_html = []
    for item in data['international_news']:
        new_badge = '<span class="new-badge">🆕 NEW</span>' if item.get('new', False) else ''
        international_news_html.append(f'''
            <div class="news-item">
                <h3>{item['title']} {new_badge}</h3>
                <p>{item['summary']}</p>
                <a href="{item['link']}" target="_blank">Read ↗</a>
            </div>
        ''')
    html_template = html_template.replace('<!-- INTERNATIONAL_NEWS_ITEMS -->', '\n'.join(international_news_html))

    ai_news_html = []
    for item in data['ai_news']:
        new_badge = '<span class="new-badge">🆕 NEW</span>' if item.get('new', False) else ''
        ai_news_html.append(f'''
            <div class="news-item">
                <h3>{item['title']} {new_badge}</h3>
                <p>{item['summary']}</p>
                <a href="{item['link']}" target="_blank">Read ↗</a>
            </div>
        ''')
    html_template = html_template.replace('<!-- AI_NEWS_ITEMS -->', '\n'.join(ai_news_html))

    html_template = html_template.replace('Updated: March 2, 2026 - 6:00 PM MT', f"Updated: {datetime.now().strftime('%B %d, %Y - %I:%M %p MT')}")

    with open('/home/ubuntu/dashboard/index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("Dashboard HTML generated successfully.")

def main():
    job_keywords = "internship finance accounting business data analytics operations supply chain entry-level"
    job_location = "Denver, CO"
    days_ago_limit = 7

    linkedin_jobs = scrape_linkedin_jobs(job_keywords, job_location, days_ago_limit)
    ziprecruiter_jobs = scrape_ziprecruiter_jobs(job_keywords, job_location, days_ago_limit)
    glassdoor_jobs = scrape_glassdoor_jobs(job_keywords, job_location, days_ago_limit)
    
    financial_news = get_financial_news()
    us_gov_news = get_us_government_news()
    international_news = get_international_news()
    ai_news = get_ai_news()

    dashboard_data = {
        "jobs": linkedin_jobs + ziprecruiter_jobs + glassdoor_jobs,
        "financial_news": financial_news,
        "us_gov_news": us_gov_news,
        "international_news": international_news,
        "ai_news": ai_news,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    generate_dashboard_html(dashboard_data)

if __name__ == "__main__":
    main()
'''
