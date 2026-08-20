import re

with open('script.js', 'r', encoding='utf-8') as f:
    content = f.read()

# For Banks
content = re.sub(r'h\.casa \* 100', r'(h.casa || 0) * 100', content)
content = re.sub(r'h\.nim \* 100', r'(h.nim || 0) * 100', content)
content = re.sub(r'h\.llr \* 100', r'(h.llr || 0) * 100', content)
content = re.sub(r'h\.pb\.toFixed', r'(h.pb || 0).toFixed', content)
content = re.sub(r'h\.npl \* 100', r'(h.npl || 0) * 100', content)
content = re.sub(r'h\.ep \* 100', r'(h.ep || 0) * 100', content)

# For Non-Banks
content = re.sub(r'h\.roic \* 100', r'(h.roic || 0) * 100', content)
content = re.sub(r'h\.de\.toFixed', r'(h.de || 0).toFixed', content)
content = re.sub(r'\(h\.ni !== 0 \? \(h\.cfo / h\.ni\) : 0\)', r'(h.ni ? (h.cfo / h.ni) : 0)', content)
content = re.sub(r'\(h\.bp > 0 \? 1 / h\.bp : 0\)', r'(h.bp ? 1 / h.bp : 0)', content)
content = re.sub(r'h\.icr\.toFixed', r'(h.icr || 0).toFixed', content)
# h.ep * 100 is already covered

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched script.js")
