import os

def check_file(directory):
    mobile_file = os.path.join(directory, 'mobile-al', 'index.html')
    main_file = os.path.join(directory, 'index.html')
    test_file = os.path.join(directory, 'abbeville-al', 'index.html') # A different generated file
    
    with open(mobile_file, 'r', encoding='utf-8') as f: mobile_content = f.read()
    with open(main_file, 'r', encoding='utf-8') as f: new_content = f.read()
    with open(test_file, 'r', encoding='utf-8') as f: test_content = f.read()

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

    # Try replacement on test file
    c2 = test_content.replace(old_nonm[0], new_nonm[0])
    print(f"Replacement on abbeville-al changed file: {test_content != c2}")
    
    if test_content == c2:
        print("Failed to replace! Let's check if the span exists in test_content:")
        test_nonm = get_all_spans_after(test_content, 'name="consent_nonmarketing"')
        print("--- TEST SPAN ---")
        print(repr(test_nonm[0]))
        print("--- OLD SPAN (we are searching for) ---")
        print(repr(old_nonm[0]))

if __name__ == "__main__":
    import sys
    check_file(sys.argv[1] if len(sys.argv) > 1 else ".")
