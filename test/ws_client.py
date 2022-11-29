import json

import rel
import websocket
from utils import generate_test_token


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    ws.send(get_dreamachine_request())


def get_dreamachine_request():
    request = {
        "image": "replicate:stability-ai/stable-diffusion",
        "input": {
            "prompt": "A knight on a horse made out of stars and a galactic nebula"
        },
    }
    return json.dumps(request)


if __name__ == "__main__":
    websocket.enableTrace(True)
    token = generate_test_token()
    ws = websocket.WebSocketApp(
        f"ws://localhost:5000/ws?token={token}",
        # "wss://worker-dev.pollinations.ai/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever(
        dispatcher=rel, reconnect=5
    )  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
