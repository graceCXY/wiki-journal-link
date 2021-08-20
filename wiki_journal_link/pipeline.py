import dateparser
import datetime
import re
import requests.adapters
import json

import pandas as pd 
import numpy as np

from autourl_check import autourl_exists
from trans_aliases import get_aliases

from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz 
from elasticsearch import Elasticsearch
from textblob import TextBlob


###########################################################################################
###########################  CITATION PREPROCESSING  ######################################
###########################################################################################



# Parsing a wikipedia citation data
def parse_citation_data(citation):

    alias_lst = get_aliases(citation)
    journal_aliases = alias_lst[0]
    date_aliases = alias_lst[1]
    year_aliases = alias_lst[2]
    volume_aliases = alias_lst[3]
    issue_aliases = alias_lst[4]
    page_aliases = alias_lst[5]
    pages_aliases = alias_lst[6]
    url_aliases = alias_lst[7]
    title_aliases = alias_lst[8]
    ext_id_aliases = alias_lst[9]
    author_aliases = alias_lst[10]
    first_name_aliases = alias_lst[11]
    last_name_aliases = alias_lst[12]
    
    citation = re.sub('[{}]', '', citation)
    citation_list = citation.split("|")
    
    journal = ""
    volume = ""
    issue = ""
    
    title = ""
    page = ""
    
    url = ""
    external_ids = {}
    
    date = ""
    month_str = ""
    year = 0
    
    authors = []
    first_names = []
    last_names = []
    
    for field in citation_list:
        field = field.strip()
        
        # find journal title
        for j_a in journal_aliases:
            journal_regex = j_a + "(\s{0,})="
            if re.match(re.compile(journal_regex), field):
                journal = field.split("=")[1].strip()
                break
   
        # find journal volume 
        for v_a in volume_aliases:
            volume_regex = v_a + "(\s{0,})="
            if re.match(re.compile(volume_regex), field):
                volume = field.split("=")[1].strip()
                volume = re.sub('[^0-9]+', '', volume)
                break
            
        # find journal issue
        for i_a in issue_aliases:
            issue_regex = i_a + "(\s{0,})="
            if re.match(issue_regex, field):
                issue = field.split("=")[1].strip()
                break
        
        # find journal year
        for y_a in year_aliases:
            year_regex = y_a + "(\s{0,})="
            if re.match(year_regex, field):
                year = field.split("=")[1].strip()
                date = re.sub('[^0-9]+', '', year)
                try:
                    year = int(date)
                except:
                    year = 0
                break
            
        # find journal date
        for d_a in date_aliases:
            date_regex = d_a + "(\s{0,})="
            if re.match(date_regex, field):
                date = field.split("=")[1].strip()

                try:
                    year = int(date)
                    date = str(year)
                except:
                    # use the python library for parsing
                    parsed_date = dateparser.parse(date)
                    if parsed_date != None:
                        if parsed_date.year < 2021 and parsed_date.year > 1800:
                            year = parsed_date.year
                            date = str(year)

                        if parsed_date.month < 10:
                            month = parsed_date.month
                            month_str = "0" + str(month)
                        else:
                            month = parsed_date.month
                            month_str = str(month)

                        if month_str != "":
                            date = date + "-" + month_str 
                break
        
         # find existing url
        for u_a in url_aliases:
            url_regex = u_a + "(\s{0,})="
            if re.match(url_regex, field):
                url = field.split("=")[1].strip()
                break
            
        # find page field 
        for p_a in page_aliases:
            page_regex = p_a + "(\s{0,})="
            if re.match(page_regex, field):
                page = field.split("=")[1].strip()
                if "[" in page:
                    page = ""
                break
                
        # find pages field
        for ps_a in pages_aliases:
            pages_regex = ps_a + "(\s{0,})="
            if re.match(pages_regex, field):
                pages = field.split("=")[1].strip()
                if "[" not in pages:
                    if "-" in pages:
                        page = pages.split("-")[0].strip()
                    elif "–" in pages:
                        page = pages.split("–")[0].strip()
                    else:
                        page = ""
                        
                break
                
        # find page field 
        for t_a in title_aliases:
            title_regex = t_a + "(\s{0,})="
            if re.match(title_regex, field):
                title = field.split("=")[1].strip()
                if "[" in title:
                    title = ""
                break
                
        # find external identifier field 
        for ext_id_a in ext_id_aliases:
            ext_id_regex = ext_id_a + "(\s{0,})="
            if re.match(ext_id_regex, field):
                ext_id = field.split("=")[1].strip()
                external_ids[ext_id_a] = ext_id
                break
                
        # find author field 
        for au_a in author_aliases:
            author_regex = au_a + "(\s{0,})="
            if re.match(author_regex, field):
                authors.append(field.split("=")[1].strip())
                break
        
        # find author first name 
        for f_n in first_name_aliases:
            first_name_regex = re.sub("#", r"[0-9]", f_n)
            if re.match(first_name_regex, field):
                first_names.append(field.split("=")[1].strip())
                break
                
        # find author last name 
        for l_n in last_name_aliases:
            last_name_regex = re.sub("#", r"[0-9]", l_n)
            if re.match(last_name_regex, field):
                last_names.append(field.split("=")[1].strip())
                break
            
    if len(last_names) == len(first_names):
        for i in range(len(last_names)):
            authors.append(first_names[i] + " " + last_names[i])
    else:
        authors.extend(last_names)
            
    return {"journal": journal, "date": date, "year": year, 
            "volume": volume, "issue": issue, 
            "title": title, "author": authors,
            "page": page, 
            "url": url, "external_ids": external_ids}
        
        

