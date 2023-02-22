import json

with open("message_lemonade_cached.json") as f:
    cached = json.load(f)

with open("message_lemonade_uncached.json") as f:
    uncached = json.load(f)


def check_response(response):
    assert response["status"] == "succeeded"
    assert "output" in response
    assert "image" in response
    assert "input" in response


def print_typescript_interface(response):
    print("interface Response {")
    for key, value in response.items():
        if isinstance(value, dict):
            print(f"  {key}: {{")
            for key2, value2 in value.items():
                print(f"    {key2}: {type(value2).__name__};")
            print("  };")
        else:
            print(f"  {key}: {type(value).__name__};")
    print("}")


print_typescript_interface(cached)
print_typescript_interface(uncached)


check_response(cached)
check_response(uncached)

assert cached["image"] == uncached["image"]

assert cached["output"].keys() == uncached["output"].keys()
