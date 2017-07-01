# spaceship generator


import bs4
import requests

descripts = []


def gen_spaceship():
    # generate a spaceship
    ships = {"names": [], "type": [], "weapons": [], "defence": [], "condition": [], "constructed_by": []}
    #  fields = ["Spaceship name:", "Type:", "Condition:", "Weapons:", "Defence:", "Constructed by:", "Ship name:", "Defence:", "Class:"]
    url = "http://www.scifiideas.com/spaceship-generator/"
    #  print url
    response = requests.get(url)
    # tree = html.fromstring(response.content)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    text = soup.select("p")
    for t in text:
        ts = t.get_text().split("\n")
        for t in ts:
            if "Spaceship name:" in t or "Ship name:" in t:
                t = t.replace("Spaceship name:", "").replace("Ship name:", "")
                if t not in ships["names"]:
                    ships["names"].append(t)
            elif "Constructed by:" in t:
                t = t.replace("Constructed by:", "")
                if t not in ships["constructed_by"]:
                    ships["constructed_by"].append(t)
            elif "Type:" in t or "Class:" in t:
                t = t.replace("Class:", "").replace("Type:", "")
                if t not in ships["type"]:
                    ships["type"].append(t)
            elif "Weapons:" in t:
                t = t.replace("Weapons:", "")
                if t not in ships["weapons"]:
                    ships["weapons"].append(t)
            elif "Condition:" in t:
                t = t.replace("Condition:", "")
                if t not in ships["condition"]:
                    ships["condition"].append(t)
            elif "Defence:" in t:
                t = t.replace("Defence:", "")
                if t not in ships["defence"]:
                    ships["defence"].append(t)
    # print text
    return ships


print gen_spaceship()
# self.Name = soup.select('h1 a[href^=http://www.metal-archives.com]')[0].get_text()
# self.link = soup.select('h1 a[href^=http://www.metal-archives.com]')[0].attrs.get('href')
# self.Style =
# self.Theme = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[2]/text()")[0]
# self.Label = tree.xpath(".//*[@id='band_stats']/dl[2]/dd[3]/text()")[0]