def citation_contains_relevant_info(cite_info, verbose = False):
    
    # make sure there's no existing url 
    if cite_info['url'] != '':
        if verbose: print("There is already an existing url.")
        return False
    
    # no existing external identifiers for auto urls 
    if cite_info['external_ids']:
        if verbose: print("There is already an existing doi link.")
        return False

    # check citation has all desired info
    if cite_info['journal'] == '':
        if verbose: print("Citation has no journal name. ")
        return False
    if cite_info['volume'] == '':
        if verbose: print("Citation has no volume.")
        return False
    if cite_info['year'] == 0:
        if verbose: print("Citation has no valid year.")
        return False
    if cite_info['page'] == '':
        if verbose: print("Citation has no page.")
        return False
    if cite_info['title'] == '':
        if verbose: print("Citation has no article title.")
        return False
    
    return True

data_path = "wiki_journal_link/data/"

data = []
with open(data_path + "journal_abbrev.csv") as file:
    lines = file.readlines()
    for curr_line in lines:
        curr_info = {}
        curr_line = curr_line.strip()
        curr_line_lst = curr_line.split(";")
        if len(curr_line_lst) == 2:
            curr_info["full"] = curr_line_lst[0]
            curr_info["abbrev"] = curr_line_lst[1]
        elif len(curr_line_lst) == 1:
            curr_info["full"] = curr_line_lst[0]
            curr_info["abbrev"] = ""
        else:
            curr_info["full"] = ""
            curr_info["full"] = ""
        data.append(curr_info)

abbrev_df = pd.DataFrame(data)
abbrev_df = abbrev_df.drop_duplicates() 



def normalize_journal_name(journal):
    
    df = abbrev_df[abbrev_df["abbrev"] == journal]
    
    if not df.empty:
        row = df.iloc[0]
        return row["full"]
    
    return journal


def preprocessing_citation(citation, verbose = False):
    
    cite_info = parse_citation_data(citation)
    
    if not citation_contains_relevant_info(cite_info, verbose):
        if verbose: print("This citaiton does not have all relevant info, or contains external identifiers.")
        return "" 
    
    if autourl_exists(citation):
        if verbose: print("There already exists an autourl.")
        return ""
    
    cite_info["journal"] = normalize_journal_name(cite_info["journal"])
    
    return cite_info


###########################################################################################
#################################  SIM COLLECTION  ########################################
###########################################################################################


