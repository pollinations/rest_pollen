import random

import boto3

from rest_pollen.authentication import supabase

s3 = boto3.client("s3")


bucket_name = "pollinations-ci-bucket"
# prefix = "avatars4/"  # Optional prefix to limit results to a specific folder
prefix_raw = "raw/"
prefix_approved = "meme-avatars/"
avatar_table = "wedatanation-avatar"


animals = ["wolf", "lion", "owl", "bear", "gorilla", "sloth", "rabbit", "fox"]

attributes = [
    "conservative",
    "sporty",
    "modern",
    "old",
    "young",
    "baby",
    "chubby",
    "business dude",
    "doctor",
    "scientist",
    "astronaut",
    "cyborg",
    "hippie",
    "hip hop",
    "rock 'n' roll",
    "painter",
    "happy",
    "curious",
    "hero",
]

items = [
    "golf club",
    "tennis racket",
    "baseball bat",
    "sword",
    "laptop",
    "headphones",
    "phone",
    "guitar",
    "microphone",
    "camera",
    "nerd glasses",
    "top hat",
    "cowboy hat",
    "flowers",
    "coffee",
    "book",
    "suit and tie",
    "sun glasses",
    "sunglasses",
]


def get_all_image_urls(bucket=bucket_name, prefix=prefix_approved):
    response = s3.list_objects(Bucket=bucket, Prefix=prefix)
    if "Contents" in response:
        available = [obj["Key"] for obj in response["Contents"]]
    else:
        available = []
    avatar_urls = [
        f"https://{bucket_name}.s3.amazonaws.com/{avatar}" for avatar in available
    ]
    return avatar_urls


def get_available(prefix, animal=None):
    response = s3.list_objects(Bucket=bucket_name, Prefix=prefix)
    if "Contents" in response:
        available = [obj["Key"] for obj in response["Contents"]]
    else:
        return []
    # remove used avatars from available
    used = supabase.table(avatar_table).select("img_url").execute().data
    used = [i["img_url"].replace("url:", "") for i in used]
    available = [i for i in available if i not in used]

    if animal is None:
        return available
    selection = [i for i in available if animal in i]
    return selection


def _find_avatar(animal, item, attribute, num_suggestions):
    available = get_available(prefix_approved, animal)
    if len(available) < num_suggestions:
        available = get_available(prefix_raw, animal)
    if len(available) < num_suggestions:
        available = get_available(prefix_approved)
    if len(available) < num_suggestions:
        available = get_available(prefix_raw)
    if item is not None:
        selection = [i for i in available if item in i]
        if len(selection) >= num_suggestions:
            available = selection
    if attribute is not None:
        selection = [i for i in available if attribute in i]
        if len(selection) >= num_suggestions:
            available = selection
    avatars = random.sample(available, num_suggestions)
    avatar_urls = [
        f"https://{bucket_name}.s3.amazonaws.com/{avatar}" for avatar in avatars
    ]
    return avatar_urls


def get_attributes(description):
    description = description.lower()
    animal = [i for i in animals if i in description]
    item = [i for i in items if i in description]
    attribute = [i for i in attributes if i in description]
    if len(animal) == 0:
        animal = None
    else:
        animal = animal[0]
    if len(item) == 0:
        item = None
    else:
        item = item[0]
    if len(attribute) == 0:
        attribute = None
    else:
        attribute = attribute[0]
    if item == "sunglasses":
        item = "sun glasses"
    return animal, item, attribute


def find_avatar(description, num_suggestions):
    animal, item, attribute = get_attributes(description)
    return _find_avatar(animal, item, attribute, num_suggestions)
