import time
import webbrowser
from datetime import datetime
import datetime

import PySimpleGUI as sg
import flickrapi
import xlsxwriter

global API_Key
global Secret_Key

"""""

FLICKR API SERVICES V1.0
Matthew Tralka 2020
GNU General Public License v3.0

The code is a mess. I know. 

"""""


def api_auth_window():
    global flickr
    sg.theme('DarkGrey1')
    layout = [
        [sg.Text('API Key')],
        [sg.InputText(key='-api_key-')],
        [sg.Text('Secret Key')],
        [sg.InputText(key='-secret_key-', password_char='*')],
        [sg.Button('Validate'), sg.Text(size=(15, 1), key='-Valid_Status-')],
        [sg.Text('Token')],
        [sg.InputText(key='-token-'), sg.Text(size=(15, 1), key='-Authentication_Status-')],
        [sg.Button('Authenticate')],
        [sg.Ok(), sg.Cancel()],

    ]

    window = sg.Window('API Authentication Settings', layout)

    while True:
        event, values = window.read()

        api_key = values['-api_key-']
        secret_key = values['-secret_key-']

        if event is None or event == 'Cancel' or event == 'Ok':
            break

        if event == 'Validate':

            # Creates Flickr search object
            flickr = flickrapi.FlickrAPI(api_key, secret_key)

            window['-Valid_Status-'].update('Authenticating..')

            # If, token given is not valid for writing permissions
            # Do, authenticate
            if not flickr.token_valid(perms='write'):

                flickr.get_request_token(oauth_callback='oob')

                # open browser
                authorization_url = flickr.auth_url(perms='write')
                webbrowser.open_new(authorization_url)

                event, values = window.read()

                # If, user clicks 'authenticate'
                if event == 'Authenticate':

                    window['-Authentication_Status-'].update('Authenticating')

                    # 2 factor auth code
                    verifier = values['-token-']

                    flickr.get_access_token(verifier)

                    if flickr.token_valid(perms='write'):
                        window['-Authentication_Status-'].update('Authenticated')

            if flickr.token_valid(perms='write'):
                window['-Valid_Status-'].update('Validated')

                window['-Authentication_Status-'].update('Authenticated')

    window.close()

    return flickr


def about_window():
    sg.theme('DarkGrey1')
    layout = [
        [sg.Multiline(
            default_text="FLICKR API SERVICES V1.0\nCreated by: Matthew Tralka, Mar 5 2020\nSource available on Github: "
                         "mtralka\nLicensed under: GNU General Public License v3.0\n\n\n\nUses the Flickr API to "
                         "execute geotagged photo searches. Results are auto formatted into an excel file and can be "
                         "uploaded to Flickr photo galleries for review. Also supports the download of photos from "
                         "Flickr photo galleries. "
                         "", enter_submits=False, disabled=True, autoscroll=False, enable_events=False,
            do_not_clear=True, size=(50, 30))],

    ]

    window = sg.Window('About', layout)

    while True:
        event, values = window.read()

        if event is None or event == 'Cancel' or event == 'Ok':
            break

    window.close()


