original = {
    "image": "replicate:pollinations/lemonade-preset",
    "input": {
        "image": "https://store.pollinations.ai/ipfs/QmejbsQbhi4UsNGEeDSRszpzXv6W6CR61Gk2TZ53vQx5sT?filename=00003.png"
    },
    "output": {
        "prompt": "archer arcane modern disney - beautiful happy mohawk black hair 10 years old african american male. With white caucasian skin. With black eyes. wearing a baseball cap hat. with a beard beard with a fake mustache moustache wearing sunglasses. Distinctive features: blue and yellow",
        "answers": '{"hairstyle": "mohawk", "hair_color": "black", "ethnicity": "african american", "hat": "baseball cap", "beard": "beard", "moustache": "fake mustache", "age": "10", "skin_type": "caucasian", "skin_color": "white", "eyes": "black", "glasses": "sunglasses", "gender": "male", "distinctive_features": "blue and yellow"}',
        "avatars": [
            "https://replicate.delivery/pbxt/WfrcB5WVNMyAL6WXE8iPLdDRRMPNzmgsbN1QF1p3AYPbxyCIA/avatar_0.png"
        ],
        "removed_background": "https://replicate.delivery/pbxt/JGw25dnE0fRXYKmpxY69hwoTxDPV0qZ3r0l0eccOJ932ilFQA/removed_bg.png",
    },
    "status": "succeeded",
}

stored = {
    "image": "replicate:pollinations/lemonade-preset",
    "input": {
        "image": "https://store.pollinations.ai/ipfs/QmejbsQbhi4UsNGEeDSRszpzXv6W6CR61Gk2TZ53vQx5sT?filename=00003.png"
    },
    "output": {
        ".cid": "QmdVVnSDS7eA6annuM1bEpVdsn6i31k46uh2nFthwhXkSp",
        "answers": '{"hairstyle": "mohawk", "hair_color": "black", "ethnicity": "african american", "hat": "baseball cap", "beard": "beard", "moustache": "fake mustache", "age": "10", "skin_type": "caucasian", "skin_color": "white", "eyes": "black", "glasses": "sunglasses", "gender": "male", "distinctive_features": "blue and yellow"}',
        "avatars": {
            "0": "https://store.pollinations.ai/ipfs/Qmdtveu2VKcqXcMum2mrUSknET4VCCfCxmwRoqQVg2JVqz?filename=0",
            ".cid": "QmWFHyK2MJ5EpiLjWmQsvNqUYgh9n87Ctd7DYKVcwUT9M1",
        },
        "prompt": "archer arcane modern disney - beautiful happy mohawk black hair 10 years old african american male. With white caucasian skin. With black eyes. wearing a baseball cap hat. with a beard beard with a fake mustache moustache wearing sunglasses. Distinctive features: blue and yellow",
        "removed_background": "https://store.pollinations.ai/ipfs/QmfRZCWg6fZzE1JAd9qPWztzu99ZuKhoRrf8tztx7t1FtP?filename=removed_background",
    },
    "status": "success",
}


def adjust_format(data):
    if isinstance(data, list):
        return [adjust_format(x) for x in data]
    elif isinstance(data, dict):
        if "0" in data:
            return [adjust_format(data[k]) for k in sorted(data.keys()) if k.isdigit()]
        else:
            return {k: adjust_format(v) for k, v in data.items() if k != ".cid"}
    else:
        return data


rec = adjust_format(stored)
breakpoint()
