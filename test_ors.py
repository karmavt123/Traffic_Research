import openrouteservice

API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImQwYmQ5NWY5ODg3MjQ3Y2NhYmU5ZmE0MzIyM2ZmNmY5IiwiaCI6Im11cm11cjY0In0="

client = openrouteservice.Client(key=API_KEY)

coords = (
    (106.660172, 10.762622),  # origin
    (106.700806, 10.776889)   # destination
)

route = client.directions(coords)

summary = route['routes'][0]['summary']

distance = summary['distance']
duration = summary['duration']

print("Distance (m):", distance)
print("Duration (s):", duration)
print("Duration (min):", duration / 60)