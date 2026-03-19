import os
import re

def fix_canonicals(base_dir):
    # Regex to find canonical tags pointing to anything under the city slug
    # We want to replace it with the city slug itself.
    # Pattern looks like: <link rel="canonical" href="https://www.zoiriscleaningservices.com/CITY-SLUG/SERVICE-SLUG/" />
    canonical_pattern = re.compile(r'<link rel="canonical" href="https://www\.zoiriscleaningservices\.com/([^/]+)/[^/]+/"\s*/>')
    
    count = 0
    errors = 0
    
    # Precompile the replacement string using the matched city slug group \1
    
    for root, dirs, files in os.walk(base_dir):
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == '.': continue
            
        parts = rel_path.split(os.sep)
        city_slug = parts[0]
        
        # Only process city folders ending in -al
        if not city_slug.endswith('-al'): continue
            
        # We only want to modify service pages, not the city root page itself
        if len(parts) == 1:
            continue
            
        for file in files:
            if not file.endswith('.html'): continue
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace service canonical with city canonical
                # e.g., <link rel="canonical" href="https://www.zoiriscleaningservices.com/albertville-al/" />
                replacement = f'<link rel="canonical" href="https://www.zoiriscleaningservices.com/{city_slug}/" />'
                
                content = canonical_pattern.sub(replacement, content)
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1
            except Exception as e:
                errors += 1
                
    print(f"✅ Updated canonical tags in {count} HTML service files. Errors: {errors}")

if __name__ == '__main__':
    fix_canonicals('.')
