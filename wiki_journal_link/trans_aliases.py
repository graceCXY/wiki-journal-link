

def get_aliases(citation):

    lang = "tr"
    
    ### Default is in english and turkish
    journal_aliases = ['journal', 'newspaper', 'magazine', 'work','website',  'periodical', 
                       'encyclopedia', 'encyclopaedia', 'dictionary', 'mailinglist', 'dergi', 'gazete', 
                       'eser', 'çalışma', 'iş', 'websitesi', 'süreliyayın', 'ansiklopedi', 'sözlük', 'program']
    date_aliases = ['date', 'air-date', 'airdate', 'tarih']
    year_aliases = ['year', 'yıl', 'sene']
    volume_aliases = ['volume', 'cilt']
    issue_aliases = ['issue', 'number', 'sayı', 'numara']
    page_aliases = ['p', 'page', 's', 'sayfa']
    pages_aliases = ['pp', 'pages', 'ss', 'sayfalar']
    url_aliases = ['url', 'URL', 'katkı-url', 'chapter-url', 'contribution-url', 'entry-url', 
               'article-url', 'section-url']
    title_aliases= ['title', 'başlık']
    ext_id_aliases = ['pmid', 'PMID', 'jstor', 'doi', 'DOI', 'isbn', 'ISBN', 'pmc', "oclc", "OCLC", "lccn", "LCCN"]
    author_aliases = ['authors', 'people', 'credits', 'host', 'yazarlar', 'yazars', 'katkıdabulunanlar', 
                  'muhataplar', 'kişiler']
    first_name_aliases = ["first#", "given#", "author-first#", "author#-first", "ad#", "ilk#", "muhatapadı#"]
    last_name_aliases = ["last#", "author#", "surname#", "author-last#", "author#-last", "subject#", "son#", 
                     "soyadı#", "yazar#", "muhatap#", "muhatapsoyadı#", "özne#", "süje#", "konu#"]
    
    this_journal = []
    this_date = []
    this_year = []
    this_volume = []
    this_issue = []
    this_page = []
    this_pages = []
    this_title = []
    this_author = []
    this_first_name = []
    this_last_name = []
    
    ### Todo: better language detection
    # b = TextBlob(citation)
    # lang = b.detect_language()
    if lang == "nl":
        this_journal = []
        this_date = ["datum"]
        this_year = []
        this_volume = ["version", "edition", "editie"]
        this_issue = []
        this_page = []
        this_pages = ["pagina's", "paginas"]
        this_title = ["titel"]
        this_author = ["auteur", "auteur#", "medeauteurs#", "editor#"]
        this_first_name = ["voornaam#"]
        this_last_name = ["achternaam#"]
    
#     ### template for adding in new languages
#     if lang == "":
#         this_journal = []
#         this_date = []
#         this_year = []
#         this_volume = []
#         this_issue = []
#         this_page = []
#         this_pages = []
#         this_title = []
#         this_author = []
#         this_first_name = []
#         this_last_name = []
        
    journal_aliases.extend(this_journal)
    date_aliases.extend(this_date) 
    year_aliases.extend(this_year) 
    volume_aliases.extend(this_volume) 
    issue_aliases.extend(this_issue)
    page_aliases.extend(this_page) 
    pages_aliases.extend(this_pages)
    title_aliases.extend(this_title) 
    author_aliases.extend(this_author) 
    first_name_aliases.extend(this_first_name) 
    last_name_aliases.extend(this_last_name)
    
        
    return [journal_aliases, date_aliases, year_aliases, volume_aliases, issue_aliases, page_aliases, pages_aliases, 
            url_aliases, title_aliases, ext_id_aliases, author_aliases, first_name_aliases, last_name_aliases]
