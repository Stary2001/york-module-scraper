import os.path
import os
import requests
from bs4 import BeautifulSoup

def apply_terrible_workaround(text):
	# The module text has nested <p> tags, which is invalid HTML.
	# The rest of the HTML is too broken to use the 'xml' type which would allow this to work
	# So instead, we do this.
	# I hate it, and I hope you hate it too.
	return text.replace("<p>","<p-nt>").replace("</p>","</p-nt>")

def cached_get(url):
	cache_filename = "cache/"+url.replace("/","_")
	if os.path.exists(cache_filename):
		print("hit")
		return open(cache_filename,"r").read()
	else:
		resp = requests.get(url)
		text = apply_terrible_workaround(resp.text)
		with open(cache_filename, "w") as f:
			f.write(text)
		return text

os.makedirs("cache", exist_ok=True)
url = "https://www.york.ac.uk/students/studying/manage/programmes/module-catalogue/module"
off = 0
max = 10000
resp = cached_get(url+f"?query=&department=&year=2018-19&offset={off}&max={max}")
page = BeautifulSoup(resp, 'html')
tab = page.find("table")

class Module:
	def __init__(self, link, id):
		self.detail_url = "https://www.york.ac.uk" + link['href']
		self.name = link.get_text()
		self.id = id

modules = {}

for c in tab.select("tr"):
	cols = c.select("td")
	if len(cols) == 0:
		continue

	link = cols[0].contents[0]
	module_id = cols[1].get_text()
	modules[module_id] = Module(link, module_id)

for (id,mod) in modules.items():
	detail_page = cached_get(mod.detail_url)
	detail_page = BeautifulSoup(detail_page, 'html')
	content = detail_page.select_one('#mdcolumn')
	for header in content.select('h2'):
		title = header.get_text()
		maybe_section=header.findNext()
		print(title, maybe_section)
	exit()