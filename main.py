import threading
from datetime import date
import webbrowser
import PySimpleGUI as sg
import flickrapi
import xlsxwriter
import datetime
import queue

"""""

FLICKR GeoSearch V3.0
Matthew Tralka 2020
GNU General Public License v3.0

"""""


class flickrSearchParameters:
    extras = "description, license, date_upload, date_taken, owner_name, icon_server, original_format, " \
             "last_update, geo, tags, url_sq"

    month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
                  'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12', '': None}

    def __init__(self, values):
        self.gallery_download = values['-gallery_download_boolean-']
        self.bbox_boolean = values['-bbox_boolean-']
        self.min_long = values['-min_long-']
        self.min_lat = values['-min_lat-']
        self.max_long = values['-max_long-']
        self.max_lat = values['-max_lat-']
        self.radial = values['-radial_boolean-']
        self.radial_long = values['-radial_long-']
        self.radial_lat = values['-radial_lat-']
        self.radial_radius = values['-radial_radius-']
        self.radial_units = values['-radial_units-']
        self.accuracy = values['-accuracy-']
        self.file_name = values['-file_save_as-']
        self.gallery_id = values['-gallery_id-']
        self.search_tags = values['-search_tags-']
        self.accuracy_boolean = values['-accuracy_boolean-']
        self.min_date_boolean = values['-min_date_boolean-']
        self.min_month = self.month_dict[values['-min_month-']]
        self.min_date = values['-min_date-']
        self.min_year = values['-min_year-']
        self.max_date_boolean = values['-max_date_boolean-']
        self.max_month = self.month_dict[values['-max_month-']]
        self.max_date = values['-max_date-']
        self.max_year = values['-max_year-']
        self.gallery_upload_boolean = values['-upload_to_gallery_boolean-']
        self.user_info_boolean = values['-user_info_boolean-']
        self.bbox_grid = '{},{},{},{}'.format(self.min_long, self.min_lat, self.max_long, self.max_lat)

    def __del__(self):
        # For good measure
        self.gallery_download = False
        self.max_date_boolean = False
        self.min_date_boolean = False
        self.accuracy_boolean = False
        self.bbox_boolean = False
        self.radial = False

    def get_BBOX_grid(self):
        if self.bbox_boolean:
            return self.bbox_grid

    def get_gallery_download(self):
        return self.gallery_download

    def get_bbox_boolean(self):
        return self.bbox_boolean

    def get_min_long(self):
        return self.min_long

    def get_min_lat(self):
        return self.min_lat

    def get_max_lat(self):
        return self.max_lat

    def get_max_long(self):
        return self.max_long

    def get_radial(self):
        return self.radial

    def get_radial_long(self):
        return self.radial_long

    def get_radial_lat(self):
        return self.radial_lat

    def get_radial_radius(self):
        return self.radial_radius

    def get_radial_units(self):
        return self.radial_units

    def get_accuracy(self):
        return self.accuracy

    def get_search_tags(self):
        return self.search_tags

    def get_file_name(self):
        return self.file_name

    def get_gallery_id(self):
        return self.gallery_id

    def get_accuracy_boolean(self):
        return self.accuracy_boolean

    def get_min_date_boolean(self):
        return self.min_date_boolean

    def get_min_month(self):
        return self.min_month

    def get_min_day(self):
        return self.min_date

    def get_min_year(self):
        return self.min_year

    def get_max_date_boolean(self):
        return self.max_date_boolean

    def get_max_month(self):
        return self.max_month

    def get_max_day(self):
        return self.max_date

    def get_max_year(self):
        return self.max_year

    def get_min_date_joined(self):
        min_complete = '-'.join((str(self.min_year), str(self.min_month), self.min_date))
        return min_complete

    def get_max_date_joined(self):
        max_complete = '-'.join((self.max_year, str(self.max_month), self.max_date))
        return max_complete

    # Optional: can search with UNIX datetime instead of SQL datetime
    # def get_min_date_unix(self):
    # dt = datetime.datetime(int(self.min_year), int(self.min_month), int(self.min_date)).timestamp()
    # return str(math.trunc(dt))

    # def get_max_date_unix(self):
    # dt = datetime.datetime(int(self.max_year), int(self.max_month), int(self.max_date)).timestamp()
    # return str(math.trunc(dt))

    def get_gallery_upload(self):
        return self.gallery_upload_boolean

    def get_user_info(self):
        return self.user_info_boolean


