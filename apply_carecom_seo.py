import os
import re

head_pattern = re.compile(
    r'<title>.*?(?=<!-- / Yoast SEO plugin\. -->|<!-- Favicons -->)',
    re.DOTALL | re.IGNORECASE
)

hero_pattern = re.compile(
    r'(<h1 class="text-3xl[^>]*>).*?(</h1>\s*<p class="text-base[^>]*>).*?(</p>)',
    re.DOTALL | re.IGNORECASE
)

root_dir = os.path.dirname(os.path.abspath(__file__))

# Pages that shouldn't use "Service" naming
NON_SERVICES = {"about", "contact", "blog", "terms", "privacy", "404", "dashboard", "gallery"}

def process_file(filepath):
    try:
        # Determine location and service from filepath
        rel_path = os.path.relpath(filepath, root_dir)
        parts = rel_path.split(os.sep)
        
        # Default to Mobile, AL for root pages
        location_slug = "mobile-al"
        location_title = "Mobile, AL"
        service_slug = ""
        service_name = "House Cleaning"
        
        # Parse path logic
        if len(parts) >= 2 and parts[0].endswith("-al"):
            # It's a city folder
            location_slug = parts[0]
            location_title = " ".join([word.capitalize() for word in location_slug.split("-")])
            if location_title.endswith(" Al"):
                location_title = location_title[:-3] + ", AL"
                
            if len(parts) >= 3 and parts[1].endswith(".html"):
                # e.g. abbeville-al/index.html
                pass
            elif len(parts) >= 3:
                # e.g. abbeville-al/deep-cleaning/index.html
                service_slug = parts[1]
                if service_slug in NON_SERVICES:
                    service_name = "House Cleaning" # Fallback to core keyword
                elif service_slug.lower().startswith("detailing"):
                    service_name = "Detailing"
                else:
                    service_name = " ".join([word.capitalize() for word in service_slug.split("-")])
        elif parts[0] == "locations":
            location_title = "Alabama"
            location_slug = "locations"
        elif len(parts) == 1 and parts[0].endswith(".html"):
            # Root files
            name = parts[0][:-5]
            if name.lower() in NON_SERVICES:
                service_name = "House Cleaning"
            elif name != "index":
                service_name = " ".join([word.capitalize() for word in name.split("-")])
        else:
            # Other root directories like Gallery/
            location_title = "Mobile, AL"
            location_slug = "mobile-al"
            service_slug = parts[0]
            if service_slug.lower() in NON_SERVICES:
                service_name = "House Cleaning"
            else:
                service_name = " ".join([word.capitalize() for word in service_slug.split("-")])

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Build canonical
        canonical_url = f"https://www.zoiriscleaningservices.com/"
        if location_slug != "mobile-al":
            canonical_url += f"{location_slug}/"
        if service_slug and service_slug != "index":
            canonical_url += f"{service_slug}/"
            
        # Build keywords
        if service_name.lower() == "house cleaning":
            keywords = f"House Cleaning in {location_title}"
        else:
            keywords = f"House Cleaning in {location_title}, {service_name} in {location_title}"

        new_head = f"""<title>{service_name} Services in {location_title} - Top Rated Cleaners</title>
  <meta name="description" content="Find affordable {service_name.lower()} options in {location_title}. Search local cleaners by rates, reviews, experience, and more. Match made with Zoiris Cleaning Services." />
  <meta name="keywords" content="{keywords}" />
  <link rel="canonical" href="{canonical_url}" />
  <meta property="og:title" content="{service_name} Services in {location_title} - Top Rated Cleaners" />
  <meta property="og:type" content="website" />
  <meta property="og:image" content="https://imgur.com/yjACVrG.png" />
  <meta property="og:image:width" content="512" />
  <meta property="og:image:height" content="512" />
  <meta property="og:image:type" content="image/png" />
  <meta property="og:url" content="{canonical_url}" />
  <meta property="og:description" content="Find affordable {service_name.lower()} options in {location_title}. Search local cleaners by rates, reviews, experience, and more. Match made with Zoiris Cleaning Services." />
  <meta property="og:site_name" content="Zoiris Cleaning Services" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content="@themaidscorp" />
  <link rel="sitemap" type="application/xml" href="https://www.zoiriscleaningservices.com/sitemap_index.xml" />
  """

        # Replace head block
        content, n_head = head_pattern.subn(new_head, content, count=1)

        # Build new hero content
        new_h1_text = f"\n          Find Trusted {service_name} Services in {location_title}\n        "
        new_p_text = f"\n          We have top-rated local cleaners in {location_title}. Explore {service_name.lower()} services and compare your options to find the right fit for your home and schedule.\n        "
        
        # Replace hero block
        content, n_hero = hero_pattern.subn(r'\1' + new_h1_text + r'\2' + new_p_text + r'\3', content, count=1)

        # Only write if we actually modified something
        if n_head > 0 or n_hero > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

if __name__ == '__main__':
    import concurrent.futures
    import multiprocessing

    filepaths = []
    for root, dirs, files in os.walk(root_dir):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            if file.endswith(".html"):
                filepaths.append(os.path.join(root, file))
                
    print(f"Found {len(filepaths)} HTML files to process. Starting parallel execution...")

    count = 0
    # Use ThreadPoolExecutor to speed up I/O bound file operations
    with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 4) as executor:
        futures = [executor.submit(process_file, fp) for fp in filepaths]
        for future in concurrent.futures.as_completed(futures):
            try:
                if future.result():
                    count += 1
                    if count % 100 == 0:
                        print(f"Processed {count} files so far...", flush=True)
            except Exception as e:
                pass

    print(f"Successfully processed {count} files.")
