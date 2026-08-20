import string

def extract_strings(filename, min_length=4):
    with open(filename, 'rb') as f:
        data = f.read()

    strings = []
    current_string = ""
    for byte in data:
        char = chr(byte)
        if char in string.printable and char not in ['\n', '\r', '\t']:
            current_string += char
        else:
            if len(current_string) >= min_length:
                strings.append(current_string)
            current_string = ""

    if len(current_string) >= min_length:
        strings.append(current_string)

    with open('scratch/lidwa_apk/strings.txt', 'w', encoding='utf-8') as f:
        for s in strings:
            f.write(s + '\n')

extract_strings('scratch/lidwa_apk/classes.dex')
