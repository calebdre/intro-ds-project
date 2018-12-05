import requests
import pandas as pd
from lxml import etree
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

search_url = lambda genre, page = 1: "https://archiveofourown.org/works/search?commit=Search&page={}&utf8=%E2%9C%93&work_search%5Bbookmarks_count%5D=&work_search%5Bcharacter_names%5D=&work_search%5Bcomments_count%5D=&work_search%5Bcomplete%5D=&work_search%5Bcreators%5D=&work_search%5Bcrossover%5D=&work_search%5Bfandom_names%5D=&work_search%5Bfreeform_names%5D={}&work_search%5Bhits%5D=&work_search%5Bkudos_count%5D=&work_search%5Blanguage_id%5D=&work_search%5Bquery%5D=&work_search%5Brating_ids%5D=&work_search%5Brelationship_names%5D=&work_search%5Brevised_at%5D=&work_search%5Bsingle_chapter%5D=0&work_search%5Bsort_column%5D=kudos_count&work_search%5Bsort_direction%5D=desc&work_search%5Btitle%5D=&work_search%5Bword_count%5D=".format(page, genre)

def get_story(href):
    url = "https://archiveofourown.org{}?view_full_work=true".format(href)
    html = requests.get(url).text
    tree = etree.HTML(html)
    paragraphs = tree.cssselect("div.userstuff p:not(align)")
    paragraphs = [t.text.strip() for t in paragraphs if t.text and t.text.strip() != '' and t.text.strip()  is not '\xa0' and t.text.strip() is not '\n']
    
    story = " ".join(paragraphs)
    try:
        author = tree.cssselect("a[rel='author']")[0].text
    except:
        author = "-"
    try:
        fandom = tree.cssselect('.fandom.tags a')[0].text
    except: 
        fandom = "-"
    
    return author, story, fandom, url

def get_links(search_html):
    tree = etree.HTML(search_html)
    return [e.get("href") for e in tree.cssselect("li.work .heading a:first-child")]

def main():
    genres = [
        'Tragedy', 'Poetry', 'Supernatural', 'Humor', 'Horror',
        'Adventure', 'Drama', 'Fantasy', 'Parody', 'Angst', 'Friendship',
        'Romance', 'Spiritual', 'Family', 'Hurt', 'Mystery', 'Suspense',
        'Crime', 'Western', 'Science Fiction'
    ]
    
    num_pages = int(15000 / 20) # we want 15000 samples and the site shows 20 per page
    pool = Pool(cpu_count())
    
    for genre in tqdm(genres, desc = "Genres", unit="genre"):
        print("**************\nScraping {}\n**************".format(genre))
        stories = []
        for page in tqdm(range(1, num_pages+1), desc = genre, leave = False, unit="page"):
            url = search_url(genre, page)
            html = requests.get(url).text
            links = get_links(html)
            
            infos = pool.map(get_story, links)
            for author, story, fandom, story_url in infos:
                info = {
                    'author': author,
                    'story': story,
                    'book': fandom,
                    'href': story_url,
                    'genre': genre
                }
                stories.append(info)            
                
        print("\nSaving {}...\n".format(genre))
        with open("data/{}.csv".format(genre.replace(" ", "")), 'a') as f:
            pd.DataFrame(stories).to_csv(f, sep='|', index=False, header=False)
        

if __name__ == "__main__":
    main()