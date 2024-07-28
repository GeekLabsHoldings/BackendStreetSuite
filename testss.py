import http.client

conn = http.client.HTTPSConnection("api.unusualwhales.com")

headers = {
    'Accept': "application/json, text/plain",
    'Authorization': "Bearer a4c1971d-fbd2-417e-a62d-9b990309a3ce"
}

conn.request("GET", "/api/option-contract/NVDA240726C00055000/flow", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))