def main_view():
    global is_authenticated, flickr, number_pages, prelim_search_results, search_results_on_page, accuracy_column, description_column, gallery_id, owner_name_column, original_format_column, date_upload_column, date_taken_column, wed_column, longitude_column, latitude_column, icon_server_column, tags_column, last_update_column
    is_authenticated = False

    sg.theme('DarkGrey6')

    menu_def = [

        ['File', ['About', 'API Authentication']],

    ]

    layout = [

        [sg.Menu(menu_def)],
        [sg.Text('FLICKR API: PHOTO SEARCH')],

        # Location
        [sg.Radio('Geotagged', "Search", default=True, size=(10, 1), key='-search_geotagged_boolean-')],
        [sg.Text(size=(1, 1)), sg.Frame(layout=[

            [sg.Radio('BBOX', "Search_Type", default=True, key='-bbox_boolean-')],
            [sg.Text(size=(5, 1)), sg.Text('Min Lat:', size=(7, 1)), sg.InputText(size=(5, 1), key='-min_lat-'),
             sg.Text(size=(1, 1)), sg.Text('Max Lat:', size=(7, 1)), sg.InputText(size=(5, 1), key='-max_lat-')],
            [sg.Text(size=(5, 1)), sg.Text('Min Long:', size=(7, 1)), sg.InputText(size=(5, 1), key='-min_long-'),
             sg.Text(size=(1, 1)), sg.Text('Max Long:', size=(7, 1)), sg.InputText(size=(5, 1), key='-max_long-')],
            [sg.Radio('Radial', "Search_Type", default=False, key='-radial_boolean-')],
            [sg.Text(size=(5, 1)), sg.Text('Lat: ', size=(7, 1)), sg.InputText(size=(5, 1), key='-radial_Lat-'),
             sg.Text(size=(1, 1)), sg.Text('Long:', size=(7, 1)), sg.InputText(size=(5, 1), key='-radial_Long-')],
            [sg.Text(size=(5, 1)), sg.Text('Radius:', size=(7, 1)), sg.InputText(size=(5, 1), key='-radial_radius-'),
             sg.Text(size=(1, 1)), sg.Text('Units', size=(7, 1)),
             sg.Drop(values=('mi', 'km'), size=(4, 1), auto_size_text=True, key='-radial_units-')],

            # Accuracy
            [sg.Checkbox('Accuracy: ', default=False, size=(7, 1), key='-accuracy_boolean-'),
             sg.InputText(size=(4, 1), key='-accuracy-'), sg.Text(size=(13, 1), key='-accuracy_description-')],
            [sg.Text(size=(3, 1)),
             sg.Slider((1, 16), key='-slider_accuracy-', orientation='h', enable_events=True,
                       disable_number_display=True)],

            # Search Tags
            [sg.Checkbox('Search tags: ', default=False, size=(9, 1), key='-search_tags_boolean-',
                         tooltip='comma delimited'),
             sg.InputText(size=(23, 0), key='-search_tags-')],

            # User wants results uploaded to favorites
            [sg.Checkbox('Upload to Gallery', default=False, size=(17, 1), key='-upload_to_gallery_boolean-',
                         tooltip='time intensive, expect 10 min per 1k results')],

        ], title='', title_color='red', relief=sg.RELIEF_SUNKEN)],

        # Download Gallery
        [sg.Radio('Download From Gallery', "Search", default=False, key='-gallery_download_boolean-',
                  tooltip='downloads selected gallery of calling user')],
        [sg.Text(size=(1, 1)), sg.Frame(layout=[

            [sg.Text('Gallery ID: ', size=(9, 1)), sg.InputText(size=(20, 1), key='-gallery_id-')],

        ], title='', title_color='red', relief=sg.RELIEF_SUNKEN)],

        # Extras
        [sg.Checkbox('Extras to Return', default=False, size=(15, 1), key='-return_extras_boolean-')],
        [sg.Text(size=(1, 1)), sg.Frame(layout=[

            [sg.Checkbox('Description', key='-return_description_boolean-', size=(9, 1)),
             sg.Checkbox('Owner Name', key='-return_owner_name_boolean-', size=(9, 1)),
             sg.Checkbox('Original Form', key='-return_original_format_boolean-', size=(10, 1))],
            [sg.Checkbox('Date Upload', key='-return_date_upload_boolean-', size=(9, 1)),
             sg.Checkbox('Date Taken', key='-return_date_taken_boolean-', size=(9, 1)),
             sg.Checkbox('Location', key='-return_geo_boolean-', size=(9, 1), tooltip='returns lat / lon')],
            [sg.Checkbox('Icon Server', key='-return_icon_server_boolean-', size=(9, 1)),
             sg.Checkbox('Tags', key='-return_tags_boolean-', size=(9, 1)),
             sg.Checkbox('Last Update', key='-return_last_update_boolean-', size=(9, 1))],
        ], title='', title_color='red', relief=sg.RELIEF_SUNKEN)],

        # File name and location
        [sg.InputText('Output File'), sg.FileSaveAs(key='-file_save_as-')],

        # Search
        [sg.Button('Search')]

    ]

    window = sg.Window("FLICKR API SERVICES", layout)

    global bbox_grid
    bbox_grid = ""
    global radial_Lat
    radial_Lat = ""
    global radial_Long
    radial_Long = ""
    global radial_radius
    radial_radius = ""
    global radial_units1
    radial_units1 = ""
    global accuracy_search
    accuracy_search = ""
    global extras_string
    extras_string = ""
    global tags1
    tags1 = ""
    global accuracy1
    accuracy1 = ""
    global has_geo1
    has_geo1 = 0
    global gallery_title
    gallery_title = ''

    while True:

        event, values = window.read()

        if event is None or event == 'Exit':
            break

        # If, user clicks 'API Authentication'
        # Do, goto method
        # Return, flickr control object
        if event == 'API Authentication':

            flickr = api_auth_window()

            if flickr.token_valid(perms='write'):
                is_authenticated = True
        if event == 'About':
            about_window()

        # Accuracy updater for slider
        window['-accuracy-'].update(values['-slider_accuracy-'])
        if int(values['-slider_accuracy-']) == 1:
            window['-accuracy_description-'].update('World')
        if int(values['-slider_accuracy-']) == 2:
            window['-accuracy_description-'].update('World+')
        if int(values['-slider_accuracy-']) == 3:
            window['-accuracy_description-'].update('Country')
        if int(values['-slider_accuracy-']) == 4:
            window['-accuracy_description-'].update('Country+')
        if int(values['-slider_accuracy-']) == 5:
            window['-accuracy_description-'].update('Country++')
        if int(values['-slider_accuracy-']) == 6:
            window['-accuracy_description-'].update('Region')
        if int(values['-slider_accuracy-']) == 7:
            window['-accuracy_description-'].update('Region+')
        if int(values['-slider_accuracy-']) == 8:
            window['-accuracy_description-'].update('Region++')
        if int(values['-slider_accuracy-']) == 9:
            window['-accuracy_description-'].update('Region+++')
        if int(values['-slider_accuracy-']) == 10:
            window['-accuracy_description-'].update('Region++++')
        if int(values['-slider_accuracy-']) == 11:
            window['-accuracy_description-'].update('City')
        if int(values['-slider_accuracy-']) == 12:
            window['-accuracy_description-'].update('City+')
        if int(values['-slider_accuracy-']) == 13:
            window['-accuracy_description-'].update('City++')
        if int(values['-slider_accuracy-']) == 14:
            window['-accuracy_description-'].update('City+++')
        if int(values['-slider_accuracy-']) == 15:
            window['-accuracy_description-'].update('City++++')
        if int(values['-slider_accuracy-']) == 16:
            window['-accuracy_description-'].update('Street')

        if event == 'Search' and is_authenticated == False:
            sg.popup("Authentication Needed", title="Error", background_color='red', no_titlebar=True)

        # If, 'Search' and flickr object is authenticated
        # Do, execute search
        if event == 'Search' and is_authenticated:
            sg.popup("Search Confirmed: Please Wait", title="OK", background_color='green', no_titlebar=True,
                     keep_on_top=True, auto_close=True)
            window.close()
            return values