### make sure year is within range and not one of those na
def within_year_range(row, year):
    first = row['First Volume']
    last = row['Last Volume']
    gaps = row['NA Gaps']
    if first != np.nan and last != np.nan:
        if year > first and year < last:
            if gaps != np.nan and gaps != "":
                gaps = str(gaps)
                gaps_list = gaps.split(";")
                for gap in gaps_list:
                    if gap.strip() == str(year):
                        return False
                return True
            return True
    return False

### generate sim ids
def generate_sim_ids(journal):
    # special characters
    if "/" in journal: # turn / into -
        journal = re.sub("/", " ", journal)
    if "-" in journal: # drop - first so that we can join with - later
        journal = re.sub("-", " ", journal)
    if "[" in journal: # ignore what's in between '[' and ']'
        index_front = journal.find("[")
        index_back = journal.find("]")
        if index_back > index_front:
            journal = journal[:index_front] + journal[index_back:]
        else:
            journal = journal[:index_front]
    if "=" in journal: # ignore what comes after =
        journal_lst = journal.split("=")
        journal = journal_lst[0]
    
    journal = re.sub('[^A-Za-z0-9 ]+', '', journal)
    sim_ids = []
    if journal != "":
        sim_id = journal.lower()
        sim_id_lst = sim_id.split()
        
        if sim_id_lst[0] == "the":
            sim_id_without_the = "-".join(sim_id_lst[1:])
            sim_id_without_the = "sim_" + sim_id_without_the
            sim_ids.append(sim_id_without_the)
            
        sim_id = "-".join(sim_id_lst)
        sim_id = "sim_" + sim_id
        
        sim_ids.append(sim_id)
    return sim_ids

def initialize_archive_session():
    with open('login_info.txt') as f:
        login_data_raw = f.read()
    
    login_data = json.loads(login_data_raw)
    
    session = requests.Session()
    
    # get login values through scraping
    login_url = "https://archive.org/account/login"
    res = session.get(login_url, timeout = 10,)
    soup = BeautifulSoup(res.content, "html.parser")
    login_data['login'] = soup.find('input', attrs = {'name':'login'})['value']
    
    # post cookie values to login 
    res = session.post(login_url, data = login_data, timeout = 10)
    
    return session, login_data

def perform_advanced_search(session, login_data, identifier):
    url_head = "https://archive.org/advancedsearch.php?q="
    url_tail = "&fl%5B%5D=identifier&sort%5B%5D=&sort%5B%5D=&sort%5B%5D=&rows=5000&page=1&output=json&callback=callback&save=yes"
    
    url = url_head + identifier + url_tail
    
    try:
        request = session.get(url, data = login_data, timeout = 10)
        request.raise_for_status()
        
        response = request.text[9:-1]
        response_json = json.loads(response)['response']

        nums = response_json['numFound']

        # if nothing is found, return empty string
        if nums == 0: 
            return ""

        # if more than one thing is found, return 
        result = dict()
        response_list = response_json['docs']
        for item in response_list:
            temp_id = item['identifier']
            temp_score = item['_score']
            result[temp_id] = temp_score

        return result
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
    
    return ""


def find_close_match_from_cite_info(cite_info, search_result, verbose = False):
    id_list = list(search_result.keys())
