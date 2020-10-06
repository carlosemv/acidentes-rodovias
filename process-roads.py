import numpy as np
import pandas as pd
from os import listdir, path
import re

all_sups = ['DUP', 'EOD', 'EOI',
	'EOP', 'IMP', 'LEN',
	'PAV', 'PLA', 'TRV']

sup = 'Superfície Federal'
length = 'Extensão'

data_dir = 'data/roads'
dfs = {}
for f in listdir(data_dir):
	y = re.match(r'[A-Z]+_?(\d{4})', f).group(1)
	header_line = 1 if int(y) < 2010 else 2
	df = pd.read_excel(path.join(data_dir, f),
		header=header_line)

	if int(y) < 2010:
		df.rename(columns={'SUPERFICIE': sup,
			'EXTENSAO': length}, inplace=True)
	if int(y) > 2015:
		eo = 'OBRAS'
		df[sup] = np.where(~df[eo].isnull(),
			df[eo], df[sup])
	dfs[y] = df

data = {}
for y in map(str, range(2007,2020)):
	df = dfs[y]
	data[y] = df[df[sup].isin(all_sups)].groupby(
		sup).sum()[length].to_dict()
sup_df = pd.DataFrame.from_dict(data)
sup_df['sup'] = sup_df.index
sup_df.reset_index(drop=True, inplace=True)
print(sup_df)
sup_df.to_csv('data/roads-data.csv', index=False)