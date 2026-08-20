import re

with open('scripts/4_matan_linker.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace normalize_arabic mojibake
old_normalize = """def normalize_arabic(text):
    if not text:
        return ""
    text = re.sub(r'[\\u200e\\u200f\\u202a-\\u202e\\u200b\\u200c\\u200d\\uFEFF]', '', text)
    text = re.sub(r'[\\u0617-\\u061A\\u064B-\\u0652]', '', text)
    text = re.sub(r'[Ã˜Â¥Ã˜Â£Ã˜Â¢Ã˜Â§]', 'Ã˜Â§', text)
    text = re.sub(r'[Ã˜Â©]', 'Ù‡', text)
    text = re.sub(r'[Ù‰]', 'ÙŠ', text)
    text = re.sub(r'[\\W_]+', '', text)
    return text"""

new_normalize = """def normalize_arabic(text):
    if not text:
        return ""
    text = re.sub(r'[\\u200e\\u200f\\u202a-\\u202e\\u200b\\u200c\\u200d\\uFEFF]', '', text)
    text = re.sub(r'[\\u0617-\\u061A\\u064B-\\u0652]', '', text)
    text = re.sub(r'[\\u0625\\u0623\\u0622\\u0627]', '\\u0627', text)
    text = re.sub(r'[\\u0629]', '\\u0647', text)
    text = re.sub(r'[\\u0649]', '\\u064A', text)
    text = re.sub(r'[\\W_]+', '', text)
    return text"""

content = re.sub(r'def normalize_arabic\(text\):.*?return text', new_normalize, content, flags=re.DOTALL)

# Replace extract_matan mojibake
old_extract = """def extract_matan(text):
    norm = normalize_arabic(text)
    if not norm: return ""
    markers = ["Ù‚Ø§Ù„Ø±Ø³ÙˆÙ„Ø§Ù„Ù„Ù‡", "Ø³Ù…Ø¹ØªØ±Ø³ÙˆÙ„Ø§Ù„Ù„Ù‡", "Ø¹Ù†Ø§Ù„Ù†Ø¨Ù‰", "ÙŠÙ‚ÙˆÙ„Ø±Ø³ÙˆÙ„Ø§Ù„Ù„Ù‡", "Ø§Ù†Ø±Ø³ÙˆÙ„Ø§Ù„Ù„Ù‡", "Ø¹Ù†Ø±Ø³ÙˆÙ„Ø§Ù„Ù„Ù‡", "Ù‚Ø§Ù„Ø§Ù„Ù†Ø¨Ù‰", "Ø³Ù…Ø¹ØªØ§Ù„Ù†Ø¨Ù‰"]"""

new_extract = """def extract_matan(text):
    norm = normalize_arabic(text)
    if not norm: return ""
    markers = ["\\u0642\\u0627\\u0644\\u0631\\u0633\\u0648\\u0644\\u0627\\u0644\\u0644\\u0647", "\\u0633\\u0645\\u0639\\u062a\\u0631\\u0633\\u0648\\u0644\\u0627\\u0644\\u0644\\u0647", "\\u0639\\u0646\\u0627\\u0644\\u0646\\u0628\\u0649", "\\u064a\\u0642\\u0648\\u0644\\u0631\\u0633\\u0648\\u0644\\u0627\\u0644\\u0644\\u0647", "\\u0627\\u0646\\u0631\\u0633\\u0648\\u0644\\u0627\\u0644\\u0644\\u0647", "\\u0639\\u0646\\u0631\\u0633\\u0648\\u0644\\u0627\\u0644\\u0644\\u0647", "\\u0642\\u0627\\u0644\\u0627\\u0644\\u0646\\u0628\\u0649", "\\u0633\\u0645\\u0639\\u062a\\u0627\\u0644\\u0646\\u0628\\u0649"]"""

content = re.sub(r'def extract_matan\(text\):.*?markers = \[[^\]]+\]', new_extract, content, flags=re.DOTALL)

with open('scripts/4_matan_linker.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed 4_matan_linker.py")