#     identifier_list = identifier.split("_")
    
    close_matches = dict()
    for possible_id in id_list:
        possible_id_list = possible_id.split("_")
        
        
        if verbose: print(possible_id_list)
        
        if len(possible_id_list) < 4:
            continue
        
        if cite_info["issue"] != "" and len(possible_id_list) >= 5:
            
            if verbose: print("longer than 5")
            
            # Check that it is sim
            if possible_id_list[0] == "sim":
                
                # Check that journal name matches
                if possible_id_list[1] == cite_info['sim_id'][4:]:
                    
                    # Check that year/date is within other case
                    if str(cite_info["year"]) in possible_id_list[2]:
                        
                        # Check that journal volume matches
                        if possible_id_list[3] == cite_info["volume"]:
                            
                            # Check that journal issue matches
                            if possible_id_list[4] == cite_info["issue"]:
                                close_matches[possible_id] = search_result[possible_id]
                                continue
                                
                            if verbose: print("Not the right issue")
                            continue
                            
                        if verbose: print("Not the right volume")
                        continue
                        
                    if verbose: print("Not the right year")
                    continue
                    
                if verbose: print("Possible id journal name not exact match")
                continue
                
            if verbose: print("Possible id is not in sim")
            continue
            
        if len(possible_id_list) == 4:
            
            if verbose: print("equal to 4")
            
            # Check that it is sim
            if possible_id_list[0] == "sim":
                
                # Check that journal name matches
                if possible_id_list[1] == cite_info['sim_id'][4:]:
                    
                    # Check that year/date is within other case
                    if str(cite_info["year"]) in possible_id_list[2]:
                        
                        # Check that journal volume matches
                        if possible_id_list[3] == cite_info["volume"]:
                            
                            close_matches[possible_id] = search_result[possible_id]
                            continue
                            
                        if verbose: print("Not the right volume")
                        continue
                        
                    if verbose: print("Not the right year")
                    continue
                    
                if verbose: print("Possible id journal name not exact match")
                continue
                            
            if verbose: print("Possible id is not in sim")
            continue
            
    if verbose: 
        print('close matches: ')
        print(close_matches)
                    
    if not close_matches:
        return ""
    
    close_matches_keys = list(close_matches.keys())
    close_matches_values = list(close_matches.values())
    
    # if 1 close match, return it
    if len(close_matches_keys) == 1:
        return close_matches_keys[0]
    
    
    # if multiple, return the one with the highest score
    index_of_max = close_matches_values.index(max(close_matches_values))
    return close_matches_keys[index_of_max]
    

def generate_url_archive(identifier):
    return "https://archive.org/details/" + identifier


sim_info = pd.read_csv(data_path + "SIM_info.csv")


def process_citation_to_SIM(citation, doi_filter = False, verbose = False):
    
    cite_info = preprocessing_citation(citation)
    if cite_info == "":
        return ""

    # Generate sim ids 
    possible_sim_ids = generate_sim_ids(cite_info['journal'])
    sim_id = ""
    for poss_id in possible_sim_ids:
        if poss_id in sim_info["PubIssueID"].tolist():
            sim_id = poss_id
    
    cite_info["sim_id"] = sim_id
    
    # check if journal in SIM and in year range
    df = sim_info[sim_info["PubIssueID"] == cite_info["sim_id"]]
    
    
    if not df.empty:
        row = df.iloc[0]
        
        if within_year_range(row, cite_info['year']):

            # generate a id
            gen_id = cite_info['sim_id'] + "_" + str(cite_info['year'])
            
            if verbose: print("Gen id: " + gen_id)

            # initialize session
            session, login_data = initialize_archive_session()
            
            # find all entries with this journal name
            search_result = perform_advanced_search(session, login_data, gen_id)
            
            if verbose: 
                print("search results: ")
                print(search_result)

            if search_result != "":

                # find close match on generated id
                real_id = find_close_match_from_cite_info(cite_info, search_result)
                
                if verbose:
                    print("real id: " + real_id)

                if real_id != "":

                    # new citation
                    url = generate_url_archive(real_id)
                    if verbose: print("url: " + url)
                    return url
                
                print("No close match exist for ids. The id is " + gen_id)
                return ""
                
            print("There's no search result for the id: " + gen_id)
            return ""
                
        print("Citation not in SIM collection year range. ")
        return ""
    
    print("Citation not in SIM collection.")
    return "" 


###########################################################################################
###############################  FATCAT COLLECTION  #######################################
###########################################################################################


def generate_url_content(cite_info):
    url_fields = []
    
    if cite_info["journal"] != "":
        url_fields.append("(container_name:" + re.sub(":", "", cite_info["journal"]) + ")")
    if cite_info["title"] != "":
        url_fields.append("(title:" + re.sub(":", "", cite_info["title"]) + ")")
    if cite_info["year"] != 0:
        url_fields.append("(release_year:" + str(cite_info["year"]) + ")")

    url_content = "AND".join(url_fields)
    url_content = re.sub("\[", "", url_content)
    url_content = re.sub("\]", "", url_content)
    
    return url_content


