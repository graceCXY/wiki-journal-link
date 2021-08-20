# ISO4 Abbrevations Expander
This is a commandline tool for generating journal articles from wikipedia citations. 

The program works with Internet Archive's websites and tools, including https://scholar.archive.org/, https://fatcat.wiki/ as well as specific collections of periodicals such as https://archive.org/details/sim_microfilm. 

The Turn All References Blue Project aims to improve wikipedia's information network connectivity and this project attempts to contribute to that goal.

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
## SIM
`SIM <Citation>`
```bash
$ python wiki_journal_link/__main__.py SIM "{{Akademik dergi kaynağı|başlık=The Mind and Brain of Short-Term Memory|yazarlar=Jonides|tarih=Ocak 2008|sayı=1|sayfalar=193-224|çalışma=Annual Review of Psychology|cilt=59}}"
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
![alt text](https://github.com/graceCXY/wiki-journal-link/blob/master/wiki_journal_link/workflow_diagram.png)



# Challenges and Future Research

## Elastic Search Explorations 

## Different Languages and different templates 

## Program structure
