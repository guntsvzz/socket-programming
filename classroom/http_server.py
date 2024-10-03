# Import the requests package
import requests

# Pass the API URL to the get function
url = "http://gaia.cs.umass.edu/kurose_ross/interactive/index.php"
response = requests.get(url)

# Print out the text attribute of the response object
print(response.text)
print(response.status_code)