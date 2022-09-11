from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
from datetime import datetime
import os
from multiprocessing import Pool
import sys
import os


from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())


df = pd.read_csv('proteins_166_159857.csv')


loci = df['Locus tag']

map_rv_ra = {}



column_names = ["Rv", "Ra", "Ra_UNIPROT"]

df = pd.DataFrame(columns = column_names)

start = 3806
intervalo = 100
end = start+intervalo

for index, locus in enumerate(loci[start:end]):
	print(locus)
	link = 'https://www.kegg.jp/ssdb-bin/ssdb_best?org_gene=mtu:' + locus
	driver.get(link)

	try:
		WebDriverWait(driver, 40
		).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'mra:')))
	except TimeoutException:
		print("Timed out, no se pudo encontrar el ortologo de Ra")
		print('Locus Rv:', locus)
		print('Salteando')
		continue



	MRA_gen = driver.find_elements(By.PARTIAL_LINK_TEXT, 'mra:')[0]

	MRA_gen_link = MRA_gen.get_attribute('href')
	MRA_gen = MRA_gen.get_attribute('text')
	# map_rv_ra = {locus = MRA_gen}


	print(MRA_gen)
	print(MRA_gen_link)

	driver.get(MRA_gen_link)


	try:
		WebDriverWait(driver, 40
		).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'A5')))
	except TimeoutException:
		print("Timed out, no se pudo encontrar el codigo UNIPROT")
		print('Locus Rv:', locus)
		print('Salteando')
		continue


	MRA_gen_uniprot = driver.find_elements(By.PARTIAL_LINK_TEXT, 'A5')[0]
	MRA_gen_uniprot = MRA_gen_uniprot.get_attribute('text')

	
	print(MRA_gen_uniprot)
	map_rv_ra[index] = {'Rv' : locus, 'Ra': MRA_gen, 'Ra_UNIPROT' : MRA_gen_uniprot}

	if (index+1) % 25 == 0:

		print('Guardando dataset')
		print('Ultimo gen guardado:', locus)

		df_temp = pd.DataFrame(map_rv_ra)
		map_rv_ra = {}

		df_temp = df_temp.transpose()

		df = pd.concat([df, df_temp])

		nombre_csv = 'Rv_to_Ra' + str(start) + '.csv'

		df.to_csv(nombre_csv)