values = main_view()

global id_list
id_list = ['0000000']

# Determines starting column data is written to in excel
starting_column = 4

if bool(values['-search_geotagged_boolean-']) or bool(values['-gallery_download_boolean-']):

    wed_column = starting_column
    starting_column += 1

    has_geo1 = "1"

    if bool(values['-bbox_boolean-']):
        min_long = values['-min_long-']
        min_lat = values['-min_lat-']
        max_long = values['-max_long-']
        max_lat = values['-max_lat-']
        comma = ','

        bbox_grid = min_long + comma + min_lat + comma + max_long + comma + max_lat

        longitude_column = starting_column
        starting_column += 1
        latitude_column = starting_column
        starting_column += 1

    if bool(values['-radial_boolean-']):
        radial_Lat = values['-radial_Lat-']
        radial_Long = values['-radial_Long-']
        radial_radius = values['-radial_radius-']
        radial_units1 = values['-radial_units-']

        longitude_column = starting_column
        starting_column += 1
        latitude_column = starting_column
        starting_column += 1

# User wants accuracy
if bool(values['-accuracy_boolean-']) or bool(values['-gallery_download_boolean-']):
    accuracy_search = values['-accuracy-']

    accuracy_column = starting_column
    starting_column += 1

# User wants extras
if bool(values['-return_extras_boolean-']):

    if bool(values['-return_description_boolean-']):
        description_column = starting_column
        starting_column += 1

    if bool(values['-return_owner_name_boolean-']):
        owner_name_column = starting_column
        starting_column += 1

    if bool(values['-return_original_format_boolean-']):
        original_format_column = starting_column
        starting_column += 1

    if bool(values['-return_date_upload_boolean-']):
        date_upload_column = starting_column
        starting_column += 1

    if bool(values['-return_date_taken_boolean-']):
        date_taken_column = starting_column
        starting_column += 1
        date_taken_time_column = starting_column
        starting_column += 1

    if bool(values['-return_icon_server_boolean-']):
        icon_server_column = starting_column
        starting_column += 1

    if bool(values['-return_last_update_boolean-']):
        last_update_column = starting_column
        starting_column += 1

    if bool(values['-return_tags_boolean-']):
        tags_column = starting_column
        starting_column += 1

