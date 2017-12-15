'''
Automatically pulls down weather data from wunderground and saves to csv file(s).
The script has the ability to pull hourly or daily data from any date range.

Examples: get_weather(77007, 'd', '1/1/2014') will pull down the entire month of January on a daily basis
get_weather(77007, 'h', '1/1/2014') will pull down hourly readings for one day.
get_weather will create one csv file called 'weather' unless otherwise specified.

If you need more daily data than a month or more hourly data than a day use the bulk function.
Example: get_bulk_weather(77007, 'h', '1/1/2014', '1/1/2015') will pull hourly data for an entire year.
This will create a csv file for each day.

Per wunderground's api I have limited the bulk request function to 500 requests when pulling hourly data, please be nice :)
'''

import os
import requests
import ujson
from bs4 import BeautifulSoup
from io import StringIO
from pandas import DataFrame
from datetime import datetime
from dateutil import rrule

airport_station = None

#Two helper functions to format dates and find nearest airport to zipcode provided
def format_date(date):
    return datetime.strptime(str(date), '%m/%d/%Y')
    
def min_airport(zipcode):
    zipcode = str(zipcode)
    url = 'http://api.wunderground.com/api/b8e924a8f008b81e/geolookup/q/' + \
    zipcode + '.json'
    r = requests.get(url)
    json = r.json()
    json_encode = ujson.encode(json)
    json_load = ujson.loads(json_encode)
    airports = json_load['location']['nearby_weather_stations']['airport']['station']
    global airport_station
    airport_station = airports[0]['icao']
    return airport_station
    
def get_weather(zipcode, interval, from_date, to_date=None, filename='weather.csv', bulk=0):
    if airport_station is None:
        station = min_airport(zipcode)
    else:
        station = airport_station
    intervals = {'h': 'Daily','d': 'Monthly','c': 'Custom'}
    interval = intervals[interval]
    date = format_date(from_date)
    if to_date is not None:
        format_date(to_date)
    url_begin = 'http://www.wunderground.com/history/airport/'+station+'/'+str(date.year)+'/'+str(date.month)+'/'+str(date.day)+'/'+interval+'History.html?'
    if interval == 'Custom':
        url =  url_begin+'dayend='+str(to_date.day)+'&monthend='+str(to_date.month)+'&yearend='+str(to_date.year)+'&HideSpecis=1'
    else:
        url = url_begin + 'HideSpecis=1'
    
    print('retrieving... ' + url)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser"))
    weather_string = soup.p.get_text()
    weather_stringio = StringIO(weather_string)
    
    if bulk == 1:
        filename = str(date.year)+'-'+str(date.month)+'-'+str(date.day)+'.csv'
    df = DataFrame.from_csv(weather_stringio, sep=',')
    print('found ' + str(len(df) - 1) + ' rows... ', end="")
    if os.path.isfile(filename):
        df.to_csv(filename, mode='a', header=False)
        print('updating ' + filename + '... ', end="")
    else:
        df.to_csv(filename)
        print('creating ' + filename + '... ', end="")
    print('done')

def get_bulk_weather(zipcode, interval, from_dt, to_dt):
    from_date = format_date(from_dt)
    to_date = format_date(to_dt)
    delta = to_date - from_date
    if (interval == 'h') or (interval == 'd' and int(delta.days) > 365):
        if interval == 'h' and int(delta.days) > 500:
            raise Exception('Too many hours, we gotta be nice to the wunderground servers :) (limit to under 500 days).')
        if interval == 'd':
            iteration = rrule.MONTHLY
        else:
            iteration = rrule.DAILY
        for dt in rrule.rrule(iteration, dtstart=from_date, until=to_date):
            curr_date = str(dt.month)+'/'+str(dt.day)+'/'+str(dt.year)
            get_weather(zipcode, interval, curr_date, bulk=1)
    else:
        get_weather(zipcode, 'c', from_dt, to_date=to_dt)