def long_operation_thread(flickr, search):
    """"" 
    :param flickr: (obk) flickr auth search object
    :param search: (obj) user defined search parameters
    """""

    file_name = search.get_file_name()

    if file_name[-4] != 'xlsx':
        file_name += '.xlsx'

    workbook = xlsxwriter.Workbook(file_name)
    worksheet0 = workbook.add_worksheet()
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})

    worksheet0.write_string(0, 0, 'FLICKR GeoSearch', bold)
    worksheet0.write_string(1, 0, "Matthew Tralka")

    worksheet0.write(8, 0, "Accuracy")
    worksheet0.write_string(8, 1, search.get_accuracy())

    if search.get_bbox_boolean():
        worksheet0.write_string(7, 0, "BBOX Search")
        worksheet0.write(9, 0, "Grid")
        worksheet0.write(9, 1, search.get_BBOX_grid())

    if search.get_radial():
        worksheet0.write_string(7, 0, "Radial Search")
        worksheet0.write(9, 0, "Lat")
        worksheet0.write_string(9, 1, search.get_radial_lat())
        worksheet0.write(10, 0, "Long")
        worksheet0.write_string(10, 1, search.get_radial_long())
        worksheet0.write(11, 0, "Radius")
        worksheet0.write_string(11, 1, search.get_radial_radius())
        worksheet0.write(12, 0, "Units")
        worksheet0.write(12, 1, search.get_radial_units())

    if search.get_min_date_boolean():
        worksheet0.write_string(13, 0, 'Min Date Taken')
        worksheet0.write_string(13, 1, search.get_min_date_joined())

    if search.get_max_date_boolean():
        worksheet0.write_string(14, 0, 'Max Date Taken')
        worksheet0.write_string(14, 1, search.get_max_date_joined())

    if search.get_search_tags():
        worksheet0.write_string(15, 0, "Search Tags: ")
        worksheet0.write_string(15, 1, search.get_search_tags())

    if search.get_gallery_download():
        worksheet0.write_string(7, 0, "Downloaded Favorites")
        worksheet0.write(8, 0, "Gallery ID: " + search.get_gallery_id())
        worksheet0.write(9, 1, '')
        worksheet0.write(10, 0, "")
        worksheet0.write(10, 1, "")
        worksheet0.write(11, 0, "")
        worksheet0.write(11, 1, "")
        worksheet0.write(12, 0, "")
        worksheet0.write(12, 1, "")

    # search can not handle null min_date values, program defaults to Flickr creation year
    if not search.get_min_date_boolean():
        min_date = "2004-01-01"
        print(min_date)

    else:
        min_date = search.get_min_date_joined()
        print(min_date)

    if not search.get_max_date_boolean():
        max_date = date.today().strftime("%Y-%m-%d")
        print(max_date)

    else:
        max_date = search.get_max_date_joined()
        print(max_date)

    photo_counter = 1
    photo_starting_row = 1
    gallery_part = 1
    gallery_count = 1
    gallery_valid = False
    id_list = [0000000]

    """""""""
    Excel Variables
    """""""""

    header_row = 0
    photo_number_column = 0
    photo_ID_column = 1
    secret_column = 2
    title_column = 3
    WOE_ID_column = 4
    longitude_column = 5
    latitude_column = 6
    accuracy_column = 7
    owner_name_column = 8
    original_format_column = 9
    date_upload_column = 10
    date_taken_column = 11
    time_taken_column = 12
    icon_server_column = 13
    last_update_column = 14
    link_column = 15
    tags_column = 16
    owner_real_name_column = 17
    owner_hometown_column = 18
    worksheet.set_column('A:T', 13)
    worksheet.set_column('R:R', 17)

    def write_string_header(row, column, string):
        worksheet.write_string(row, column, string, bold)

    if search.get_user_info():
        tags_column = 18
        owner_real_name_column = 16
        owner_hometown_column = 17
        write_string_header(header_row, owner_real_name_column, "Owner Real Name")
        write_string_header(header_row, owner_hometown_column, "Owner Hometown")

    write_string_header(header_row, photo_number_column, 'Photo Number')
    write_string_header(header_row, photo_ID_column, "Photo ID")
    write_string_header(header_row, secret_column, "Secret")
    write_string_header(header_row, title_column, "Title")
    write_string_header(header_row, WOE_ID_column, "WOE ID")
    write_string_header(header_row, longitude_column, "Longitude")
    write_string_header(header_row, latitude_column, "Latitude")
    write_string_header(header_row, accuracy_column, "Accuracy")
    write_string_header(header_row, owner_name_column, "Owner Name")
    write_string_header(header_row, original_format_column, "Original Format")
    write_string_header(header_row, date_upload_column, "Date Uploaded")
    write_string_header(header_row, date_taken_column, "Date Taken")
    write_string_header(header_row, time_taken_column, "Time Taken")
    write_string_header(header_row, icon_server_column, "Icon Server")
    write_string_header(header_row, last_update_column, "Last Update")
    write_string_header(header_row, link_column, "Link")
    write_string_header(header_row, tags_column, "Tags")

    # TODO Gallery Download
    """""""""""""""""""""
    search_results_on_page = flickr.galleries.getPhotos(gallery_id=values['-gallery_id-'], extras=extras_string,
                                                                per_page=per_page_photo, page=page_x

    '""""""""""""""""""'"""

    for photo in flickr.walk(bbox=search.get_BBOX_grid(), lat=search.get_radial_lat(),
                             lon=search.get_radial_long(), has_geo='1',
                             radius=search.get_radial_radius(),
                             radius_units=search.get_radial_units(),
                             tags=search.get_search_tags(),
                             accuracy=search.get_accuracy(), extras=search.extras,
                             min_taken_date=min_date, max_taken_date=max_date):

        # Photo Number
        worksheet.write(photo_starting_row, photo_number_column, photo_counter)

        # Write Photo ID
        worksheet.write_number(photo_starting_row, photo_ID_column, int(photo.get('id')))
        print(photo.get('id'))

        if search.get_gallery_upload():
            id_list.append(int(photo.get('id')))

        # Write Secret
        worksheet.write_string(photo_starting_row, secret_column, photo.get('secret'))

        # Write Title
        worksheet.write_string(photo_starting_row, title_column, photo.get('title'))

        # Write WOE ID
        try:
            worksheet.write_number(photo_starting_row, WOE_ID_column, int(photo.get('woeid')))
        except:
            print("Null Object")

        # Write Longitude
        try:
            worksheet.write_number(photo_starting_row, longitude_column, float(photo.get('longitude')))
        except:
            print("Null Object")

        # Write Latitude
        try:
            worksheet.write_number(photo_starting_row, latitude_column, float(photo.get('latitude')))
        except:
            print("Null Object")

        # Write Accuracy
        try:
            worksheet.write_string(photo_starting_row, accuracy_column, photo.get('accuracy'))
        except:
            print("Null Object")

        # Write Owner Name
        try:
            worksheet.write_string(photo_starting_row, owner_name_column, photo.get('owner'))
        except:
            print("Null Object")

        # Write Original Format
        try:
            worksheet.write_string(photo_starting_row, original_format_column, photo.get('originalformat'))
        except:
            print("Null Object")

        # Write Date Upload
        try:
            worksheet.write_string(photo_starting_row, date_upload_column, datetime.datetime.utcfromtimestamp(float(
                photo.get('dateupload'))).strftime('%Y-%m-%d'))
        except:
            print("Null Object")

        # Write Date / Time Taken
        try:
            modified_date_taken = str(photo.get('datetaken')).split()
            worksheet.write_string(photo_starting_row, date_taken_column, modified_date_taken[0])
            worksheet.write_string(photo_starting_row, time_taken_column, modified_date_taken[1])
        except:
            print("Null Object")

        # Write Icon Server
        try:
            worksheet.write_number(photo_starting_row, icon_server_column, int(photo.get('iconserver')))
        except:
            print("Null Object")

        # Write Last Update
        try:
            worksheet.write_string(photo_starting_row, last_update_column, datetime.datetime.utcfromtimestamp(
                float(photo.get('lastupdate'))).strftime('%Y-%m-%d'))
        except:
            print("Null Object")

        # Write link
        try:
            url = 'https://www.flickr.com/photos/' + photo.get('owner') + '/' + photo.get('id')
            worksheet.write_string(photo_starting_row, link_column, url)
        except:
            print("Null Object")

        # Write Tags

        try:
            worksheet.write_string(photo_starting_row, tags_column, photo.get('tags'))
        except:
            print("Null Object")

        # Write Owner Home Town and Real Name
        if search.get_user_info():

            try:
                raw_response = flickr.photos.getInfo(photo_id=photo.get('id'), secret=photo.get('secret'))
                response = raw_response.find('photo').find('owner')
                worksheet.write_string(photo_starting_row, owner_real_name_column, response.attrib['realname'])
                worksheet.write_string(photo_starting_row, owner_hometown_column, response.attrib['location'])
            except:
                print("Failed Response")

        photo_counter += 1
        photo_starting_row += 1

    worksheet0.write_string(4, 0, '# Photos: ')
    worksheet0.write_number(4, 1, int(photo_counter - 1))

    workbook.close()

    # Uploader
    if search.get_gallery_upload():

        i = 0
        while i < len(id_list):

            if gallery_count > 500:
                gallery_valid = False
                gallery_part += 1
                gallery_count = 1

            if not gallery_valid:
                timestamp = datetime.datetime.now()
                gallery_title = "Search: " + str(timestamp.strftime('%Y-%m-%d')) + " Pt. " + str(gallery_part)
                gallery_description = "Created by FLICKR GeoSearch \n\n By: Matthew Tralka \n\n Executed: " + str(
                    timestamp.strftime('%Y-%m-%d %H:%M:%S') + "\n\nFind Gallery ID in URL")

                new_gallery = flickr.galleries.create(title=gallery_title, description=gallery_description)
                new_gallery_id = new_gallery.find('gallery').attrib['id']

                gallery_valid = True

            try:
                flickr.galleries.addPhoto(gallery_id=new_gallery_id, photo_id=id_list[i],
                                          comment=photo_counter)
                gallery_count += 1
            except:
                print('Unable to add to Gallery')

            i += 1

    del search
    sg.popup_animated(None)
    thread = None


