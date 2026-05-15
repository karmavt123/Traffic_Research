from serpapi import GoogleSearch
import pandas as pd
from datetime import datetime
import time

API_KEY = "509d60beaf34928723b52d94682e6fc16b2987059fb637dd5923db85f8ffa2e4"

# ===== ROUTES =====
routes = [
    {
        "origin": "Ben Thanh Market, Ho Chi Minh City",
        "destination": "Landmark 81, Ho Chi Minh City"
    },

    {
        "origin": "Tan Son Nhat Airport, Ho Chi Minh City",
        "destination": "Thu Duc, Ho Chi Minh City"
    },

    {
        "origin": "District 7, Ho Chi Minh City",
        "destination": "District 1, Ho Chi Minh City"
    }
]

records = []

# ===== MAIN LOOP =====
while True:

    for route_info in routes:

        try:

            params = {
                "engine": "google_maps_directions",

                "start_addr": route_info["origin"],
                "end_addr": route_info["destination"],

                "api_key": API_KEY
            }

            search = GoogleSearch(params)

            results = search.get_dict()

            # ===== DEBUG =====
            print(results.keys())

            # ===== CHECK =====
            if "directions" not in results:

                print("No directions found")
                print(results)

                continue

            direction = results["directions"][0]

            record = {
                "timestamp": datetime.now(),

                "origin": route_info["origin"],
                "destination": route_info["destination"],

                "distance": direction.get("distance", "N/A"),
                "duration": direction.get("duration", "N/A")
            }

            records.append(record)

            df = pd.DataFrame(records)

            df.to_csv("eta_dataset.csv", index=False)

            print(record)

        except Exception as e:

            print("ERROR:", e)

    # ===== WAIT 5 MIN =====
    time.sleep(300)