"""
Script to update secure_words.bin from telugu_badwords.txt
This encodes the bad words list in base64 for secure storage
"""

import base64

# Read the Telugu bad words from text file
with open('data/telugu_badwords.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Encode to base64
encoded = base64.b64encode(content.encode('utf-8'))

# Write to secure binary file
with open('data/secure_words.bin', 'wb') as f:
    f.write(encoded)

print(f"✓ Successfully updated secure_words.bin")
print(f"✓ Total bad words: {len(content.splitlines())}")
