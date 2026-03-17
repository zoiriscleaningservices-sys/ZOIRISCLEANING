import os
import re

def update_forms(directory):
    files_updated = 0
    
    hero_nonmarketing_pattern = re.compile(
        r'(<input type="checkbox" name="consent_nonmarketing"[^>]*>\s*)<span style="font-size:0.68rem;color:rgba\(255,255,255,0.65\);line-height:1.55;">.*?</span>',
        re.DOTALL | re.IGNORECASE
    )
    hero_marketing_pattern = re.compile(
        r'(<input type="checkbox" name="consent_marketing"[^>]*>\s*)<span style="font-size:0.68rem;color:rgba\(255,255,255,0.65\);line-height:1.55;">.*?</span>',
        re.DOTALL | re.IGNORECASE
    )
    
    contact_nonmarketing_pattern = re.compile(
        r'(<input type="checkbox" name="consent_nonmarketing"[^>]*>\s*)<span style="font-size:0.71rem;color:rgba\(255,255,255,0.7\);line-height:1.5;">.*?</span>',
        re.DOTALL | re.IGNORECASE
    )
    contact_marketing_pattern = re.compile(
        r'(<input type="checkbox" name="consent_marketing"[^>]*>\s*)<span style="font-size:0.71rem;color:rgba\(255,255,255,0.7\);line-height:1.5;">.*?</span>',
        re.DOTALL | re.IGNORECASE
    )

    hero_nonmarketing_replacement = r'\1<span style="font-size:0.68rem;color:rgba(255,255,255,0.65);line-height:1.55;">I consent to Receive SMS Notifications, Alerts from <strong style="color:#fff;">Zoiris Cleaning Services</strong>. Message frequency varies. Message &amp; data rates may apply. Text HELP to <strong style="color:#fff;">+1 251-220-2515</strong> for assistance. You can reply STOP to unsubscribe at any time.</span>'
    hero_marketing_replacement = r'\1<span style="font-size:0.68rem;color:rgba(255,255,255,0.65);line-height:1.55;">By checking this box I agree to receive occasional marketing messages from <strong style="color:#fff;">Zoiris Cleaning Services</strong>.</span>'
    
    contact_nonmarketing_replacement = r'\1<span style="font-size:0.71rem;color:rgba(255,255,255,0.7);line-height:1.5;">I consent to Receive SMS Notifications, Alerts from <strong style="color:#fff;">Zoiris Cleaning Services</strong>. Message frequency varies. Message &amp; data rates may apply. Text HELP to <strong style="color:#fff;">+1 251-220-2515</strong> for assistance. You can reply STOP to unsubscribe at any time.</span>'
    contact_marketing_replacement = r'\1<span style="font-size:0.71rem;color:rgba(255,255,255,0.7);line-height:1.5;">By checking this box I agree to receive occasional marketing messages from <strong style="color:#fff;">Zoiris Cleaning Services</strong>.</span>'

    for root, dirs, files in os.walk(directory):
        # Skip .git etc
        if '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    orig_content = content
                    
                    content = hero_nonmarketing_pattern.sub(hero_nonmarketing_replacement, content)
                    content = hero_marketing_pattern.sub(hero_marketing_replacement, content)
                    content = contact_nonmarketing_pattern.sub(contact_nonmarketing_replacement, content)
                    content = contact_marketing_pattern.sub(contact_marketing_replacement, content)
                    
                    if content != orig_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        files_updated += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    
    print(f"Updated {files_updated} files with new consent text.")

if __name__ == "__main__":
    import sys
    # Allow passing directory as argument, otherwise use current
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    update_forms(target_dir)
