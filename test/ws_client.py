import json

import rel
import websocket
from utils import generate_test_token


class WebsocketError(Exception):
    pass


class WebsockerClosed(Exception):
    pass


def ws_client(backend, request):
    backends = {
        "prod": "wss://rest.pollinations.ai",
        "dev": "wss://worker-dev.pollinations.ai",
        "local": "ws://localhost:6000",
    }
    backend_url = backends[backend]

    def on_message(ws, message):
        print(json.loads(message))

    def on_error(ws, error):
        raise error

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")
        raise WebsockerClosed(close_msg)

    def on_open(ws):
        ws.send(json.dumps(request))

    websocket.enableTrace(True)
    token = generate_test_token()
    ws = websocket.WebSocketApp(
        f"{backend_url}/ws?token={token}",
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


if __name__ == "__main__":
    ws_client()
