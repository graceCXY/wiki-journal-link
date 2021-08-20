import requests
import urllib.parse
import json
import time
import re


### perform http request 
# INPUT:
## language: wikipedia language (ex.en, tr)
## citation: the citation input ({{cite journal}})
## verbose: debug mode 
# OUTPUT:
## json object 
def get_wikimedia_json(language, source, citation, verbose = False):
    
    ### build url
    url_header = "https://" + language + "." + source + ".org/w/api.php?action=parse&text="
    url_content = urllib.parse.quote(citation, safe = "")
    url_param = "&contentmodel=wikitext&format=json"
    
    url = url_header + url_content + url_param
    
    ### debug
    if verbose: print(url)
    
    ### make http requests
    response = requests.get(url, timeout = 20)
    if response.status_code != 200:
        time.sleep(15)
        response = requests.get(url, timeout = 20)
        if response.status_code != 200:
            time.sleep(15)
            response = requests.get(url, timeout = 20)
            if response.status_code != 200:
                time.sleep(15)
                response = requests.get(url, timeout = 20)
                if response.status_code != 200:
                    return ""
    
    try: 
        res_json = json.loads(response.text)
    except:
        return ""
    
    return res_json


### find html element strings with href 
# INPUT:
## json: json object returned by wikipedia parse
# OUTPUT:
## list of html strings with href 
def find_html_lst_from_json(json, verbose = False):
    if json == "":
        return ""
    
    html_str = json["parse"]["text"]["*"]
    if verbose: print(html_str)
        
    html_tags = [m.span() for m in re.finditer(r'<[^>]*>', html_str)]
    
    if verbose: print(html_tags)
    has_href = []
    for t_loc in html_tags:
        start = t_loc[0]
        end = t_loc[1]
        substr = html_str[start:end]
        if "href" in substr:
            has_href.append(substr)
    
    return has_href


### find html element strings with href 
# INPUT:
## list of html strings with href 
# OUTPUT:
## list of urls
def find_urls(html_lst, verbose = False):
    
    urls = []
    for element in html_lst:
        element = re.sub("<", "", element)
        element = re.sub(">", "", element)
        attr_lst = element.split()
        
        if verbose: print(attr_lst)
            
        for attr in attr_lst:
            
            if "=" in attr:
                field_name = attr.split("=")[0].strip()
                field_content = attr.split("=")[1].strip()
                
                if verbose:
                    print(attr)
                    print(field_name)
                    print(field_content)
                    
                if "href" == field_name or "href" in field_name:
                    
                    if verbose: print("it's href")
                
                    
                    url_regex = r"\/\/[a-zA-Z0-9]+\.[^\s]{2,}"
        
                    if re.search(url_regex, field_content):
                
                        if verbose: 
                            print("match")
                        
                        urls.append(field_content)
                        break
                    else: 
                        if verbose: print('href content is not url')
                        
    return urls
                

### Main function to checking if auto url exists
# Input:
## language: wikipedia language (ex.en, tr)
## citation: the citation input ({{cite journal}})
# Output:
## Boolean: True or False

def autourl_exists(citation, language = "en", source = "wikipedia", verbose = False):
    
    res_json = get_wikimedia_json(language, source, citation, verbose)
    
    if res_json == "":
        return False
    
    html_lst = find_html_lst_from_json(res_json, verbose)
    
    if html_lst == [] or html_lst == None:
        return False
    
    urls = find_urls(html_lst, verbose)
    
    if urls == []:
        return False
    
    return True
        

