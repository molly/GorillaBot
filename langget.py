import re

file = open('stats.html', 'r')
html = file.read()
file.close()
regex = r'<td\sclass\="text"><a\shref\=".*?">(.*?)</a></td>\s+<td\sclass\="text"><a\shref\=".*?">(.*?)</a></td><td\sclass\="text"><a\shref\=".*?">(.*?)</a></td>'
list = re.findall(regex, html)
for entry in list:
    if '&' in entry[1]:
        split = re.split(r'(&#\d{3,5};)', entry[1])
        for part in split:
            if '&' in part:
