# Flickr GeoSearch

Uses the Flickr API to execute geotagged photo searches. Results are auto formatted into an excel file and can be uploaded to Flickr photo galleries for review. Also supports the download of photos from Flickr photo galleries.

**Search Criteria:**

    BBOX: Min Lat, Min Long, Max Lat, Max Long
    Radial: Lat, Long, Radius, Units
    Accuracy
    Tags
    Minimum Date Taken
    Maximum Date Taken
    
**Returning Variables**

    Photo ID
    Secret
    Title
    WOE ID
    Long
    Lat
    Accuracy
    Owner Name
    Orignal Format
    Date Upload
    Date Taken
    Time Taken
    Icon Server
    Last Update
    Tags
    Owner Name (optional, slow)
    Owner Country (optional, slow)
  
**Return Options**
    
    XLXS File
    Flickr Photo Album- delimited at 500 photos, not all photos are uploadable to a user's album, time intensive due to API restrictions
  
**Using**

Xlsx Writer, 
PySimpleGUI, 
Python Flickr API Kit
