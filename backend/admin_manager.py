import base64
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PLAIN_FILE = os.path.join(DATA_DIR, "telugu_badwords.txt")
SECURE_FILE = os.path.join(DATA_DIR, "secure_words.bin")

def load_secure_words():
    if not os.path.exists(SECURE_FILE):
        return []
    try:
        with open(SECURE_FILE, "rb") as f:
            encoded_data = f.read()
            decoded_data = base64.b64decode(encoded_data).decode("utf-8")
            return [w.strip() for w in decoded_data.splitlines() if w.strip()]
    except Exception as e:
        print(f"Error loading secure file: {e}")
        return []

def save_secure_words(words):
    try:
        content = "\n".join(words)
        encoded_data = base64.b64encode(content.encode("utf-8"))
        with open(SECURE_FILE, "wb") as f:
            f.write(encoded_data)
        print(f"Successfully saved {len(words)} words to secure storage.")
    except Exception as e:
        print(f"Error saving secure file: {e}")

def migrate():
    if not os.path.exists(PLAIN_FILE):
        print(f"No plain text file found at {PLAIN_FILE}")
        return
    
    print(f"Migrating {PLAIN_FILE} to secure storage...")
    with open(PLAIN_FILE, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    save_secure_words(words)
    print("Migration complete. You can now safely delete the .txt file.")

def view_words():
    words = load_secure_words()
    print(f"--- SECURE WORD LIST ({len(words)} words) ---")
    for w in words:
        print(w)
    print("-------------------------------------------")

def add_word(word):
    words = load_secure_words()
    if word in words:
        print(f"'{word}' is already in the list.")
        return
    words.append(word)
    save_secure_words(words)
    print(f"Added '{word}'.")

def remove_word(word):
    words = load_secure_words()
    if word not in words:
        print(f"'{word}' not found in the list.")
        return
    words = [w for w in words if w != word]
    save_secure_words(words)
    print(f"Removed '{word}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python admin_manager.py [migrate|view|add <word>|remove <word>]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "migrate":
        migrate()
    elif command == "view":
        view_words()
    elif command == "add" and len(sys.argv) > 2:
        add_word(sys.argv[2])
    elif command == "remove" and len(sys.argv) > 2:
        remove_word(sys.argv[2])
    else:
        print("Invalid command or missing argument.")
