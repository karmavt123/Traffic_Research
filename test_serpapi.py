from serpapi import GoogleSearch

params = {
    "engine": "google_maps_directions",

    "start_addr": "District 1, Ho Chi Minh City",
    "end_addr": "Thu Duc, Ho Chi Minh City",

    "api_key": "509d60beaf34928723b52d94682e6fc16b2987059fb637dd5923db85f8ffa2e4"
}

search = GoogleSearch(params)

results = search.get_dict()

print(results)