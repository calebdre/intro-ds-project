import requests
import pandas as pd
from lxml import etree

from multiprocessing import Pool, cpu_count
import random
import os
import re
from functools import reduce
from time import sleep as _sleep

max_chapters = 10 # use 'None' for all chapters
genre_samples = 10000
max_samples_from_book = 5000
num_books = 25 # use 'None' for all books
num_pages = 10 # use 'None' for all pages
    
def sleep():
    sleep_time = random.randint(30,120)/100
    _sleep(sleep_time) 

def get_story(href):
    url = "https://www.fanfiction.net{}".format(href)
    story_xpath = '//*[@id="storytext"]'
    story_xpath_no_extra = '//*[@id="storytext"]/following-sibling::hr' # sometimes authors put direct messages to the reader at the beginning of their story. they end it with <hr/>
    chapters_xpath = '//*[@id="chap_select"]/option'

    def get_story_text(tree):
        story_text = tree.xpath(story_xpath_no_extra)
        if len(story_text) == 0:
            story_text = tree.xpath(story_xpath)[0]
            story_text = ''.join(story_text.itertext())
        return story_text

    story_name = url.split("/")[-1]
    
    sleep() # to avoid DOSing fanfic.net. Otherwise the server will randomly fail to respond in a few different ways
    html = requests.get(url).text
    tree = etree.HTML(html)

    story_text = get_story_text(tree)
    chapters = tree.xpath(chapters_xpath)
    chapters = len(reduce((lambda x, y: [y.text] + x if y.text not in x else x), chapters, [])) # sometimes lxml counts each element twice. this gets rid of duplicates
    
    if max_chapters is not None and chapters > max_chapters:
        chapters = max_chapters
    chapter_href_prefix = '/'.join(href.split("/")[:3])
    print("Fetching {} chapters for {}".format(chapters if chapters > 0 else 1, story_name))
    for i in range(2, chapters-1):
        chapter_url = "https://www.fanfiction.net{}/{}".format(chapter_href_prefix, i)
#         print("fetching chapter: {}".format(chapter_url))
        sleep() # to avoid DOSing fanfic.net. Otherwise the server will randomly fail to respond in a few different ways
        
        html = requests.get(chapter_url).text
        tree = etree.HTML(html)
        story_text += get_story_text(tree)

    return story_text

def collect_links(book, page):
    url = "https://www.fanfiction.net/book/{}/?&srt=5&r=10&lan=1&len=51&p={}".format(book, page)
    stories_xpath = '//*[@id="content_wrapper_inner"]/div[@class="z-list zhover zpointer "]'
    author_xpath = lambda idx: "{}[{}]/a[2]".format(stories_xpath, idx+1)
    link_xpath = lambda idx: "{}[{}]/a[1]".format(stories_xpath, idx+1)
    genre_xpath = lambda idx: "{}[{}]/div/div".format(stories_xpath, idx+1)

    html = requests.get(url).text
    tree = etree.HTML(html)
    stories = tree.xpath(stories_xpath)

    links = []
    for i, story in enumerate(stories):
        genre_area_text = tree.xpath(genre_xpath(i))[0].text
        genre_area_text = re.search("Rated.+Chapters", genre_area_text).group(0)
        if genre_area_text.count("-") == 2:
            continue
        else:
            genre = re.search("English -([a-zA-Z\s/]+)-", genre_area_text).group(1).strip()
            author = tree.xpath(author_xpath(i))[0].text
            href = tree.xpath(link_xpath(i))[0].get("href")
            links.append((genre, author, href))

    return links

def get_num_pages(book):
    url = "https://www.fanfiction.net/book/{}".format(book.replace(" ","-"))
    hr_xpath = '//*[@id="content_wrapper_inner"]/hr'
    nav_links_xpath = '//*[@id="content_wrapper_inner"]/center[1]/a'

    html = requests.get(url).text
    tree = etree.HTML(html)
    if len(tree.xpath(hr_xpath)) == 0:
        return 1

    links = tree.xpath(nav_links_xpath)
    if len(links) == 1:
        return 2
    if links[-2].text == "Last":
        href = links[-2].get("href")
        count = re.search('p=([0-9]+)', href).group(1)
        return int(count)
    
    return int(links[-2].text)

