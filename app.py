import requests
import googlemaps
import pandas as pd

#---------- API KEYS, please insert your token/key ---------- #
gmaps = googlemaps.Client(key='')
gmaps_key = ""
ig_token = ""
#------------------------------------------------------------ #

def getPhotosByLoc(lat,lng, access_token): 
    api_req = 'https://api.instagram.com/v1/media/search?lat='+lat+'&lng='+lng+'&access_token='+access_token
    photos = requests.get(url=api_req)
    return photos.json()

def getPhotosByTag(tag, access_token):
    api_req = "https://api.instagram.com/v1/tags/"+tag+"/media/recent?access_token="+access_token
    photos = requests.get(url=api_req)
    return photos.json()

def get_nearby(origin_geoc, dest_geoc, key):
    middle=get_middle_point(origin_geoc, dest_geoc)
    lat = middle[0]
    lng = middle[1]
    endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+lat+","+lng+"&radius=500&type=restaurant|museum|park|art_gallery|church&key="+key
    nearby = requests.get(url=endpoint)
    return nearby.json()

def get_middle_point(origin_geoc, dest_geoc):
    origin_lat = origin_geoc[0]['geometry']['location']['lat']
    origin_lng = origin_geoc[0]['geometry']['location']['lng']
    dest_lat = dest_geoc[0]['geometry']['location']['lat']
    dest_lng = dest_geoc[0]['geometry']['location']['lng']
    lat = str((dest_lat+origin_lat)/2)
    lng = str((dest_lng+origin_lng)/2)
    middle = [lat,lng]
    return middle


def geocode_addrs(address):
    geo = gmaps.geocode(address)
    return geo

def reverse_geo(long, lat):
    reverse_geocode_result = gmaps.reverse_geocode((long, lat))
    return reverse_geocode_result

def create_nearby_df(nearby):
    i=0
    loc_name=[]
    loc_lat=[]
    loc_lng=[]
    loc_type=[]
    while i < len(nearby['results']):  
        loc_name.append(nearby['results'][i]['name'])
        loc_type.append(nearby['results'][i]['types'])
        loc_lat.append(nearby['results'][i]['geometry']['location']['lat'])
        loc_lng.append(nearby['results'][i]['geometry']['location']['lng'])
        i+=1

    poi_collection = pd.DataFrame(
        {'name': loc_name,
         'latitude': loc_lat,
         'longitude': loc_lng,  
         'type': loc_type
        })
    return poi_collection  

def create_ig_df(photo):
    loc_name = []
    loc_lat = [] 
    loc_lng = []
    photo_url = []
    #iterate through the json content from instegram, and add data to the list
    i=0 #create counter
    while i < len(photo['data']):  
        photo_url.append(photo['data'][i]['link'])
        loc_name.append(photo['data'][i]['location']['name'])
        loc_lat.append(photo['data'][i]['location']['latitude'])
        loc_lng.append(photo['data'][i]['location']['longitude'])
        i+=1

    poi_collection = pd.DataFrame(
        {
        'name': loc_name,
        'latitude': loc_lat,
        'longitude': loc_lng, 
        'url': photo_url
        })
    return poi_collection



#----------------- MAIN PROGRAM STARTS HERE ----------------- #

origin = input('Enter origin: ')
dest = input('Enter Destination: ')

#geocode
geocoded_origin = geocode_addrs(origin) 
geocoded_dest = geocode_addrs(dest)

#get nearby
gmaps_nearby=get_nearby(geocoded_origin, geocoded_dest, gmaps_key)
gmaps_df = create_nearby_df(gmaps_nearby)
try:
    gmaps_df.to_csv('gmaps_nearby_list.csv', index=False)
    print("data saved to gmaps_nearby_list.csv")
except:
    print("data can't be saved!")
    raise

# extract the latitude & longitude from geocoded address
lat = str(geocoded_origin[0]['geometry']['location']['lat'])
lng = str(geocoded_dest[0]['geometry']['location']['lng'])
ig_nearby = getPhotosByLoc(lat,lng, ig_token)
ig_df = create_ig_df(ig_nearby)
try:
    ig_df.to_csv('ig_nearby_list.csv', index=False)
    print("data saved to ig_nearby_list.csv")
except:
    print("data can't be saved!")
    raise