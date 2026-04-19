import urllib.request, urllib.parse, json

url = "https://api.telegram.org/bot8696199318:AAH38shv8GbeEkSZvWcUnpWD-ihtWCyQLig/sendMessage"
data = json.dumps({"chat_id": "5851162500", "text": "Test direct verification Telegram Bot"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as response:
        print("Response:", response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print("Error:", str(e))
