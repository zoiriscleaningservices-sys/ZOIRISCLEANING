import os
import sys
import time
import re
from concurrent.futures import ProcessPoolExecutor

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        orig_content = content
        
        # Regex is safe and doesn't rely on another file's state
        hero_nonmarketing_pattern = re.compile(
            r'(<input type="checkbox" name="consent_nonmarketing"[^>]*>\s*)<span style="font-size:0.68rem;color:rgba\(255,255,255,0.65\);line-height:1.55;">(?:By checking this box, I\s*consent to receive <strong style="color:#fff;">non-marketing text messages</strong> from|I consent to receive <strong style="color:#fff;">non-marketing text messages</strong>).*?</span>',
            re.DOTALL | re.IGNORECASE
        )
        hero_marketing_pattern = re.compile(
            r'(<input type="checkbox" name="consent_marketing"[^>]*>\s*)<span style="font-size:0.68rem;color:rgba\(255,255,255,0.65\);line-height:1.55;">(?:By checking this box, I\s*consent to receive <strong style="color:#fff;">marketing and promotional text messages</strong>|I consent to receive <strong style="color:#fff;">marketing and promotional text messages</strong>).*?</span>',
            re.DOTALL | re.IGNORECASE
        )
        
        contact_nonmarketing_pattern = re.compile(
            r'(<input type="checkbox" name="consent_nonmarketing"[^>]*>\s*)<span style="font-size:0.71rem;color:rgba\(255,255,255,0.7\);line-height:1.5;">(?:I consent to receive\s*<strong style="color:#fff;">non-marketing messages</strong>).*?</span>',
            re.DOTALL | re.IGNORECASE
        )
        contact_marketing_pattern = re.compile(
            r'(<input type="checkbox" name="consent_marketing"[^>]*>\s*)<span style="font-size:0.71rem;color:rgba\(255,255,255,0.7\);line-height:1.5;">(?:I consent to receive\s*<strong style="color:#fff;">marketing &(?:amp;)? promotional messages</strong>).*?</span>',
            re.DOTALL | re.IGNORECASE
        )

        hero_nonmarketing_replacement = r'\1<span style="font-size:0.68rem;color:rgba(255,255,255,0.65);line-height:1.55;">I consent to Receive SMS Notifications, Alerts from <strong style="color:#fff;">Zoiris Cleaning Services</strong>. Message frequency varies. Message &amp; data rates may apply. Text HELP to <strong style="color:#fff;">+1 251-220-2515</strong> for assistance. You can reply STOP to unsubscribe at any time.</span>'
        hero_marketing_replacement = r'\1<span style="font-size:0.68rem;color:rgba(255,255,255,0.65);line-height:1.55;">By checking this box I agree to receive occasional marketing messages from <strong style="color:#fff;">Zoiris Cleaning Services</strong>.</span>'
        
        contact_nonmarketing_replacement = r'\1<span style="font-size:0.71rem;color:rgba(255,255,255,0.7);line-height:1.5;">I consent to Receive SMS Notifications, Alerts from <strong style="color:#fff;">Zoiris Cleaning Services</strong>. Message frequency varies. Message &amp; data rates may apply. Text HELP to <strong style="color:#fff;">+1 251-220-2515</strong> for assistance. You can reply STOP to unsubscribe at any time.</span>'
        contact_marketing_replacement = r'\1<span style="font-size:0.71rem;color:rgba(255,255,255,0.7);line-height:1.5;">By checking this box I agree to receive occasional marketing messages from <strong style="color:#fff;">Zoiris Cleaning Services</strong>.</span>'

        content = hero_nonmarketing_pattern.sub(hero_nonmarketing_replacement, content)
        content = hero_marketing_pattern.sub(hero_marketing_replacement, content)
        content = contact_nonmarketing_pattern.sub(contact_nonmarketing_replacement, content)
        content = contact_marketing_pattern.sub(contact_marketing_replacement, content)

        if content != orig_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, True
        return True, False
    except Exception:
        return False, False

def chunk_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def process_chunk(filepaths):
    processed = 0
    updated = 0
    for fp in filepaths:
        r1, r2 = process_file(fp)
        if r1: processed += 1
        if r2: updated += 1
    return processed, updated

def run_all(directory):
    print("Gathering files...", flush=True)
    all_files = []
    
    for d in os.listdir(directory):
        d_path = os.path.join(directory, d)
        if os.path.isdir(d_path):
            if d.endswith('-al') or d.endswith('-tx'):
                for root, dirs, files in os.walk(d_path):
                    for file in files:
                        if file.endswith('.html'):
                            all_files.append(os.path.join(root, file))
    
    total_files = len(all_files)
    print(f"Total HTML files to process: {total_files}", flush=True)
    
    t0 = time.time()
    
    chunk_size = 500
    chunks = list(chunk_list(all_files, chunk_size))
    
    processed_count = 0
    updated_count = 0

    with ProcessPoolExecutor() as executor:
        for p, u in executor.map(process_chunk, chunks):
            processed_count += p
            updated_count += u
            print(f"Progress: {processed_count}/{total_files} | Fixed: {updated_count}", flush=True)

    t1 = time.time()
    print(f"Done. Processed {processed_count} files, updated {updated_count} files in {t1-t0:.2f}s.", flush=True)

if __name__ == "__main__":
    run_all(sys.argv[1] if len(sys.argv) > 1 else ".")
