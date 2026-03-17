import os

def test(directory):
    mobile_file = os.path.join(directory, 'mobile-al', 'index.html')
    main_file = os.path.join(directory, 'index.html')
    
    with open(mobile_file, 'r', encoding='utf-8') as f: mobile_content = f.read()
    with open(main_file, 'r', encoding='utf-8') as f: new_content = f.read()

    def get_all_spans_after(content, marker):
        spans = []
        idx = 0
        while True:
            idx = content.find(marker, idx)
            if idx == -1: break
            span_start = content.find('<span', idx)
            if span_start == -1: break
            span_end = content.find('</span>', span_start) + 7
            spans.append(content[span_start:span_end])
            idx = span_end
        return spans

    old_nonm = get_all_spans_after(mobile_content, 'name="consent_nonmarketing"')
    new_nonm = get_all_spans_after(new_content, 'name="consent_nonmarketing"')

    print("--- OLD HERO SPAN ---")
    print(repr(old_nonm[0]))
    print("--- NEW HERO SPAN ---")
    print(repr(new_nonm[0]))

    if old_nonm[0] == new_nonm[0]:
        print("THEY ARE IDENTICAL?? (This would cause 0 updates)")
    else:
        print("They are different.")

    # Try replacement
    c = mobile_content
    c2 = c.replace(old_nonm[0], new_nonm[0])
    print(f"Replacement changed file: {c != c2}")

if __name__ == "__main__":
    import sys
    test(sys.argv[1] if len(sys.argv) > 1 else ".")
