import os

file_path = 'frontend/js/app.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("Shor\\\\'s", "Shor\\'s")
content = content.replace("Grover\\\\'s", "Grover\\'s")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
