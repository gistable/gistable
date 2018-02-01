import xlwt
import glob
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

ezxf =xlwt.easyxf
def isApple(fn):
	flag= False
	i = Image.open(fn)
	info = i._getexif()
	if info:
		for tag, value in info.items():
			decoded = TAGS.get(tag, tag)
			if decoded =="Make" and value =="Apple":
				flag= True
	return flag

def get_exif_data(fn):
	"""Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
	exif_data = {}
	i = Image.open(fn)
	info = i._getexif()
	if info:
		for tag, value in info.items():
			decoded = TAGS.get(tag, tag)
			if decoded == "GPSInfo":
				gps_data = {}
				for t in value:
					sub_decoded = GPSTAGS.get(t, t)
					gps_data[sub_decoded] = value[t]
				exif_data[decoded] = gps_data
			else:
				exif_data[decoded] = value
	return exif_data
 
def _get_if_exist(data, key):
    if key in data:
        return data[key]
		
    return None
	
def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)
 
    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)
 
    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)
 
    return d + (m / 60.0) + (s / 3600.0)
 
def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if "GPSInfo" in exif_data:		
        gps_info = exif_data["GPSInfo"]
 
        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')
 
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":                     
                lat = 0 - lat
 
            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
    return lat, lon
 
def write_xls(file_name, sheet_name, headings, data, heading_xf, data_xfs):
    book = xlwt.Workbook()
    sheet = book.add_sheet(sheet_name.decode('cp949'))
    rowx = 0
    for colx, value in enumerate(headings):
		if (type(value) == int or type(value) == float):
			sheet.write(rowx, colx, value, data_xfs[colx])
		else:
			sheet.write(rowx, colx, value.decode('cp949'), data_xfs[colx])
    sheet.set_panes_frozen(True) # frozen headings instead of split panes
    sheet.set_horz_split_pos(rowx+1) # in general, freeze after last heading row
    sheet.set_remove_splits(True) # if user does unfreeze, don't leave a split there
    for row in data:
        rowx += 1
        for colx, value in enumerate(row):
			if (type(value) == int or type(value) == float):
				sheet.write(rowx, colx, value, data_xfs[colx])
			else:
				sheet.write(rowx, colx, value.decode('cp949'), data_xfs[colx])
    book.save(file_name)

################
# Example ########
################
if __name__ == "__main__":
	data = []
	file_list  = glob.glob('INPUT FILE PATH AND FILE FORMAT') #input file path and file format e.g. "c:\pictures\\*.jpg"
	for file_name in file_list: 
		image = file_name
		exif_data = get_exif_data(image)
		#Only focus on pictures taken by Apple product
		if isApple(image):
			exif_data = get_exif_data(image)
			Date = exif_data['DateTimeOriginal'].split()[0]
			Time = exif_data['DateTimeOriginal'].split()[1]
			Lat = get_lat_lon(exif_data)[0]
			Lon = get_lat_lon(exif_data)[1]

			#Only write data when the picture has GPS information 
			if Lat != None and Lon != None:
				data +=[[file_name[file_name.find("test\\")+5:], Date, Time, Lat, Lon]]

	# prepare for writing on Excel file
	hdngs = ['Filename', 'Date', 'Time', 'Latitude', 'Longitude']
	kinds =  'text	date	time float float'.split()
	heading_xf = ezxf('font: bold on;  align: wrap on, vert centre, horiz center;')
	kind_to_xf_map = {
	'date': ezxf(num_format_str='yyyy:mm:dd'),
	'time': ezxf(num_format_str='hh:mm:ss'),
	'int': ezxf(num_format_str='#,##0'),
	'float':ezxf(num_format_str='#.##0'),
	'text': ezxf(),
	}
	data_xfs = [kind_to_xf_map[k] for k in kinds]
	output_file_name = 'OUTPUT FILE PATH AND FILE NAME' #output file path and file name e.g. "c:\data.xls"

	print output_file_name
	# write data on Excel file
	write_xls(output_file_name, 'photo', hdngs, data, heading_xf, data_xfs)