def elastic_search_query_string(url_content):

    query_string = {
      "query": {
        "query_string": {
          "query": url_content
        }
      }
    }
    
    return query_string


def elastic_search_cite_info(url_content, verbose = False):
    
    es = Elasticsearch(["https://search.fatcat.wiki"], timeout = 20)
    
    query_string = elastic_search_query_string(url_content)
    
    if verbose: print(query_string)

    try: 
        response_json = es.search(index="fatcat_release", body = query_string, track_total_hits=True)

        search_results = response_json["hits"]["hits"]
        result = []
        for search_res in search_results:
            search_res_id = search_res["_id"]
            search_res_score = search_res["_score"]
            release = search_res["_source"]
            search_res_info = {"work_id": release["work_id"], "score": search_res_score, 
                                "title": release["title"], 
                                "year": release["release_year"], "journal":release["container_name"],
                                "volume": release["volume"], "issue": release["issue"], "page": release["pages"],
                                "author": release["contrib_names"], "url": release["best_pdf_url"]}
            result.append(search_res_info)

        return result
    except: 
        return ""


def jaccard_similarity(str1, str2):
    
    list1 = str1.split()
    list2 = str2.split()
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union



def fatcat_check_match(cite_info, result, verbose = False):
    
    score = 0
    
    journal_exact_match = False
    journal_partial_match = False
    journal_match_score = 0

    if cite_info["journal"] != "" and result["journal"] != None:
        cite_info["journal"] = cite_info["journal"].strip().lower()
        result["journal"] = result["journal"].strip().lower()
        if cite_info["journal"] == result["journal"] or fuzz.ratio(cite_info["journal"], result["journal"]) == 100:
            journal_exact_match = True
        elif (cite_info["journal"] in result["journal"] or result["journal"] in cite_info["journal"] 
              or fuzz.partial_ratio(cite_info["journal"], result["journal"]) == 100):
            journal_match_partial = False
            
        elif abbreviate_journal_name(cite_info["journal"]) == abbreviate_journal_name(result["journal"]):
            journal_exact_match = True
        elif fuzz.ratio(abbreviate_journal_name(cite_info["journal"]), abbreviate_journal_name(result["journal"])) > 95:
            journal_exact_match = True
        else:
            journal_match_score += fuzz.ratio(cite_info["journal"], result["journal"])/100
    
    # volume 
    volume_match = False
    if result["volume"] != "None" and cite_info["volume"] == result["volume"]:
        volume_match = True
    
    # issue 
    issue_match = False
    if result["issue"] != "None" and cite_info["issue"] == result["issue"]:
        issue_match = True
    
    # year 
    year_match = False
    if result["year"] != "None" and cite_info["year"] == result["year"]:
        year_match = True
        
    # page 
    page_match = False
    if result["page"] != None: 
        if "-" in result["page"]:
            page_start = result["page"].split("-")[0]
            page_end = result["page"].split("-")[0]
            if cite_info["page"] in result["page"]:
                page_match = True
            try: 
                int(page_start)
                int(page_end)
                
                if cite_info["page"] > page_start and cite_info["page"] < page_end:
                    page_match = True
            except:
                page_match = False
        else: 
            if cite_info["page"] in result["page"]:
                page_match = True
        
    # title
    title_exact_match = False
    title_partial_match = False
    title_match_score = 0
    if cite_info["title"] != "" and result["title"] != None:
        cite_info["title"] = cite_info["title"].strip().lower()
        result["title"] = result["title"].strip().lower()
            
        # exact match 
        if cite_info["title"] == result["title"] or fuzz.ratio(cite_info["title"], result["title"]) == 100:
            title_exact_match = True
        # partial match    
        elif (cite_info["title"] in result["title"] or result["title"] in cite_info["title"] 
              or fuzz.partial_ratio(cite_info["title"], result["title"]) == 100):
            title_match_partial = False
        # jaccard similarity
        else:
            title_match_score += fuzz.ratio(cite_info["title"], result["title"])/100
    
    # author
    author_exact_match = False
    author_match_score = 0
    if cite_info["author"] != "":
        # exact match 
        cite_author_lst = cite_info["author"]
        result_author_lst = result["author"]
        
        
        if cite_author_lst == result_author_lst:
            author_exact_match = True
            
