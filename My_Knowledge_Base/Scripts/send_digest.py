# -*- coding: utf-8 -*-
import sys, io, urllib.request, json, uuid, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

TOKEN = '8784420556:AAH-9kjv374fgDcHRX_UwXv4C_m2YBuZ9a4'
CHAT = '-1003790798162'
TOPIC = '7'

cover_path = 'My_Knowledge_Base/Cover_Elements/output/cover.png'

with open('My_Knowledge_Base/Scripts/digest_post.txt', encoding='utf-8') as f:
    post_text = f.read()

# sendPhoto
boundary = uuid.uuid4().hex
parts = []
for name, val in [('chat_id', CHAT), ('message_thread_id', TOPIC)]:
    parts.append(('--' + boundary + '\r\nContent-Disposition: form-data; name="' + name + '"\r\n\r\n' + val).encode('utf-8'))
with open(cover_path, 'rb') as f:
    photo_data = f.read()
parts.append(
    ('--' + boundary + '\r\nContent-Disposition: form-data; name="photo"; filename="cover.png"\r\nContent-Type: image/png\r\n\r\n').encode('utf-8')
    + photo_data
)
body = b'\r\n'.join(parts) + ('\r\n--' + boundary + '--\r\n').encode('utf-8')
req = urllib.request.Request(
    'https://api.telegram.org/bot' + TOKEN + '/sendPhoto',
    data=body,
    headers={'Content-Type': 'multipart/form-data; boundary=' + boundary}
)
resp = urllib.request.urlopen(req)
result = json.loads(resp.read().decode('utf-8'))
print("Photo sent: message_id=" + str(result.get('result', {}).get('message_id')))

# sendMessage
payload = json.dumps({
    'chat_id': CHAT,
    'message_thread_id': int(TOPIC),
    'text': post_text,
    'parse_mode': 'HTML'
}).encode('utf-8')
req2 = urllib.request.Request(
    'https://api.telegram.org/bot' + TOKEN + '/sendMessage',
    data=payload,
    headers={'Content-Type': 'application/json'}
)
resp2 = urllib.request.urlopen(req2)
result2 = json.loads(resp2.read().decode('utf-8'))
print("Message sent: message_id=" + str(result2.get('result', {}).get('message_id')))
