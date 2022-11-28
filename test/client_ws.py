import json

from websocket import create_connection


def get_dreamachine_request():
    request = {
        "image": "replicate:stability-ai/stable-diffusion",
        "input": {
            "prompt": "A knight on a horse made out of stars and a galactic nebula"
        },
    }
    return request


ws = create_connection("ws://localhost:5000/live")
breakpoint()
print("Sending")
ws.send(json.dumps(get_dreamachine_request()))
print("Sent")
while True:
    print("Receiving...")
    result = ws.recv()
    print("Received '%s'" % result)
    if result == "done":
        break
ws.close()
