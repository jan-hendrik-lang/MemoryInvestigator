import requests

def get_references_from_malpedia(reference_name):
    """
    Fetches information about a malware family from Malpedia and extracts URLs.

    :param reference_name: The Malpedia reference name (e.g., 'win.parite', or 'win.emotet')
    :return: A list of URLs from the response or an error message
    """
    # Define the API endpoint
    api_url = f"https://malpedia.caad.fkie.fraunhofer.de/api/get/family/{reference_name}"
    headers = {"Accept": "application/json"}

    # Make the request
    response = requests.get(api_url, headers=headers)

    # Check response
    if response.status_code == 200:
        data = response.json()
        return data.get('urls', [])
    else:
        return [f"Error: {response.status_code}, {response.text}"]