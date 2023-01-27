import json

import websocket
from utils import (  # noqa
    generate_test_token,
    get_lemonade_request,
    get_stablediffusion_request,
)


class WebsocketError(Exception):
    pass


class WebsockerClosed(Exception):
    pass


def ws_client(backend, request):
    backends = {
        "prod": "wss://rest.pollinations.ai",
        "dev": "wss://worker-dev.pollinations.ai",
        "local": "ws://localhost:7000",
    }
    backend_url = backends[backend]

    print(request)

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
    token = generate_test_token()  # noqa
    ws = websocket.WebSocketApp(
        # f"{backend_url}/ws?token={token}",
        f"{backend_url}/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    # run until closed
    ws.run_forever()


if __name__ == "__main__":
    # ws_client("local", get_stablediffusion_request(True))
    # ws_client("local", get_stablediffusion_request())
    # ws_client("local", get_lemonade_request())
    ws_client("local", get_lemonade_request(True))
