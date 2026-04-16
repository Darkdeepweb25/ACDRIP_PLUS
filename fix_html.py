import re

with open('frontend/index.html', encoding='utf-8') as f:
    content = f.read()

# Find the orphaned block - starts after the new section ends (</div>\n\n) and contains the old threat feed card
# The old block is between the section </div></div> and the MITRE comment

# Strategy: Find lines 565-624 region using unique markers
start_marker = '\n\n            <div class="card" style="margin-top: 24px;">\n                <div class="card-header">\n                    <div class="card-title"><span class="icon">🚨</span> Live Threat Feed'
end_marker = '        <!-- ===== 7. MITRE ATT'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx) if start_idx >= 0 else -1

if start_idx >= 0 and end_idx > start_idx:
    removed = content[start_idx:end_idx]
    content = content[:start_idx] + '\n\n        ' + content[end_idx:]
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'SUCCESS: Removed {len(removed)} chars of orphaned HTML')
elif start_idx < 0:
    print('Old block start marker not found - may already be clean')
else:
    print('End marker not found after start')