# User wants tag search
if bool(values['-search_tags_boolean-']):
    tags1 = values['-search_tags-']

extras_string = "description, license, date_upload, date_taken, owner_name, icon_server, original_format, " \
                "last_update, geo, tags "

number_pages = ''
number_photos = ''
per_page_photo = ''
target_gallery_id = ''

# preliminary search to find number of pages/photos/results
if bool(values['-search_geotagged_boolean-']):
    if bool(values['-bbox_boolean-']):
        prelim_search_results = flickr.photos_search(bbox=bbox_grid, lat=radial_Lat, lon=radial_Long,
                                                     has_geo='1', radius=radial_radius,
                                                     radius_units=radial_units1, tags=tags1,
                                                     accuracy=accuracy_search, extras=extras_string
                                                     )
    if bool(values['-radial_boolean-']):
        prelim_search_results = flickr.photos_search(lat=radial_Lat, lon=radial_Long, has_geo='1',
                                                     radius=radial_radius, radius_units=radial_units1,
                                                     tags=tags1, accuracy=accuracy_search,
                                                     extras=extras_string)
else:
    prelim_search_results = flickr.galleries.getPhotos(gallery_id=values['-gallery_id-'], extras=extras_string)

number_pages = int(prelim_search_results.find('photos').attrib['pages'])
number_photos = int(prelim_search_results.find('photos').attrib['total'])
per_page_photo = int(prelim_search_results.find('photos').attrib['perpage'])

starting_page = 1

# File name setter
file_name = values["-file_save_as-"]

if file_name[-4] != 'xlsx':
    file_name += '.xlsx'

workbook = xlsxwriter.Workbook(file_name)
worksheet0 = workbook.add_worksheet()
worksheet = workbook.add_worksheet()

# TODO Fix this
format_date_time = workbook.add_format({'num_format': 'dd/mm/yy hh:mm'})
format_date = workbook.add_format({'num_format': 'dd/mm/yy'})

photo_starting_row = 1
photo_counter = 1

worksheet0.write_string(0, 0, 'Flickr API Services')
worksheet0.write_string(1, 0, "By: Matthew Tralka")

worksheet0.write_string(4, 0, '# Photos: ')
worksheet0.write_number(4, 1, number_photos)
worksheet0.write(5, 0, "Per Page")
worksheet0.write(5, 1, per_page_photo)
worksheet0.write(6, 0, "Pages")
worksheet0.write(6, 1, number_pages)

