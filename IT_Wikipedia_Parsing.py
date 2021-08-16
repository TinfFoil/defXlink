# Retrieve html of Italian wiki dump
base_url = 'https://dumps.wikimedia.org/itwiki/'
index = requests.get(base_url).text
soup_index = BeautifulSoup(index, 'html.parser')

# Find the links that are dates of dumps
dumps = [a['href'] for a in soup_index.find_all('a') if a.has_attr('href')]
print("list of latest dumps:", dumps)

dump_url = base_url + '20210720/'

# Retrieve the html and convert to soup
dump_html = requests.get(dump_url).text
soup_dump = BeautifulSoup(dump_html, 'html.parser')

files = []

# Search through all files
for file in soup_dump.find_all('li', {'class': 'file'}):
    text = file.text
    # Select the files that have "pages-articles" and append them to files list
    if 'pages-articles' in text:
        files.append((text.split()[0], text.split()[1:]))        
print("list of page-articles files:", files[:10])

# Get only partitioned files
files_to_download = [file[0] for file in files if '.xml-p' in file[0]]
print("num partitioned files:", len(files_to_download))
print("list of partitioned files:", files_to_download)

