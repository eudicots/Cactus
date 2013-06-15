
from datetime import date

MAIN_PAGES = []

def preBuildPage(site, page, context, data):

	if "sitemap.xml" == page.path:
		context['now'] = date.today().strftime("%Y-%m-%d")
		#context['URI'] = "http://www.example.com/"
		
	return context, data
