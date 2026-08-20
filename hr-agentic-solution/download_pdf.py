import urllib.request
url = "https://raw.githubusercontent.com/tanyagoogle/elevate-hr-policy-agent/main/data/handbook.pdf"
urllib.request.urlretrieve(url, "/usr/local/google/home/anujshaunj/hr-agentic-solution/hr-agentic-solution/handbook.pdf")
print("Downloaded successfully")
