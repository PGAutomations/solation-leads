import requests
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to get authentication token
def get_auth_token():
    url = 'https://api-v1.photovoltaik-angebotsvergleich.de/v1/login'
    headers = {'Content-Type': 'application/json'}
    data = {
        "user": "solation-api",
        "pass": "XKqnbV4L3wzBghKtbkoh!v"
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f'Failed to authenticate: {e}')
        return None
    logging.info('Authentication successful')
    return response.json()['auth_token']

# Function to get leads using the authentication token
def get_leads(auth_token):
    url = 'https://api-v1.photovoltaik-angebotsvergleich.de/v1/leads?start=1490520000&stop=1698529875'
    headers = {'X-AUTH-TOKEN': auth_token}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f'Failed to retrieve leads: {e}')
        return None
    logging.info(f'Retrieved {len(response.json()["data"])} leads')
    return response.json()['data']

# Function to add the first lead to Monday.com
def add_leads_to_monday(leads):
    monday_api_url = "https://api.monday.com/v2"
    monday_api_key = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI5MTkxOTMxMCwiYWFpIjoxMSwidWlkIjo0MzAxNDM0OCwiaWFkIjoiMjAyMy0xMC0yNlQwNzoyMDoxMy4xNTdaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTY4MjQ1OTksInJnbiI6ImV1YzEifQ.X6cUk_woFhgLS2cBzyRC2k8l0j4Z35DDwWZ15FgeTOs'
    headers = {
        'Authorization': monday_api_key,
        'Content-Type': 'application/json',
    }
    
    for lead in leads:
        item_name = f"{lead['firstname']} {lead['lastname']}"

          # Manually escape newline characters in the notes field
        notes_escaped = lead['notes'].replace('\n', '\\n')

         # Split the geocode string into latitude and longitude values
        lat, lng = lead['geocode'].split(',')

        address = f"{lead['street']}, {lead['city']}, {lead['zip']}"
    
        # Build the column_values string
        column_values = json.dumps({
            'lead_email': f"{lead['email']} {lead['email']}",
            'lead_phone': lead['phone'],
            'text' : lead['firstname'],
            'text01': lead['lastname'],
            'text2': notes_escaped,
            'location': {  # use your location column's id
            'lat': lat,
            'lng': lng,
            'address': address
        },
            'text7': "Wattfox",
            'zahlen0': lead['leadid'],
            'drop_down0': lead['ph_artdesgebaeude'],
            'dropdown8': lead['ph_neigungderflaeche'],
            'dropdown87': lead['ph_ausrichtungderflaeche'],
            'drop_down9': lead['ph_alterderflaeche'],
            'zahlen1': lead['ph_sonnigeflaeche'],
            'drop_down5': lead['ph_erwerb'],
            'drop_down00': lead['ph_stromspeicher'],
            'zahlen7': lead['stromverbrauch'],
            'zahlen6': lead['lead_product_id'],
            'text89': lead['lead_product_name'],
            'zahlen66': lead['lead_price']
        })


        # Escape double quotes in the column_values string
        column_values_escaped = column_values.replace('"', '\\"')
        # Build the mutation string
        mutation = f'''
        mutation {{
            create_item (
                board_id: 1191566946,
                group_id: "emailed_elemente",
                item_name: "{item_name}",
                column_values: "{column_values_escaped}"
            ) {{
                id
            }}
        }}
    '''
    logging.info(f'Mutation: {mutation}')  # Log the mutation string
    response = requests.post(monday_api_url, headers=headers, json={'query': mutation})
    if response.status_code != 200:
        logging.error(f'Failed to add lead. Status code: {response.status_code}, Response text: {response.text}')
    else:
        try:
            response_json = response.json()
            logging.info(f'Successfully added lead: {response_json}')
        except json.JSONDecodeError:
            logging.error(f'Failed to decode JSON. Response text: {response.text}')
# ...
  
if __name__ == "__main__":
    auth_token = get_auth_token()
    if auth_token:
        leads = get_leads(auth_token)
        if leads and len(leads) > 0:
            add_leads_to_monday([leads[0]])  # Process only the first lead

