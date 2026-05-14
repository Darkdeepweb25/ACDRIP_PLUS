with open('frontend/index.html', 'r', encoding='utf-8') as f:
    t = f.read()
import re
m = t.split('id="section-mitre"')[1].split('id="section-darkweb"')[0]
o = len(re.findall(r'<div\b[^>]*>', m))
c = len(re.findall(r'</div\s*>', m))
print('MITRE Balance:', o - c)