#             if verbose: print("author has exact match")
            
        # partial match    
        else:
            if len(cite_author_lst) > len(result_author_lst):
                shorter_lst = result_author_lst
                longer_lst = cite_author_lst
            else:
                shorter_lst = cite_author_lst
                longer_lst = result_author_lst
                
            if len(shorter_lst) > 0:
                author_matches = 0
                for i in range(len(shorter_lst)):
                    value1 = re.sub("[^a-zA-Z\s]", "", shorter_lst[i])
                    value2 = re.sub("[^a-zA-Z\s]", "", longer_lst[i])
                    aut_score = jaccard_similarity(value1, value2)

                    author_matches += aut_score
                author_match_score += author_matches/len(shorter_lst)
        
    
        
    if verbose:
        print("journal exact match: " + str(journal_exact_match))
        print("journal partial match: " + str(journal_partial_match))
        print("volume match: " + str(volume_match))
        print("issue match: " + str(issue_match))
        print("page match: " + str(page_match))
        print("year match: " + str(year_match))
        print("title exact match: " + str(title_exact_match))
        print("title partial match: " + str(title_partial_match))
        print("author exact match: " + str(author_exact_match))
        print("scores:")
        print("journal match score: " + str(journal_match_score))
        print("title match score: " + str(title_match_score))
        print("author match score: " + str(author_match_score))
        
    
    if journal_exact_match:
        temp_score = int(year_match) + int(volume_match) + int(issue_match) + int(page_match) 
        if title_exact_match:
            if temp_score >= 1:
                if verbose: print("journal exact, title exact, 1 other")
                return True
            if int(author_exact_match) >= 1:
                if verbose: print("journal exact, title exact, author exact")
                return True
            if temp_score + author_match_score > 1:
                if verbose: print("journal exact, title exact, 1 other and author score")
                return True
        elif title_partial_match:
            if temp_score >= 2:
                if verbose: print("journal exact, title partial, 2 other")
                return True
            if temp_score + int(author_exact_match) >= 2:
                if verbose: print("journal exact, title exact, 1 other and author exact")
                return True
            if temp_score + author_match_score >= 2:
                if verbose: print("journal exact, title exact, 2 other and author score")
                return True
        else:
            temp_score += int(title_match_score)
            if temp_score + int(author_exact_match) >= 3:
                if verbose: print("journal exact, title score, author exact or 1 other")
                return True
            if temp_score + author_match_score >= 3:
                if verbose: print("journal exact, title score, author score, or 2 other >=3")
                return True
    elif journal_partial_match:
        temp_score = int(year_match) + int(volume_match) + int(issue_match) + int(page_match) + int(author_match_score)
        if title_exact_match:
            if temp_score >= 2:
                if verbose: print("journal partial, title exact, 2 others")
                return True
        elif title_partial_match:
            if temp_score >= 2:
                if verbose: print("journal partial, title partial, 2 others")
                return True
        else:
            temp_score += title_match_score
            if temp_score >= 3:
                if verbose: print("journal partial, title exact, 2 others")
                return True
    else:
        temp_score = int(year_match) + int(volume_match) + int(issue_match) + int(page_match) 
        temp_score += int(author_match_score) + int(journal_match_score) + int(title_match_score)
        if temp_score > 4:
            if verbose: print("5 fields")
            return True
        
    return False



def find_best_cite_info_fatcat_search(cite_info, search_result, verbose = False):
    
    for curr_res in search_result:
        curr_match = fatcat_check_match(cite_info, curr_res, verbose = verbose)
        if curr_match:
            return curr_res
            
    return ""


def abbreviate_journal_name(journal, verbose = False):
    url = "https://abbreviso.toolforge.org/a/" + journal
    request = requests.get(url)
    if request.status_code != 200:
        return journal
    
    return request.text


def generate_scholars_archive_url(work_id):
    header = "https://scholar.archive.org/work/"
    content = str(work_id)
    return header + content


def process_citation_to_scholars(citation, verbose = False):
    
    cite_info = preprocessing_citation(citation)
    if type(cite_info) == str:
        return cite_info
    if verbose: print(cite_info)
    
    url_content = generate_url_content(cite_info)
    search_result = elastic_search_cite_info(url_content, verbose)
    
    if search_result == []:
        return "No search result"
    
    if len(search_result) > 10:
        search_result = search_result[:10]
        
    closest_match = find_best_cite_info_fatcat_search(cite_info, search_result, verbose = verbose)
    
    if closest_match == "":
        return "No close match"
    
    url = closest_match["url"]
    if url == None:
        return "No URL in search result"
    
    work_id = closest_match["work_id"]
    if work_id == "":
        return "No work_id in search result"
    if verbose: print(work_id)
        
    return generate_scholars_archive_url(work_id)


def process_citation_to_either(citation, verbose = False):
    
    cite_info = preprocessing_citation(citation)

    # preprocess data
    if cite_info == "":
        return ""
    
    # If link is in SIM, try to find url to SIM. 
    possible_sim_ids = generate_sim_ids(cite_info['journal'])
    sim_id = ""
    for poss_id in possible_sim_ids:
        if poss_id in sim_info["PubIssueID"].tolist():
            sim_id = poss_id
    cite_info["sim_id"] = sim_id
    df = sim_info[sim_info["PubIssueID"] == cite_info["sim_id"]]
    if not df.empty:
        url_SIM = process_citation_to_SIM(citation, verbose = verbose)
        if url_SIM != "":
            return url_SIM 
    
    # If there is no SIM link, try to find url via fatcat/scholar.
    url_scholar = process_citation_to_scholars(citation, verbose = verbose)
    return url_scholar


###########################################################################################
###################################  Test Cases  ##########################################
###########################################################################################

# ## running SIM process: no output
# test_cite1 = "{{cite journal | last1 = Lewis | first1 = Herbert | date = June 2001 | title = The Passion of Franz Boas | journal = American Anthropologist | volume = 103 | issue = 2| pages = 447–467 | doi=10.1525/aa.2001.103.2.447}}"
# print(test_cite1)
# test_res1 = process_citation_to_SIM(test_cite1)
# print(test_res1)

# ## running scholar process: output with scholar result 
# test_cite8 = "{{Akademik dergi kaynağı|url=|başlık=The mind and brain of short-term memory|yazarlar=Jonides|sayı=|sayfalar=193-224|çalışma=Annual Review of Psychology|yıl=2008|cilt=59}}"
# print(test_cite8)
# test_url8 = process_citation_to_scholars(test_cite8)
# print(test_url8)

# ## running main process: output with SIM result 
# test_cite7 = "{{Akademik dergi kaynağı|başlık=The Mind and Brain of Short-Term Memory|yazarlar=Jonides|tarih=Ocak 2008|sayı=1|sayfalar=193-224|çalışma=Annual Review of Psychology|cilt=59}}"
# print(test_cite7)
# test_url7 = main(test_cite7)
# print(test_url7)


###########################################################################################
################################  Deal with Inputs  #######################################
###########################################################################################

# import sys


# if len(sys.argv) == 3:
#     if sys.argv[1] == "scholar":
#         res_url = process_citation_to_scholars(sys.argv[2])
#         if res_url:
#             # print(res_url)
#             sys.stdout.write(res_url)
#         else:
#             print("no url generated")
#     elif sys.argv[1] == "sim":
#         res_url = process_citation_to_SIM(sys.argv[2])
#         if res_url:
#             # print(res_url)
#             sys.stdout.write(res_url)
#         else:
#             print("no url generated")
#     elif sys.argv[1] == "main": 
#         res_url = main(sys.argv[2])
#         if res_url:
#             # print(res_url)
#             sys.stdout.write(res_url)
#         else:
#             print("no url generated")
#     else:
#         print("invalid operations")
# else: 
#     print("Incorrect argument number")