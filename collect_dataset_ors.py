import openrouteservice
import pandas as pd
from datetime import datetime
import time

API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImQwYmQ5NWY5ODg3MjQ3Y2NhYmU5ZmE0MzIyM2ZmNmY5IiwiaCI6Im11cm11cjY0In0="

client = openrouteservice.Client(key=API_KEY)

coords = (
    (106.6533165423355, 10.792940135155595),
    (106.68143886196094, 10.777981481676393)
)

records = []

while True:

    route = client.directions(coords)

    summary = route['routes'][0]['summary']

    record = {
        "timestamp": datetime.now(),
        "distance_m": summary['distance'],
        "duration_s": summary['duration']
    }

    records.append(record)

    df = pd.DataFrame(records)

    df.to_csv("eta_ors_dataset.csv", index=False)

    print(record)

    time.sleep(60)  # 1 phút