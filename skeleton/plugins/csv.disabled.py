import os
import csv
INFO = {
	'name': 'CSV Importer',
	'description': 'Read csv-file as array of dicts into context'
}

"""
Each row is parsed and put into a dictionairy. 
!First line! is discarded for as keys. Following lines as values.
rowdata in context is an array of dicts.

Usage:

  {% for row in csvrows %}
    <div id="{{ row.ID }}" class="well">
      <a href="{{ row.link }}">
      <h1> {{ row.title }} </h1>
      </a>
      <p>{{ row.description }}</p>
    </div>
  {% endfor %}

Set the csv-file to parse at config.json like:

   {
     "csv" : "myfile.csv"
   }

"""

csvrows = []

def preBuild(site):
        li = 0
        keys = []
        reader = csv.reader(open(site.config.get('csv'),'r'))
        for row in reader:
                if li == 0:
                        keys = row
                        li += 1
                        continue
                        
                i = 0
                rowdict = {}
                for key in keys:
                        rowdict[key] = row[i]
                        i += 1
                        
                csvrows.append(rowdict)
        
def preBuildPage(site, page, context, data):
        context["csvrows"] = csvrows
        return context, data


