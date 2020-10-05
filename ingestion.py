from bs4 import BeautifulSoup
import requests
import re
from os import makedirs, path, remove, listdir
from pyunpack import Archive

# downloading page with links
main_url = "https://portal.prf.gov.br/dados-abertos-acidentes"
page = requests.get(main_url)
soup = BeautifulSoup(page.text)

# extracting urls from relevant links
header = soup.find("strong", text=re.compile("por ocorrência"))
links = header.find_next('ul').find_all("a", href=True)
urls = {a.string: a['href']+"/download" for a in links}

data_dir = "data"
makedirs(data_dir, exist_ok=True)
filenames = {}
for year, url in urls.items():
  # download content
  resp = requests.get(url)

  # get file name
  fname = re.search('filename="(.+)"',
    resp.headers['content-disposition']).group(1)
  fname = path.join(data_dir, fname)
  print(fname)
  filenames[year] = fname

  # save content
  with open(fname, 'wb') as f:
    f.write(resp.content)

for filename in filenames.values():
  # extract files
  Archive(filename).extractall(data_dir)
  # remove compressed files
  remove(filename)

# get new filenames
new_files = listdir(data_dir)
for year in filenames.keys():
  for file_ in new_files:
    if year in file_:
      filenames[year] = path.join(data_dir, file_)
      break
  else:
    raise ValueError(f"No data file found for {year}")
