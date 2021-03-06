import re
import pandas as pd
import numpy as np
from os import listdir, path
default_years = [str(y) for y in range(2007, 2021)]

def download_data():
    from bs4 import BeautifulSoup
    import requests
    from pyunpack import Archive
    from os import makedirs, remove

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

def get_filenames(data_dir="data", years=default_years):
    filenames = {}
    for year in years:
      for file_ in listdir(data_dir):
        if year in file_:
          filenames[year] = path.join(data_dir, file_)
          break
      else:
        raise ValueError(f"No data file found for {year}")
    return filenames

def get_data(filenames):
    # load data
    types = {"id": np.int64, 'br': str, 'km': np.float64,
        'latitude': np.float64, 'longitude': np.float64}
    def year_decimal(year):
        return '.' if int(year) <= 2015 else ','

    dfs = {year: pd.read_csv(f, sep=';', encoding='latin',
            dtype=types, decimal=year_decimal(year), na_values="(null)") for
        year, f in filenames.items()}

    # also account for datetime variable
    for df in dfs.values():
        for var in ('data_inversa', 'horario'):
            df[var] = pd.to_datetime(df[var])
    return dfs

if __name__=="__main__":
    print(get_data(get_filenames()))