def get_books():
    return ["Harry Potter", "Twilight", "Percy Jackson and the Olympians", "Lord of the Rings", "Hunger Games", "Warriors", "Mortal Instruments", "Maximum Ride", "Hobbit", "Chronicles of Narnia", "Phantom of the Opera", "Gossip Girl", "Outsiders", "A song of Ice and Fire", "Vampire Academy", "Divergent Trilogy", "Song of the Lioness", "Inheritance Cycle", "Silmarillion", "Artemis Fowl", "Fairy Tales", "Animorphs", "Janet Evanovich", "Pride and Prejudice", "Les Miserables", "Gallagher Girls", "Bible", "Sherlock Holmes", "Alex Rider", "Sookie Stackhouse/Southern Vampire...", "Clique", "Vampires", "Fifty Shades Trilogy", "Peter Pan", "Maze Runner Trilogy", "39 Clues", "Redwall", "Skulduggery Pleasant series", "Infernal Devices, Cassandra Clare", "Discworld", "Sisters Grimm", "Darren Shan Saga/Cirque Du Freak", "Ranger's Apprentice", "Morganville Vampires", "Vampire Diaries", "Series Of Unfortunate Events", "Hardy Boys/Nancy Drew", "Alice in Wonderland", "Night World series", "Mediator", "House of Night", "Lord of the Flies", "Devil Wears Prada", "Darkest Powers", "Forgotten Realms", "Good Omens", "Protector of the Small Quartet", "Host", "His Dark Materials", "Wheel of Time", "Charlie and the Chocolate Factory", "Selection Trilogy, Kiera Cass", "Gone", "Dresden Files", "Holes", "Valdemar universe", "Wings of Fire, Tui T. Sutherland", "Anne of Green Gables series","Secret Circle series","Gone with the Wind","Kane Chronicles","Dragonlance","Lunar Chronicles","Princess Diaries","Inkheart","Baby Sitters Club","Worm","Fault in Our Stars","Underland Chronicles","Carmilla","Coraline","Lorien Legacies","Gemma Doyle Trilogy","Hitchhiker's Guide to the Galaxy","To Kill a Mockingbird","Kingdom Keepers","Dragonriders of Pern series","Phantom Stallion","Charlie Bone","A Court of Thorns and Roses","100% Wolf","Throne of Glass series","Keeper of the Lost Cities","Dr. Seuss series","Daughters of the Moon","Bloodlines Series, Richelle Mead","Bartimaeus Trilogy","Hush, Hush","Giver","Young Wizards","1-800-Where-R-You","Ella Enchanted","13 to Life","Old Kingdom/Abhorsen series","Charles Dickens","Immortals, Tamora Pierce","New Jedi Order","Deltora Quest","Goosebumps","Leviathan series","In The Forests of the Night","1984","Black Jewels Trilogy","Dark Tower series","Jedi Apprentice","Carry On","Cherub","Bridge to Terabithia","Dark-Hunter series","Chronicles of Vladimir Tod","Vampire Kisses","Hollows, Kim Harrison","Book Thief","310 series","Black Magician Trilogy","Diana Wynne Jones","Jane Eyre","Fangirl","Pendragon","Fablehaven","Little Women","Sweep","Emma","Dollanganger Saga","Great Gatsby","Miss Peregrine's Home for Peculiar...","Sammy Keyes","Iron Fey Series","Robin Hood","Sleepy Hollow","1632 series","Robert Langdon series","Raven Cycle","Alexandre Dumas","Uglies","Fallen, Lauren Kate","Monster High","David Eddings","Hunchback of Notre Dame","Confessions of Georgia Nicolson","Scarlet Pimpernel","Guardians of Ga'Hoole","Blood And Chocolate","Bridget Jones' Diary","Thief Lord","H.I.V.E.","Sisterhood of the Traveling Pants","Romeo and Juliet","Cthulhu Mythos","Finding Sky","Trixie Belden","Circle of Magic","Tuck Everlasting","Dark is Rising Sequence","Watership Down","Edgar Allan Poe","Frankenstein","Blue Bloods","Everworld","Cal Leandros","Wicked","Carpathian Series","Beka Cooper series","Secret Garden","Mercy Thompson series","Wicked Lovely","Perks of Being a Wallflower","Orson Scott Card","Spirit Animals","American Girl","Guardians of Time","Thirteen Reasons Why","Of Mice and Men","Septimus Heap","Pretty Little Liars series","Sense and Sensibility","Catcher in the Rye","Secrets of the Immortal Nicholas F...","A Coming Evil","North and South","13 1/2","Magnus Chase and the Gods of Asgar...","Heartland","Modern Faerie Tales","Forbidden Game series","Private","Diary of a Wimpy Kid","Keys to the Kingdom","Seven Kingdoms Trilogy","Green Rider","A Separate Peace","Dracula","Sherwood Smith","Pellinor","Dune","Caster Chronicles","Sweet Valley series","School for Good and Evil","Kiesha'ra","Homer","Women of the Otherworld","Left Behind","Shiver, Maggie Stiefvater","Virals","Avalon Web of Magic","Penderwicks series","Odyssey","Red Queen, Victoria Aveyard","Legend, Marie Lu","Coldfire Trilogy","Persuasion","World War Z","Miles Vorkosigan","Dark Artifices","Lockwood & Co.","Queen's Thief series","Little Red Riding Hood","Young Jedi Knights","A-List","Looking For Alaska, John Green","Drake Chronicles","Winnie-the-Pooh","Little House series","Grisha Trilogy","Heist Society","Martian, Andy Weir","Demonata","Power of Five series","It","Silverwing","Ender's Game series","Enchanted Forest","Zombie Survival Guide","Wuthering Heights","Tiger's Curse Series","Dr. Jekyll and Mr. Hyde","Enid Blyton","Noughts and Crosses","Long Walk","Fearless","Warm Bodies, Isaac Marion","32c That's Me","13th Reality series","Mysterious Benedict Society series","Vampirates series","Kingkiller Chronicle","Unwind","Carrie","Temeraire","Shatter Me, Tahereh Mafi","Swallows and Amazons series","Beowulf","Chaos Walking series","Crucible","Midnighters","Six of Crows","Animals","Dork Diaries","Trickster series","Strange Angels, Lili St. Crow","Dinotopia","An Unfortunate Fairy Tale","Jeeves","Mother Daughter Book Club","Speak","Study series","My Sister's Keeper, Jodi Picoult","Animal Farm","Laurie R. King","Marion Zimmer Bradley","Picture of Dorian Gray","Price of Salt","Me Before You","Terry Brooks","Little White Horse","Chronicles of Ancient Darkness","Lloyd Alexander","Delirium, Lauren Oliver","Earth's Children","Penryn & the End of Days","Boy Meets Girl","All American Girl","Memorias de Idhún","Fahrenheit 451","Saddle Club","Immortals series, Alyson Noel","City of Ember","Tom Clancy","Alpha Force","Neverwhere","Fallen","After","Stravaganza","Matched","I Am Legend","Memoirs of a Geisha","Book of Amber","Obernewtyn","Romance of the 3 Kingdoms","Someone Like You","Drama! series","Simon vs. the Homo Sapiens Agenda","Perfect Chemistry","Дом, в котором","Companions Quartet","Avalon High","Millennium Trilogy","Will of the Empress","Time Machine","Last Apprentice series/Wardstone C...","Thoroughbred","Hercule Poirot series","Black Stallion","Truth About Forever","Edge Chronicles","Iliad","Zombie Fallout","Cassandra Palmer Series","Rapunzel, Rapunzel, Let Down Your ...","Lovely Bones","Dear John, Nicholas Sparks","Just Listen","Boy In the Striped Pajamas","Demon Headmaster","Night Huntress series","Summer I Turned Pretty","Wings, Aprilynne Pike","The Tomorrow series","Lurlene McDaniel","Clare B. Dunkle","Mansfield Park","Evernight","Fever Series","Witch & Wizard","If I Stay","Foundation","Abraham Lincoln: Vampire Hunter","Casson Family Series","A Christmas Carol","Heir series","Magisterium series","Stargirl","Guardians of Childhood series","Wolves of the Beyond","War and Peace","Paper Towns","Kite Runner","Ingo","Darkest Minds","Flipped","Le Pacte des Marchombres","Hoot","Stormlight Archive","Last Unicorn","Dark Visions series","Mistborn Trilogy","Eleanor and Park","To All the Boys I've Loved Before","A New Beginning to An Old Ending","Clive Barker'","Beastly","Treasure Island","Looking Glass Wars Trilogy","Poppy Z Brite","Alpha and Omega series","Count of Monte Cristo","American Gods","About a Boy","Witcher/Wiedźmin, Andrzej Sapkowsk...","A Dirty Job","NERDS, Michael Buckley","Broken Sky","Great Expectations","Matthew Reilly","Ghost Bird Series","Enemy, Charlie Higson","Kushiel's Legacy series","Shapeshifter, Ali Sparkes","Medoran Chronicles","A Child Called It","Pirates of the Caribbean: Jack Spa...","Lords Of The Underworld series","Dragon's Bait","Time Traveler's Wife","And Then There Were None","Love Ya, Babe","Honor Harrington","Scorpio Races","This Lullaby","Shades of London","El Ciclo de la Luna Roja","13 Little Blue Envelopes","Handmaid's Tale","Oz Series","Daughter of Smoke and Bone","A Kingdom of Dreams","Jonathan Strange & Mr. Norrell","Ever Afters series","Earthsea Trilogy","Last Song","A Little Princess","Nightshade series, Andrea Cremer","War of the Worlds","Tender_is_the_Night","Xanth","Dragon Rider","Wintergirls","Death Gate Cycle","Abarat series","A Grief Observed","Circle Opens","Biggles series","Spiderwick Chronicles","Seekers series","Cat Royal Adventure","Magic Tree House series","Michael Crichton","Pendergast series","Boy Meets Boy, Lawrence Schimel","James and the Giant Peach","Everlost","Myth Adventures","Ready Player One","Night Angel Trilogy","Incarceron series","T*Witches","New Species series","Adventures of Huckleberry Finn","Canterwood Crest series","Lux Series, Jennifer L. Armentrout","Pride and Prejudice and Zombies","Gordan Korman","Diana Gabaldon","Katherine Kurtz","Tara Duncan series","Faerie Path","Children of the Lamp","Graveyard Book","Captain Underpants","Little Prince","Sharpe Series","Companions of the Night","Chronicles of Nick","Unicorns of Balinor","Ruby Red/Rubinrot Trilogy","Matilda","Remnants","Eon: Dragoneye Reborn","Animals of Farthing Wood","Northanger Abbey","Witch of Blackbird Pond","Seven Realms series","Bloody Jack Adventures","Secret Series","Boy/Girl Battle Series","Shadow Falls series","Love at Stake series","Wolf Moon","On Writing","5th Wave series","Wolves of Mercy Falls Trilogy","Cormoran Strike Series","Megan Meade's Guide to the McGowan...","Firebringer Trilogy","Along for the Ride","13 1/2 Lives of Captain Bluebear","Rhapsody Trilogy","A Wrinkle in Time Trilogy","Supernaturalist","Chalet School","As I Lay Dying","Michael Vey series","Scarlett Letter","Silver Kiss","Icemark Chronicles","Before I Fall","Immortals After Dark series","Bad Boy","Brotherband Chronicles","Halo, Alexandra Adornetto","Seventh Tower","Margaret Peterson Haddix","Madeline series","Need, Carrie Jones","A Need So Beautiful","Across the Universe, Beth Revis","Demon's Lexicon","Wind On Fire","Wonder","Alphas Series, Lisi Harrison","Dreamland","Six of Hearts series","Stand","Jessica's Guide to Dating on the D...","Sight","Neverending Story","Nevermore, Kelly Creagh","Teen Idol","Ravenloft","Goose Girl","Spooksville","Ghostgirl series","Jurassic Park","Stardust","Brave New World","Peter Wimsey","Tudor series","Diadem","Judy Blume","Tiger Eyes","PS, I Love You","Oliver Twist","Omen Series, Lexie Xu","Tunnels, Brian Williams and Roderi...","Knight and Rogue series","Hex Hall","Amelia Peabody Series","Anna and the French Kiss","You Don't Know Me","Codex Alera","Geronimo Stilton","A to Z Mysteries","Weetzie Bat","Mara Dyer Trilogy","Airhead","Os Sete","That Was Then, This is Now","Psy-Changelings Series","It Girl","Chemical Garden Trilogy","Wereworld","Last Dragon Chronicles","Private Peaceful","Havemercy/Shadow Magic","Princess and the Goblin","Shining","Replica","Evermore, Alyson Noel","Good Night Mr Tom","Captive Prince Trilogy","Nightmare Room","Kate Daniels series","Trylle Trilogy","Luxe series","Woman in White","Rowan of Rin series","Anna Dressed in Blood","Canterbury Tales","Flowers for Algernon","Star Trek: New Frontier","Goddess Test series","Ann Rinaldi","Juliet Marillier","Short Second Life of Bree Tanner","Johnny Tremain","Mandie series","A Cage of Butterflies","Castaways of the Flying Dutchman s...","Shadow Children series","Falling Kingdoms series","Mortal Engines Quartet","Fried Green Tomatoes at the Whistl...","War and Rememberance","Misery","Kissed by an Angel series","Claidi Journals","Dark Life","William Gibson","13 Treasures Trilogy","Stolen, Lucy Christopher","Westmark","A Tangled Web","Dangerous Days of Daniel X","Unearthly, Cynthia Hand","Tales of the Frog Princess","Wonderful Wizard of Oz","Love Comes Softly series","Borrowers series","Aristotle and Dante Discover the S...","Lost Souls","Guild Hunter series","Ramona Series","Impulse, Ellen Hopkins","Conan series","Night Circus","Gormenghast","Skybreaker","Horrid Henry series","Arthur C. Clarke","Knights of Emerald/Les Chevaliers ...","A Resurrection of Magic","Soul Screamers series","Cadfael","Dalemark Quartet","Marley & Me","Unicorn Chronicles","Secrets series","Wake series","Anna Karenina","Junie B. Jones Collection","A Certain Slant of Light","TimeRiders series, Alex Scarrow","Emily of New Moon series","Last Survivors, Susan Beth Pfeffer","Boxcar Children","Elsewhere","K-PAX","Heart is a Lonely","Angel Burn","Help, Kathryn Stockett","Beautiful and Damned","Call Me by Your Name","Young Samurai series","Moby Dick","Beautiful Disaster, Jamie McGuire","Ancient Future","Shopaholic series","Fear Street series","Forest Of Hands And Teeth","Lady or the Tiger","4:Play","Road","Starcrossed, Josephine Angelini","A Knight's Honor","Original Sinners series","Dragons in Our Midst","Mel Beeby Agent Angel","Story Girl","Lock and Key","Raven Hill Mysteries","Louis Lamour","Wolf Chronicles","Never Let Me Go, Kazuo Ishiguro","Water for Elephants","Twenty Thousand Leagues Under the ...","Blood of Eden, Julie Kagawa","Chronicles of Elantra","League, Sherrilyn Kenyon","Beyonders, Brandon Mull","George Smiley series","Forbidden, Tabitha Suzuma","Survivors, Erin Hunter","Doctrine of Labyrinths series","Roman Mysteries","One Day","Gentleman Bastard Sequence","Squire's Tales, Gerald Morris","Hidden World","Coalition","Georgette Heyer novels","Tom Stoppard","How I live now","Worldwar series","Black Beauty","Rainbow Magic","Splintered Series","Paranormalcy","Parasol Protectorate Series","Airborn","Murder A-Go-Go Mystery","Fantastic Mr. Fox","Raised by Wolves, Jennifer Barnes","Dreamcatcher","Crossfire series, Sylvia Day","All for the Game Trilogy","1Q84","Vampire Plagues","Flirt series","Beyond Illusion series/Myona Moltm...","Historian","Unwanteds series","Geography Club","A Rose to the Fallen","Generation Dead","Christine","Reckoners","Listen!","Poison","Violet Eden Chapters","Half Bad Trilogy","Blood Books","Crank series","Evil Genius","Monster Blood Tattoo series","Monstrumologist series","Alex Cross series","One Chance","O'Malley series","Summer of My German Soldier","Novels of the Others","Dark Guardian series","Before I Die","Flatland","Remember Me?","Bonus Poetry/Bónus ljóð","Darkangel Trilogy","Covenant Series, Jennifer L. Armen...","Prime of Miss Jean Brodie","Outlanders","Beautiful Dead","Ascendance Trilogy","Robert Asperin","Newsflesh Trilogy","Books of the Kingdoms","Graceling Realm Trilogy","Saga of Larten Crepsley","Pet Sematary","Blue Castle","Spy High","Goddess Girls series","Single Romance Novels","Aldous Huxley","Adventures of Tom Sawyer","Princess Academy","Sleeping Beauty","Curious Incident of the Dog at Nig...","Affinity","Embassy Row, Ally Carter","School of Fear","Folly series, Ben Aaronovitch","Young Elites series","Journey to the West/西遊記","Curious George","Children's Continuous Series","Avatars","Pegasus, Kate O'Hearn","Weather Warden series","Love Story, Jennifer Echols","Tapestry, Henry H. Neff","One Flew Over The Cuckoo's Nest","Love in the Library","Crime and Punishment, Fyodor Dosto...","GhostWalkers","Crystal Cave","Dragaera","La Quête d'Ewilan","Snow Like Ashes Series","Laws of Magic","Zoombie Blondes","Handle With Care","Eyes Like Stars","Brideshead Revisited","Incarnations of Immortality","Paradise Lost","Book of Mormon","Gifted, Marilyn Kaye","Aeneid","Mistmantle Chronicles","Brave Story/ブレイブ·ストーリー","Arthur series, Luc Besson","Girl, Missing","Ally's World","Number the Stars","All Souls Trilogy","Snow-walker","Atonement","Traveler","Mara, Daughter of the Nile","Lolita, Vladimir Nabokov","Chosen, Chaim Potok","Spy School series","Drama High series","Outlander Series","Witch Child","Gone Girl","Land of Stories","Don Quixote","Chocolate Box Girls","Robert Heinlein","Shutter Island","Phantom Stallion: Wild Horse Islan...","Pact","Return, Christy Newman","Leven Thumps","Adventurers Wanted","Kingmaker, Kingbreaker","Girl with a Pearl Earring","Half Moon Investigations","Go Ask Alice","Firelight, Sophie Jordan","Secret Life of Bees","Friday","Emily Windsnap series","Scary Stories for Stormy Nights","Molly Moon series","Tangerine","Things They Carried","Willow, Julia Hoban","Scarlett","Disney Fairies","Fire Within","Elemental series, Brigid Kemmerer","Missing series, Margrets Peterson ...","Peter Rabbit series","Magicians, Lev Grossman","A Room With a View","Boy Who Couldn't Die","Chalion series","Midnight Texas Series","Seven Wonders series","Ruby Redfort","Starshield","Once Upon a Time series","Miracles","Tales of Rowan Hood","Melanie Rawn","Atlas Shrugged","Dexter series","Let the Right One In","Jedi Quest series","Books of Beginning","Custodes Noctis series","Animal Ark Series","Den of Shadows","Miss Marple Stories","Salem's Lot","Wind in the Willows","Seraphina","Chocolate War","Firekeeper Saga","Abandon, Meg Cabot","Alex Delaware series","Otherworld Series","Oracle trilogy","Other Side of the Story","Vampire Stalker","Dragon Keepers Chronicles","Girl, Interrupted","Keeping You a Secret","Freedom series","Monster Hunter series, Larry Corre...","Space Trilogy"]

