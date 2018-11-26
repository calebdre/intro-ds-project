[instructions](https://newclasses.nyu.edu/access/content/group/a655a9a4-e9ae-47ed-a62f-959223e0c99f/Project/Project_instructions.doc)

# Task
Train a model to classify genres of stories on reddit

# Setting up
1. Make sure to have the [required libraries](requirements.txt) installed:  
`pip install -r requirements.txt`  

2. Get the word embeddings:  
`bin/gen_word_embeddings`  

3. Get the data:  
`bin/gen_data`  

    - Change the number of samples to get for each genre [here](scrape_fanfic.py#93) and the max number of samples from a single book [here](scrape_fanfic.py#94)
    - The fanfiction.net parser gets all the stories for 5 random books, but you can change that number in the script [here](scrape_fanfic.py#L101) if you need more/less
    - Change the number of results pages to scrape for each book [here](scrape_fanfic.py#L107) (there are 25 stories per page)
    - Change the number of chapters for each story to scrape [here](scrape_fanfic.py#L31)
    - Note that saving only happens upon completion of collecting _all_ the stories from the random books. So if the script terminates in the middle, no new data
    - Also note that the parser will create files of the form "data/{Genre1}\_{Genre2}\_{Genre3}.csv" and will truncate if there's an existing file
4. Check out the [data notebook](data.ipynb) for how to do some data transformations