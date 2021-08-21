# Wikipedia Journal
This is a commandline tool for generating journal articles from wikipedia citations. 

The program works with Internet Archive's websites and tools, including https://scholar.archive.org/, https://fatcat.wiki/ as well as specific collections of periodicals such as https://archive.org/details/sim_microfilm. 

The Turn All References Blue Project aims to improve wikipedia's information network connectivity and this project attempts to contribute to that goal by adding links to article citations on wikipedia. Usually, papers and articles are fairly well-linked already because they are born digital and thus have a digital object identifier (DOI) that is unique. However, many Wikipedia citaitons do not have a field for this information so here is where this work comes in. The elastic search endpoints provide search results for the relevant citation information and we can use these results to generate a link. 

This project is very specific has certain limitations. Feel free to contact me if you have any suggestions or concerns!

# Installation
## Manual
Downloading Repository
```bash
  $ git clone https://github.com/graceCXY/wiki-journal-link.git
```
Setting up the environment
```bash
  $ python3 -m venv link-env
  $ source link-env/bin/activate
```
Getting all the dependencies from requirements.txt
```bash
  $ pip install -r requirements.txt
```

# Usage
## Scholar
`scholar <Citation>`
```bash
$ python wiki_journal_link/__main__.py scholar "{{Akademik dergi kaynağı|url=|başlık=The mind and brain of short-term memory|yazarlar=Jonides|sayı=|sayfalar=193-224|çalışma=Annual Review of Psychology|yıl=2008|cilt=59}}"
"https://scholar.archive.org/work/smviomizcncc5cslifvbtuymfa"
```
## Serials in Microfilms
`sim <Citation>`
```bash
$ python wiki_journal_link/__main__.py sim "{{Akademik dergi kaynağı|başlık=The Mind and Brain of Short-Term Memory|yazarlar=Jonides|tarih=Ocak 2008|sayı=1|sayfalar=193-224|çalışma=Annual Review of Psychology|cilt=59}}"
"https://archive.org/details/sim_annual-review-of-psychology_2008_59"
```

## Attempts both processes 
`either <Citation>`
```bash
$ python wiki_journal_link/__main__.py either "{{Akademik dergi kaynağı|başlık=Navigation-related structural change in the hippocampi of taxi drivers|tarih=Nisan 2000|sayı=8|sayfalar=4398-403|çalışma=Proceedings of the National Academy of Sciences of the United States of America|cilt=97}}"
"https://scholar.archive.org/work/suhffvny7rd3tfqcxtnvltzilm"
```


# Limitations 
## Login information 
The user would need to create a Internet Archive account at https://archive.org/ if they wish to run the SIM process or both processes. Since there are certain access restrictions for different accounts, the output produced would be different.

## Languages and Templates 
The Wikipedia template in the current preprocessing stage is very specific to certain fields of certain languages. More informataion can be added to the trans_aliases.py file for program robustness

## Network dependencies
Because the program uses different endpoints to access elastic search and make network requests, there may be networking errors or delays that occur. The program is also not the fastest also due to the same reason.  


# How it works
As a visual learner, I made a diagram to demonstrate the workflow of the program. 

![ScreenShot](https://github.com/graceCXY/wiki-journal-link/blob/master/wiki_journal_link/workflow_diagram.png)


Input: the pipeline takes in a citation from Wikipedia. 
Output: URL of the article or null value.

### Preprocessing 
Citation Parsing: parse input to extract desired fields. 

Basic Filtering: make sure that the journal citation has journal name, article title, year/date field, a volume number, and a page number.Perform basic filtering to remove citatons with existing url fields or external ids (ex DOI) fields. 

Autourl Check: verifies that there would be no autourl created based on the template on wikipedia since we don't want to overwrite existing urls when we don't know if it is better or worse than the url that we put up. This is its own separate module. 

Data Normalization: There are some edge cases with journal names that are stored in the database in a particular way such that the elastic searches should follow a specific patter. In addition, yhere are many journal names that appears to be abbreviated on Wikipedia, the naive approach had been to use a table of common mappings from full journal names to abbreviated names. Another approach is to attempt to exand abbreviated names so that it is standard. This part actually inspired this work: https://github.com/graceCXY/iso4-abbrev-expander


### SIM process
This process searches for articles in the Serials in Microfilms Collection, which has millions of records of articles archived in microfilms. Internet Archive has a team digitizing these records and it has been an ongoing effort. 

Generate SIM ID: All the issues of journals are stored by a id. The word "sim", journal name, and data of release are usually all encompassed in the metric. In a previous attempt, I generated many different ids and performed searches on all possible result. I later realized that it takes too much of a networking toll and shifted my focus to making a search with the minimal amount of information and placed more emphasis on evaluating searches. 

Advanced Search: use the elastic search api of archive.org to obtain search results. Keep in mind that there are limitations to what different accounts can access so results will be different. 

Find exact match: look for exact match by verifying 4 out of 5 fields of the sim id.

Generate url: return the url generated by the best result.

If there is a url, we can pass this url and the page number into the page verification system of lamp since page 1 of the scan may not always be the first page of the periodical. If the there is no url, we can use the fatcat process since the microfilm collection is still being digitized.

### Fatcat/Scholar process 
Since fatcat and scholar shares the bulk of database, we can use the fatcat's elastic search endpoint.

Determine parameters: Similar to the SIM ID generation process, I learned through experimentation to input few yet specific query parameters to yield the most appropriate search results.

Fatcat Elastic Search: I previously approached this with the url but later learned to use the elastic search api, which supports more complex query strings. 

Find Match Metric: This is a fairly complex system of verification to compare the search result with the citation information. There are variations between exact matches and fuzzy matches. For instance, if the title of the article is the exact same, we can expect less from other fields compared to the degree of similarity we expect with other fields when the title has a very low fuzzy match score. 


# Challenges and Future Research


### Elastic Search Explorations 
There are always more Elastic Search exploration that can be done with the matching threshold as well as query string experimentations. 

### Different Languages and different templates
Currently, the aliases for wikipedia templates recognizes English and Turkish. More information can be added to the trans_aliases.py file for program robustness 
