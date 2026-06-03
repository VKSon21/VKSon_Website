import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. White transparency for cards
css_replacements = {
    # Biz Card
    'background:rgba(26,17,40,.75);backdrop-filter:blur(8px);border:1px solid rgba(212,175,55,.2);': 'background:rgba(255,255,255,.05);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.2);',
    'background:rgba(26,17,40,.92);border-color:rgba(212,175,55,.5);box-shadow:0 12px 40px rgba(212,175,55,.15)': 'background:rgba(255,255,255,.15);border-color:rgba(255,255,255,.5);box-shadow:0 12px 40px rgba(255,255,255,.2)',
    
    # Prod Card
    'background:rgba(30,20,48,.85);backdrop-filter:blur(5px);padding:2rem;border-radius:12px;transition:.3s;border-left:3px solid transparent': 'background:rgba(255,255,255,.05);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.2);padding:2rem;border-radius:12px;transition:.3s;',
    'border-left-color:var(--pink);transform:translateX(5px);background:rgba(30,20,48,.95)': 'border-color:rgba(255,255,255,.5);transform:translateX(5px);background:rgba(255,255,255,.15)',
    
    # Video Card
    'background:var(--deep);border-radius:16px;overflow:hidden;transition:transform .3s,box-shadow .3s;cursor:pointer;position:relative': 'background:rgba(255,255,255,.05);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.2);border-radius:16px;overflow:hidden;transition:transform .3s,box-shadow .3s;cursor:pointer;position:relative',
    
    # Studio Card
    '.sCard{background:var(--deep);padding:1.5rem;border-radius:12px}': '.sCard{background:rgba(255,255,255,.05);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.2);padding:1.5rem;border-radius:12px}',
    
    # Post Production Card
    '.ppCard{background:var(--deep);padding:1.8rem;border-radius:12px;transition:.3s}': '.ppCard{background:rgba(255,255,255,.05);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.2);padding:1.8rem;border-radius:12px;transition:.3s}',
    '.ppCard:hover{transform:translateY(-5px);background:rgba(30,20,48,.9)}': '.ppCard:hover{transform:translateY(-5px);background:rgba(255,255,255,.15);border-color:rgba(255,255,255,.5)}',
    
    # Public Reviews Card
    '.rPubCard{background:var(--deep);border-radius:16px;padding:1.5rem;border:1px solid var(--border);transition:.3s}': '.rPubCard{background:rgba(255,255,255,.05);backdrop-filter:blur(12px);border-radius:16px;padding:1.5rem;border:1px solid rgba(255,255,255,.2);transition:.3s}',
    
    # Other tweaks for card text color visibility on white background (optional, but requested "white transparency which looks better")
    # Usually white text on dark background looks good with white transparency.
}

for k, v in css_replacements.items():
    content = content.replace(k, v)

# 2. Emojis to images
emojis = {
    '👗': 'https://images.unsplash.com/photo-1550614000-4b95d4edfa21?w=100&q=80',
    '📱': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=100&q=80',
    '🚗': 'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=100&q=80',
    '⚙️': 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=100&q=80',
    '🎨': 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=100&q=80',
    '🏖️': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=100&q=80',
    '✈️': 'travel.png',
    '🛒': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=100&q=80',
    '🛩️': 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=100&q=80',
    '🌿': 'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=100&q=80',
    '✍️': 'https://images.unsplash.com/photo-1455390582262-044cdead2708?w=100&q=80',
    '🎵': 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=100&q=80',
    '🎬': 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=100&q=80',
    '🎼': 'https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=100&q=80',
    '🌐': 'https://images.unsplash.com/photo-1522204523234-8729aa6e3d5f?w=100&q=80',
    '©️': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=100&q=80',
    '🎥': 'https://images.unsplash.com/photo-1527011045970-16474661ea00?w=100&q=80',
    '🖥️': 'https://images.unsplash.com/photo-1586776977607-310e9c725c35?w=100&q=80',
    '💍': 'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=100&q=80',
    '📣': 'https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=100&q=80',
    '⭐': 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=100&q=80',
    '💕': 'https://images.unsplash.com/photo-1518131557999-702336338fb5?w=100&q=80'
}

for emoji, img_url in emojis.items():
    img_tag = f\'<img src="{img_url}" style="width:40px;height:40px;object-fit:cover;border-radius:8px;" alt="icon">\'
    content = content.replace(f\'>{emoji}<\\', f\'>{img_tag}<\\')

# 3. Rename VK Son to V.K Son
content = content.replace(\'VK Son\', \'V.K Son\')
content = content.replace(\'VK SON\', \'V.K SON\')

# 4. Normal font for phone number
content = content.replace(\'<a href="tel:+918487015439" style="color:inherit">+91 84870 15439</a>\',
                          \'<a href="tel:+918487015439" style="color:inherit; font-family: sans-serif;">+91 84870 15439</a>\')

# 5. Word wrap fix to prevent words from cutting off
if \'body{background:var(--bg)\' in content:
    content = content.replace(\'body{background:var(--bg);color:var(--white);font-family:var(--F2);overflow-x:hidden;font-size:1.05rem}\',
                              \'body{background:var(--bg);color:var(--white);font-family:var(--F2);overflow-x:hidden;font-size:1.05rem;word-wrap:break-word;overflow-wrap:break-word;}\')

# Remove line clamps if any
content = content.replace(\'display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden\', \'\')

with open(\'index.html\', \'w\', encoding=\'utf-8\') as f:
    f.write(content)

print("Done")
