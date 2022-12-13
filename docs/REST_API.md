# Pollinations REST API

The main endpoint to use all models is the [`/pollen`](https://rest.pollinations.ai/pollen) endpoint.
It accepts a POST request with a JSON body that contains the model name and its inputs.
The response is a JSON object with the results.
The endpoint is described on [`openapi.json`](https://rest.pollinations.ai/openapi.json) and can be browsed via [/redoc](https://rest.pollinations.ai/redoc) or [/docs](https://rest.pollinations.ai/docs`).

Input and output format are model specific and described on [`/redoc/<model-author>/<model-name>/`](https://rest.pollinations.ai/redoc/<model-author>/<model-name>/) or [`/docs/<model-author>/`](https://rest.pollinations.ai/docs/<model-author>/<model-name>/).

A list of the available models can be found on [`/models`](https://rest.pollinations.ai/models).


Example:
    
    import requests
    import os

    backend_url = "https://rest.pollinations.ai"

    request = {
        "image": "pollinations/stable-diffusion-private",
        "input": {"prompts": "a horse made out of clouds"},
    }

    output = requests.post(
        f"{backend_url}/pollen",
        json=request,
        headers={"Authorization": f"Bearer {os.environ['POLLINATIONS_API_KEY']}"},
    )

    print(output.text)