def the_GUI():
    program_theme = 'DarkGrey5'
    is_authenticated = False
    gui_queue = queue.Queue()
    auth_window_active, about_window_active, console_window_active = False, False, False

    sg.theme(program_theme)

    menu_def = [

        ['File', ['About', 'API Authentication']],

    ]

    main_layout = [

        [sg.Menu(menu_def)],
        [sg.Text('FLICKR GeoSearch')],

        # Search
        [sg.Radio('BBOX', "Search_Type", default=True, key='-bbox_boolean-')],
        [sg.Text(size=(5, 1)), sg.Text('Min Lat:', size=(7, 1), tooltip='-90 - 90'),
         sg.InputText(size=(5, 1), key='-min_lat-'),
         sg.Text(size=(1, 1)), sg.Text('Max Lat:', size=(7, 1), tooltip='-90 - 90'),
         sg.InputText(size=(5, 1), key='-max_lat-')],
        [sg.Text(size=(5, 1)), sg.Text('Min Long:', size=(7, 1), tooltip='-180 - 180'),
         sg.InputText(size=(5, 1), key='-min_long-'),
         sg.Text(size=(1, 1)), sg.Text('Max Long:', size=(7, 1), tooltip='-180 - 180'),
         sg.InputText(size=(5, 1), key='-max_long-')],
        [sg.Radio('Radial', "Search_Type", default=False, key='-radial_boolean-')],
        [sg.Text(size=(5, 1)), sg.Text('Lat: ', size=(7, 1), tooltip='-90 - 90'),
         sg.InputText(size=(5, 1), key='-radial_lat-'),
         sg.Text(size=(1, 1)), sg.Text('Long:', size=(7, 1), tooltip='-180 - 180'),
         sg.InputText(size=(5, 1), key='-radial_long-')],
        [sg.Text(size=(5, 1)), sg.Text('Radius:', size=(7, 1), tooltip='max 20mi / 32km'),
         sg.InputText(size=(5, 1), key='-radial_radius-'),
         sg.Text(size=(1, 1)), sg.Text('Units', size=(7, 1)),
         sg.Drop(values=('mi', 'km'), size=(4, 1), auto_size_text=True, key='-radial_units-')],

        # Accuracy
        [sg.Checkbox('Accuracy: ', default=False, size=(7, 1), key='-accuracy_boolean-'),
         sg.InputText(size=(4, 1), key='-accuracy-'), sg.Text(size=(13, 1), key='-accuracy_description-')],
        [sg.Text(size=(3, 1)),
         sg.Slider((1, 16), key='-slider_accuracy-', orientation='h', enable_events=True,
                   disable_number_display=True)],

        # Min Date Taken Upload
        [sg.Checkbox('Minimum Date Taken: ', default=False, size=(17, 1), key='-min_date_boolean-')],
        [sg.Text(size=(3, 1)),
         sg.Drop(values=('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
                 size=(3, 1),
                 auto_size_text=True, key='-min_month-', tooltip='month, 3 letter abbreviation'),
         sg.Text('-', size=(1, 1)),
         sg.Drop(values=('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
                         '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'),
                 size=(2, 1), tooltip='day, max 2 digit', key='-min_date-'), sg.Text('-', size=(1, 1)),
         sg.InputText(size=(4, 1), tooltip='Year, 4 number', key='-min_year-')],

        # Max Date Taken Upload
        [sg.Checkbox('Maximum Date Taken: ', default=False, size=(17, 1), key='-max_date_boolean-')],
        [sg.Text(size=(3, 1)),
         sg.Drop(values=('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
                 size=(3, 1),
                 auto_size_text=True, key='-max_month-', tooltip='month, 3 letter abbreviation'),
         sg.Text('-', size=(1, 1)),
         sg.Drop(values=('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
                         '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'),
                 size=(2, 1), tooltip='day, max 2 digit', key='-max_date-'), sg.Text('-', size=(1, 1)),
         sg.InputText(size=(4, 1), tooltip='Year, 4 number', key='-max_year-')],

        # Search Tags
        [sg.Checkbox('Search tags: ', default=False, size=(9, 1), key='-search_tags_boolean-',
                     tooltip='comma delimited'),
         sg.InputText(size=(23, 0), key='-search_tags-')],

        # User wants results uploaded to gallery
        [sg.Checkbox('Upload to Gallery', default=False, size=(17, 1), key='-upload_to_gallery_boolean-',
                     tooltip='time intensive, 3 minutes per 500 results')],

        # User wants results on Owner Info
        [sg.Checkbox('Get Owner Info', default=False, size=(17, 1), key='-user_info_boolean-',
                     tooltip='Slow, Name and Hometown')],

        [sg.Text('' * 30)],

        # Download Gallery
        [sg.Radio('Download From Gallery', "Search_Type", default=False, key='-gallery_download_boolean-',
                  tooltip='TODO, see V1.0 for function')],
        [sg.Text(size=(1, 1)), sg.Frame(layout=[

            [sg.Text('Gallery ID: ', size=(9, 1)), sg.InputText(size=(20, 1), key='-gallery_id-')],

        ], title='', title_color='red', relief=sg.RELIEF_SUNKEN)],

        # File name and location
        [sg.InputText('Output File'), sg.FileSaveAs(key='-file_save_as-')],

        # Search
        [sg.Button('Search')]

    ]

    window = sg.Window("FLICKR GeoSearch", main_layout)

    thread = None

    # ---------EVENT LOOP-----------#

    while True:

        event, values = window.read()

        if event is None or event == 'Exit':
            break

        # Authorization Window
        if event == 'API Authentication' and not auth_window_active:
            sg.theme(program_theme)

            auth_layout = [
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

            auth_window = sg.Window('Authentication', auth_layout)

            auth_window_active = True

        # Authorization Interactions
        while auth_window_active:

            event2, values2 = auth_window.read()

            if event2 == sg.WIN_CLOSED or event2 == 'Cancel' or event2 == 'Ok':
                auth_window.close()
                auth_window_active = False

            if event2 == 'Validate' and not is_authenticated:

                flickr = flickrapi.FlickrAPI(values2['-api_key-'], values2['-secret_key-'])

                auth_window['-Valid_Status-'].update('Validating..')

                if flickr.token_valid(perms='write'):
                    is_authenticated = True

                    auth_window['-Valid_Status-'].update('Validated')
                    auth_window['-Authentication_Status-'].update('Authenticated')

                if not flickr.token_valid(perms='write'):
                    flickr.get_request_token(oauth_callback='oob')

                    # authorization_url = flickr.auth_url(perms='write')
                    webbrowser.open_new(flickr.auth_url(perms='write'))

            if event2 == 'Authenticate' and not is_authenticated:

                auth_window['-Authentication_Status-'].update('Authenticating...')

                verifier = values2['-token-']
                flickr.get_access_token(verifier)

                if flickr.token_valid(perms='write'):
                    is_authenticated = True
                    auth_window['-Authentication_Status-'].update('Authenticated')

        # About Window
        if event == 'About' and not about_window_active:
            sg.theme(program_theme)

            about_layout = [
                [sg.Multiline(
                    default_text="FLICKR GeoSearch V3.0\nCreated by: Matthew Tralka, 2020\nSource available on "
                                 "Github: "
                                 "mtralka\nLicensed under: GNU General Public License v3.0\n\n\n\nUses the Flickr API "
                                 "to "
                                 "execute geospatial photo searches. Results are auto formatted into an excel file and "
                                 "can be "
                                 "uploaded to Flickr photo galleries for review. Also supports the download of photos "
                                 "from "
                                 "Flickr photo galleries. "
                                 "", enter_submits=False, disabled=True, autoscroll=False, enable_events=False,
                    do_not_clear=True, size=(50, 30))],

            ]

            about_window = sg.Window('About', about_layout)

            about_window_active = True

        # About Interactions
        while about_window_active:

            event3, values3 = about_window.read()

            if event3 == sg.WIN_CLOSED:
                about_window.close()
                about_window_active = False

        # Accuracy Slider
        window['-accuracy-'].update(values['-slider_accuracy-'])
        if values['-accuracy_boolean-']:
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

        # Search Command
        if event == 'Search' and not is_authenticated:
            sg.popup("Authentication Needed", title="Error", background_color='red', no_titlebar=True)

        if event == 'Search' and is_authenticated and not thread:
            search = flickrSearchParameters(values)

            thread = threading.Thread(target=long_operation_thread, daemon=True,
                                      kwargs={'flickr': flickr, 'search': search})
            thread.start()

        # Threading
        if thread:

            sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white',
                              time_between_frames=1)
            thread.join(timeout=0)

            if not thread.is_alive():
                sg.popup_animated(None)
                thread = None


the_GUI()