def get_story_from_link_data(link_data):
    book, genre, author, href = link_data
    story = get_story(href)

    return {
        "story": story,
        "genre": genre,
        "book": book,
        "href": href,
        "author": author
    }

def main():
    genre_data = {}

    books = get_books()
    random.shuffle(books)
    pool = Pool(cpu_count())
    
    if num_books is not None:
        books = books[:num_books]
    
    for book in books:
        print("\n***********\nSourcing sample fanfics from '{}'\n***********\n".format(book))
        book = book.replace(" ", "-").replace("...", "")
        genre_counts = {}
        pages = get_num_pages(book) + 1 # +1 to account for 0 based indexing for range()
        
        if num_pages is not None:
            pages = min(num_pages, pages)

        for page in range(1, pages):
            print("\nCollecting links for page {}\n".format(page))
            page_links = collect_links(book, page)
            links_to_scrape = []
            for link_data in page_links:
                genre, author, href = link_data
                if genre not in genre_data.keys():
                    print("Found a new genre: {}".format(genre))
                    genre_data[genre] = []
                elif len(genre_data[genre]) >= genre_samples:
                    continue

                if genre not in genre_counts.keys():
                    genre_counts[genre] = 1
                elif genre_counts[genre] >= max_samples_from_book:
                    continue
                
                links_to_scrape.append([book, *link_data])

            print()
            data = pool.map(get_story_from_link_data, links_to_scrape)
            for datum in data:
                genre_data[datum["genre"]].append(datum)            
                
            print("\nCounts for each genre: {}".format(", ".join(["{}: {}".format(key, len(genre_data[key])) for key in genre_data.keys()])))
            genre_data_lengths_check = [len(genre_data[key]) > genre_samples for key in genre_data.keys()]
            if False not in genre_data_lengths_check:
                break

    pool.close()
    pool.join()
    
    print()
    outdir = 'data'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    for genre in genre_data:
        filename = "{}/{}.csv".format(outdir, genre.strip().replace("/", "_"))
        print("saving {}".format(filename))
        
        pd.DataFrame(genre_data[genre]).to_csv(filename, sep='|', mode="w+", index=False)
        
    print("\nDone!")

if __name__ == "__main__":
    main()