if bool(values['-search_geotagged_boolean-']):
    worksheet0.write(8, 0, "Accuracy")
    worksheet0.write(8, 1, accuracy_search)

    if bool(values['-bbox_boolean-']):
        worksheet0.write_string(7, 0, "BBOX Search")
        worksheet0.write(9, 0, "Grid")
        worksheet0.write(9, 1, bbox_grid)

    if bool(values['-radial_boolean-']):
        worksheet0.write_string(7, 0, "Radial Search")
        worksheet0.write(9, 0, "Lat")
        worksheet0.write(9, 1, radial_Lat)
        worksheet0.write(10, 0, "Long")
        worksheet0.write(10, 1, radial_Long)
        worksheet0.write(11, 0, "Radius")
        worksheet0.write(11, 1, radial_radius)
        worksheet0.write(12, 0, "Units")
        worksheet0.write(12, 1, radial_units1)

if bool(values['-gallery_download_boolean-']):
    worksheet0.write_string(7, 0, "Downloaded Favorites")
    worksheet0.write(8, 0, "Gallery ID: " + values['-gallery_id-'])

worksheet.write_string(0, 0, "Photo Number")
worksheet.write_string(0, 1, "Photo ID")
worksheet.write_string(0, 2, "Secret")
worksheet.write_string(0, 3, "Title")

