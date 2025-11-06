import cloudscraper
import time
from pathlib import Path

scraper = cloudscraper.create_scraper()
id=15366280
while id>0:
	path="data/html/{}.html".format(id)
	if not Path(path).is_file():
		url = 'https://www.nettiauto.com/{}'.format(id)
		response = scraper.get(url)
		fp=open(path,'w')
		fp.write(response.text)
		fp.close()

		print("Scraped id {}".format(id))
		time.sleep(1)
	else:
		print("Skipped id {}".format(id))
	id=id-1
