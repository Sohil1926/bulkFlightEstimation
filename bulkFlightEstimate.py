import requests
import pandas as pd

api_key = 'apikey'
api_secret = 'apisecret'

auth_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
auth_data = {
    'grant_type': 'client_credentials',
    'client_id': api_key,
    'client_secret': api_secret
}

auth_response = requests.post(auth_url, data=auth_data)
access_token = auth_response.json().get('access_token')
search_url = 'https://test.api.amadeus.com/v2/shopping/flight-offers'

headers = {
    'Authorization': f'Bearer {access_token}'
}

df = pd.read_csv('Flight Estimations - Sohil - Flight Sizing - MIA.csv', skiprows=5)
print(df.columns)

# for index, row in df.iterrows():
#     departing_airport = row['Departing Airport']
#     arrival_airport = row['Arrival Airport']
for index, row in df.head(10).iterrows():
    departing_airport = row['Departing Airport']
    arrival_airport = row['Arrival Airport']
    
    params = {
        'originLocationCode': departing_airport,
        'destinationLocationCode': arrival_airport,
        'departureDate': '2023-12-01', 
        'adults': 1,
        'currencyCode': 'USD'
    }

    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        flight_offers = response.json()
        if 'data' in flight_offers and flight_offers['data']:
            sorted_offers = sorted(flight_offers['data'], key=lambda x: float(x['price']['total']))

            lower_cost_offer = sorted_offers[0]
            lower_cost = lower_cost_offer['price']['total']
            
            higher_cost_offer = sorted_offers[-1]
            higher_cost = higher_cost_offer['price']['total']
            
            df.at[index, 'Lower end of cost'] = float(lower_cost)
            df.at[index, 'Higher end of cost'] = float(higher_cost)

            carrier_code = lower_cost_offer['itineraries'][0]['segments'][0]['carrierCode']
            flight_number = lower_cost_offer['itineraries'][0]['segments'][0]['number']

            df.at[index, 'Carrier Code'] = carrier_code
            df.at[index, 'Flight Number'] = flight_number

            print(f"No flight offers found for {departing_airport} to {arrival_airport}.")
    else:
        print(f"Failed to retrieve flight offers for {departing_airport} to {arrival_airport}. Status Code: {response.status_code}")

df.to_csv('updated_flight_costs.csv', index=False)

print("Access Token:", access_token)
