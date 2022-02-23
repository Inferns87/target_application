import urllib
import urllib.request
import json


class Core:
    def __init__(self):
        self.endpoint = "https://core.ac.uk:443/api-v2"
        self.api_key = "Vj1xm6loA5nOrTbPZzvwiRChgYNMsfcQ"

    def search(self, query):
        method = "articles/search"

        params = {
            "apiKey": self.api_key,
        }

        api_url = f"{self.endpoint}/{method}/{urllib.parse.quote(query)}?{urllib.parse.urlencode(params)}"

        with urllib.request.urlopen(api_url) as response:
            resp = response.read()
        
        json_result = json.loads(resp.decode('utf-8'))
        print(json_result)


if __name__ == "__main__":
    core = Core()
    core.search("\"medicinal chemistry\" AND (\"stan\" OR \"rstan\" OR \"pystan\" OR \"cmdstan\")")