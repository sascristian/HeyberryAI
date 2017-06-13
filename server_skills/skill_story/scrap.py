import requests
from lxml import html
import bs4
from os.path import dirname

dialog = []
names = ["SPOCK", "ONE", "ANDROMEDA", "HUNT", "RHADE", "HARPER", "TYR", "BEM", "COMPUTER", "BEKA",
         "TYLER", "PIKE", "GARISON", "BOYCE", "COLT", "KIRK", "UHURA", "BALOK", "BAILEY", "MCCOY",
         "SCOTT", "SULU", "CHEKOV"]

# scrap star trek tos dialog
for i in range(1, 80):
    url = "http://www.chakoteya.net/StarTrek/" + str(i) + ".htm"
    print url
    response = requests.get(url)
    tree = html.fromstring(response.content)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    text = soup.select("p")
    for t in text:
        t = t.get_text().replace("[OC]", "").replace(":", "").replace("[OC}", "").replace(";", "")
        lines = t.split("\n")
        for line in lines:
            named = False
            for name in names:
                if name in line:
                    named = True
                    line = line.replace(name, "")
            if named:
                dialog.append(line)


with open(dirname(__file__) + "/dialog/sci_fi.txt", "wb") as f:
    for line in dialog:
        try:
            f.write(line)
        except:
            pass
    f.close()

print dialog


#self.Name = soup.select('h1 a[href^=http://www.metal-archives.com]')[0].get_text()
#self.link = soup.select('h1 a[href^=http://www.metal-archives.com]')[0].attrs.get('href')
#self.Style = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[1]/text()")[0]
#self.Theme = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[2]/text()")[0]
#self.Label = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[3]/text()")[0]