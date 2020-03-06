# Flickr-API-Services

Uses the Flickr API to execute geotagged photo searches. Results are auto formatted into an excel file and can be uploaded to Flickr photo galleries for review. Also supports the download of photos from Flickr photo galleries.

**Search Criteria:**

    BBOX: Min Lat, Min Long, Max Lat, Max Long
    Radial: Lat, Long, Radius, Units
    Accuracy
    Tags
**Returning Variables**

    Photo ID
    Secret
    Title
    WOE ID
    Long
    Lat
    Accuracy
    Description
    Owner Name
    Orignal Foramt
    Date Upload
    Date Taken
    Time Taken
    Icon Server
    Last Update
    Tags
  
**Return Options**
    
    XLXS File
    Flickr Photo Album (delimited at 500 photos, not all photos are uploadable to a user's album)
  
**Uses**
Xlsx Writer, 
PySimpleGUI, 
Python Flickr API Kit
