import re
with open('york-al/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

head_pattern = re.compile(r'<title>.*?(?=<!-- / Yoast SEO plugin\. -->|<!-- Favicons -->)', re.DOTALL | re.IGNORECASE)
hero_pattern = re.compile(r'(<h1 class="text-3xl[^>]*>).*?(</h1>\s*<p class="text-base[^>]*>).*?(</p>)', re.DOTALL | re.IGNORECASE)

match_head = head_pattern.search(content)
print('Head match:', bool(match_head))

match_hero = hero_pattern.search(content)
print('Hero match:', bool(match_hero))
