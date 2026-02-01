"""
Test script to verify emoji detection in the comment moderation system
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_emoji_detection():
    print("=" * 60)
    print("Testing Emoji Detection in Comment Moderation System")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Test 1: Middle finger emoji",
            "text": "You are bad 🖕",
            "strictness": "high",
            "expected_toxic": True
        },
        {
            "name": "Test 2: Eggplant emoji",
            "text": "Check this out 🍆",
            "strictness": "high",
            "expected_toxic": True
        },
        {
            "name": "Test 3: Peach emoji",
            "text": "Nice 🍑",
            "strictness": "high",
            "expected_toxic": True
        },
        {
            "name": "Test 4: Knife emoji",
            "text": "I will 🔪 you",
            "strictness": "high",
            "expected_toxic": True
        },
        {
            "name": "Test 5: Safe emojis",
            "text": "Great post! 👍😊❤️",
            "strictness": "high",
            "expected_toxic": False
        },
        {
            "name": "Test 6: Multiple safe emojis",
            "text": "Amazing work! 🎉🎊🌟✨",
            "strictness": "high",
            "expected_toxic": False
        },
        {
            "name": "Test 7: Mixed - offensive in middle",
            "text": "Hello 🖕 friend",
            "strictness": "high",
            "expected_toxic": True
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print(f"Text: {test['text']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/analyze",
                json={"text": test["text"], "strictness": test["strictness"]},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                is_toxic = result.get("is_toxic", False)
                results = result.get("results", [])
                
                # Check if result matches expectation
                status = "✓ PASS" if is_toxic == test["expected_toxic"] else "✗ FAIL"
                print(f"Result: is_toxic={is_toxic} (expected={test['expected_toxic']}) {status}")
                
                if results:
                    print(f"Detection: {results[0]['label']} (score: {results[0]['score']:.2f})")
            else:
                print(f"✗ FAIL - HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("✗ ERROR - Could not connect to server. Is it running?")
            print("Start the server with: py main.py")
            break
        except Exception as e:
            print(f"✗ ERROR - {str(e)}")
    
    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_emoji_detection()
