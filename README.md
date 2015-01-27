Automatically pulls down weather data from wunderground and saves to csv file(s).
The script has the ability to pull hourly or daily data from any date range.

Examples: get_weather(77007, 'd', '1/1/2014') will pull down the entire month of January on a daily basis
get_weather(77007, 'h', '1/1/2014') will pull down hourly readings for one day.
get_weather will create one csv file called 'weather' unless otherwise specified.

If you need more daily data than a month or more hourly data than a day use the bulk function.
Example: get_bulk_weather(77007, 'h', '1/1/2014', '1/1/2015') will pull hourly data for an entire year.
This will create a csv file for each day.

Per wunderground's api I have limited the bulk request function to 500 requests when pulling hourly data, please be nice :)