# Iterate through all pages
for page_x in range(int(starting_page), number_pages + 1):

    # Generates new search for next page
    if bool(values['-search_geotagged_boolean-']):
        if bool(values['-bbox_boolean-']):
            search_results_on_page = flickr.photos_search(bbox=bbox_grid, lat=radial_Lat, lon=radial_Long,
                                                          has_geo='1', radius=radial_radius,
                                                          radius_units=radial_units1, tags=tags1,
                                                          accuracy=accuracy_search, extras=extras_string,
                                                          per_page=per_page_photo, page=page_x)
        if bool(values['-radial_boolean-']):
            search_results_on_page = flickr.photos_search(lat=radial_Lat, lon=radial_Long, has_geo='1',
                                                          radius=radial_radius, radius_units=radial_units1,
                                                          tags=tags1, accuracy=accuracy_search,
                                                          extras=extras_string, per_page=per_page_photo,
                                                          page=page_x)
    else:
        if bool(values['-gallery_download_boolean-']):
            search_results_on_page = flickr.galleries.getPhotos(gallery_id=values['-gallery_id-'], extras=extras_string,
                                                                per_page=per_page_photo, page=page_x)

    # Iterate through photos on page
    for photo_y in range(0, per_page_photo):
        if photo_counter <= number_photos:

            # Parses results on page
            results_on_page = search_results_on_page.find('photos').findall('photo')[photo_y]

            # Determines keys (information present)
            keys = results_on_page.keys()

            # Write Photo Number
            worksheet.write(photo_starting_row, 0, photo_counter)

            # Write Photo ID
            worksheet.write(photo_starting_row, 1, results_on_page.attrib['id'])

            # Write Secret
            worksheet.write_string(photo_starting_row, 2, results_on_page.attrib['secret'])

            # add to gallery list
            if bool(values['-upload_to_gallery_boolean-']):
                id_list.append(int(results_on_page.attrib['id']))

            # Write Title
            worksheet.write_string(photo_starting_row, 3, results_on_page.attrib['title'])

            if 'accuracy' in keys and bool(values['-accuracy_boolean-']) or bool(values['-gallery_download_boolean-']):
                worksheet.write_string(0, accuracy_column, 'Accuracy')
                worksheet.write(photo_starting_row, accuracy_column, results_on_page.attrib['accuracy'])

            if bool(values['-return_extras_boolean-']):

                if bool(values['-return_description_boolean-']):
                    if 'description' in keys:
                        worksheet.write_string(0, description_column, 'Description')
                        worksheet.write(photo_starting_row, description_column,
                                        results_on_page.attrib['description'])
                    else:
                        worksheet.write_string(0, description_column, 'Description')

                if bool(values['-return_owner_name_boolean-']):
                    if 'owner' in keys:
                        worksheet.write_string(0, owner_name_column, 'Owner Name')
                        worksheet.write(photo_starting_row, owner_name_column, results_on_page.attrib['owner'])

                if bool(values['-return_original_format_boolean-']):
                    if 'originalformat' in keys:
                        worksheet.write(0, original_format_column, 'Original Format')
                        worksheet.write(photo_starting_row, original_format_column,
                                        results_on_page.attrib['originalformat'])

                if bool(values['-return_date_upload_boolean-']):
                    if 'dateupload' in keys:
                        modified_date_upload = datetime.datetime.utcfromtimestamp(float(
                            results_on_page.attrib['dateupload'])).strftime('%Y-%m-%d')

                        worksheet.write(0, date_upload_column, 'Date Upload')
                        worksheet.write(photo_starting_row, date_upload_column, modified_date_upload, format_date)

                if bool(values['-return_date_taken_boolean-']):
                    if 'datetaken' in keys:
                        modified_date_taken = str(results_on_page.attrib['datetaken']).split()
                        modified_date_taken_date = modified_date_taken[0]
                        modified_date_taken_time = modified_date_taken[1]
                        worksheet.write_string(0, date_taken_column, 'Date Taken')
                        worksheet.write_string(0, date_taken_time_column, "Time Taken")

                        worksheet.write(photo_starting_row, date_taken_column, modified_date_taken_date, format_date)
                        worksheet.write(photo_starting_row, date_taken_time_column, modified_date_taken_time)

                if bool(values['-return_geo_boolean-']):
                    if 'woeid' in keys:
                        worksheet.write_string(0, wed_column, 'WOE ID')
                        worksheet.write(photo_starting_row, wed_column, results_on_page.attrib['woeid'])

                    if 'longitude' in keys:
                        worksheet.write_string(0, longitude_column, 'Longitude')
                        worksheet.write(photo_starting_row, longitude_column,
                                        results_on_page.attrib['longitude'])

                    if 'latitude' in keys:
                        worksheet.write_string(0, latitude_column, 'Latitude')
                        worksheet.write(photo_starting_row, latitude_column, results_on_page.attrib['latitude'])

                if bool(values['-return_icon_server_boolean-']):
                    if 'iconserver' in keys:
                        worksheet.write_string(0, icon_server_column, 'Icon Server')
                        worksheet.write(photo_starting_row, icon_server_column,
                                        results_on_page.attrib['iconserver'])

                if bool(values['-return_tags_boolean-']):
                    if 'tags' in keys:
                        worksheet.write_string(0, tags_column, 'Tags')
                        worksheet.write(photo_starting_row, tags_column, results_on_page.attrib['tags'])

                if bool(values['-return_last_update_boolean-']):
                    if 'lastupdate' in keys:
                        modified_last_update = datetime.datetime.utcfromtimestamp(
                            float(results_on_page.attrib['lastupdate'])).strftime('%Y-%m-%d')

                        worksheet.write_string(0, last_update_column, 'Last Update')
                        worksheet.write(photo_starting_row, last_update_column, modified_last_update, format_date)

            photo_counter += 1
            photo_starting_row += 1

workbook.close()

# User wants gallery upload
if bool(values['-upload_to_gallery_boolean-']):

    gallery_part = 1
    gallery_photo_count = 1

    while gallery_photo_count <= len(id_list):

        photo_in_gallery = 0

        now = datetime.datetime.now()
        gallery_title = "Search: " + str(now.strftime('%Y-%m-%d')) + " Pt. " + str(gallery_part)
        gallery_description = "Created by FLICKR API SERVICES \n\n By: Matthew Tralka \n\n Executed: " + str(
            now.strftime('%Y-%m-%d %H:%M:%S') + "\n\nFind Gallery ID in URL")
        gallery_part += 1

        gallery_return = flickr.galleries.create(title=gallery_title, description=gallery_description)
        gallery_return_id = gallery_return.find('gallery').attrib['id']

        # Flickr has a 500 photo per gallery limit
        while photo_in_gallery < 500 and gallery_photo_count <= len(id_list):

            gallery_photo_count += 1

            # Some photos can not be added to a users gallery
            try:
                flickr.galleries.addPhoto(gallery_id=gallery_return_id, photo_id=id_list[gallery_photo_count],
                                          comment=gallery_photo_count)

                photo_in_gallery += 1

            except:
                continue
