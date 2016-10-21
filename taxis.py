import requests
import lxml.html
import datetime
import re
import html as htmllib
import scraperwiki

# handle escape codes correctly

def cleanse(text, prefix=None):
    # remove tags
    text = htmllib.unescape(text)
    text = re.sub('\<[^>]*\>', '', text)
    if prefix:
        assert len(prefix) == 1
        if text.startswith(prefix):
            text = text[1:]
        if text.startswith(":"):
            text = text[1:]
        text = text.strip()
    return text
        


# TODO: drop database at start

url = "https://www.visitljubljana.com/en/visitors/explore-the-region/traffic-and-transport/taxi/"

html = requests.get(url).text

root = lxml.html.fromstring(html)
content = root.xpath(".//div[@class='detail has-content']")[0]

content_text = lxml.html.tostring(content).decode('utf-8')
for tag in ["<p>", "</p>", "<br>"]:
    content_text = content_text.replace(tag, "\n")

#print (content_text)

# Take a really dumb approach: change record when you hit a <strong>, record data when you hit a T M E W starting line...
# </a> does screw this up a little -- TODO

data = []
current_record = {}
in_progress = False

for line in content_text.split('\n'):
    l = line.strip()
    if l.startswith("<strong>"):
        if current_record:
            data.append(current_record)
            current_record = {}
        current_record['name'] = cleanse(l)
        current_record['id'] = cleanse(l)
        current_record['scraped'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if l.startswith("T"):
        clean = cleanse(l, "T")
        if ',' in clean:
            current_record['telephone'], current_record['mobile'] = clean.split(',')
        else:
            current_record['telephone'] = clean
    if l.startswith("E"):
        current_record['email'] = cleanse(l, "E")
    if l.startswith("W"):
        current_record['url'] = cleanse(l, "W")
        
    
        
for item in data:
    for key in item:
        print (key, cleanse(item[key]))
        
    print()        
        
    