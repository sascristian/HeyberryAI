
import requests
from lxml import html
import bs4

response = requests.get('http://www.metal-archives.com/band/random')
tree = html.fromstring(response.content)
soup = bs4.BeautifulSoup(response.text, "lxml")

name = soup.select('h1 a[href^=http://www.metal-archives.com]')[0].get_text()
link = soup.select('h1 a[href^=http://www.metal-archives.com]')[0].attrs.get('href')
style = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[1]/text()")[0]
lyrics = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[2]/text()")[0]
label = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[3]/text()")[0]
country = tree.xpath(".//*[@id='band_stats']/dl[1]/dd[1]/a/text()")[0]
location = tree.xpath(".//*[@id='band_stats']/dl[1]/dd[2]/text()")[0]
status = tree.xpath(".//*[@id='band_stats']/dl[1]/dd[3]/text()")[0]
formation_date = tree.xpath(".//*[@id='band_stats']/dl[1]/dd[4]/text()")[0]
years_active = tree.xpath(".//*[@id='band_stats']/dl[3]/dd/text()")[0]
years_active = years_active.strip()
print "Name: "+name
print "Link: " +link
print "Style: "+style
print "Theme: "+lyrics
print "Label: " +label
print "Country: "+country
print "Location: "+location
print "Status: "+status
print "Date: "+formation_date
print years_active
