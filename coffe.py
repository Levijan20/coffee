import json
import requests
from geopy.distance import geodesic
import folium
from dotenv import load_dotenv
import os


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

    return float(lat), float(lon)


def load_coffee_shops(file_path):
    with open(file_path, 'r', encoding='cp1251') as file:
        data = file.read()
    coffee_shops = json.loads(data)
    return coffee_shops


def main():
    load_dotenv()
    apikey = os.getenv('APIKEY')

    user_location = input("Где вы находитесь? ")

    user_coordinates = fetch_coordinates(apikey, user_location)

    coffee_shops = load_coffee_shops("coffee.json")


    coffee_shops_with_distances = []
    for shop in coffee_shops:
        title = shop.get('Name')
        geo_data = shop.get('geoData', {})
        coordinates = geo_data.get('coordinates', [])

        if len(coordinates) == 2:
            longitude, latitude = coordinates  # Обратите внимание на порядок
            shop_coordinates = (latitude, longitude)  # Переворачиваем порядок
            distance = geodesic(user_coordinates, shop_coordinates).kilometers

            coffee_shops_with_distances.append({
                'title': title,
                'distance': distance,
                'latitude': latitude,
                'longitude': longitude,
            })


    sorted_coffee_shops = sorted(coffee_shops_with_distances, key=lambda x: x['distance'])
    nearest_five_coffee_shops = sorted_coffee_shops[:5]


    for idx, shop in enumerate(nearest_five_coffee_shops, start=1):
        print(f"{idx}. {shop['title']} (расстояние: {shop['distance']:.2f} км)")

    map_center = user_coordinates
    m = folium.Map(location=map_center, zoom_start=15)

    folium.Marker(
        location=map_center,
        popup="Вы здесь",
        icon=folium.Icon(color="blue", icon="user")
    ).add_to(m)


    for shop in nearest_five_coffee_shops:
        folium.Marker(
            location=[shop['latitude'], shop['longitude']],
            popup=f"{shop['title']} ({shop['distance']:.2f} км)",
            icon=folium.Icon(color="green", icon="coffee")
        ).add_to(m)


    m.save("coffee_map.html")


if __name__ == "__main__":
    main()