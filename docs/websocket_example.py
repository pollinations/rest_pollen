import json
import os

import rel
import websocket


class WebsocketError(Exception):
    pass


class WebsockerClosed(Exception):
    pass


def ws_client(request):
    backend_url = "wss://rest.pollinations.ai"

    def on_message(ws, message):
        print(json.loads(message))

    def on_error(ws, error):
        raise error

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(ws):
        ws.send(json.dumps(request))

    websocket.enableTrace(True)
    token = os.environ["POLLINATIONS_API_KEY"]
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
    request = {
        "image": "stability-ai/stable-diffusion",
        "input": {"prompt": "a horse made out of clouds"},
    }
    ws_client(request)
