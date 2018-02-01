def create_pin_files(data_frame, outdir = '/outdir/path/only/' ):
    """  
    Batch process the creation of BEAM-VISAT (http://www.brockmann-consult.de/cms/web/beam/) pin files. 
    Outputs a "pin_sampling_date_batched.placemark" file.
    Uses pandas data_frame as input. 
    Expected column names in the input data frame are:
        ["IS_DATE"] YYYYMMDD format
        ["SITE"]  Name of the Placemark, ie. station, sampling site or Cast ID
        ["Latitude"]  Latitude of Placemark in decimal degrees using WGS84 datum
        ["Longitude"] Longitude of Placemark in decimal degrees using WGS84 datum
    
    __maintainer__ = "[José M. Beltrán](<beltran.data@gmail.com>)"
    __credits__ = ["José M. Beltrán"]
    __license__ = "GPL-3.0"
    __created_on__ = ["2014-10-15"]       
    """
       
    # Grouping by date
    bygroup_date = data_frame.groupby('IS_DATE')
    # Creating a dictionary using the dates as keys and a list of row indices for the placemarks
    date_groups = bygroup_date.groups
    # initializing the skeleton that builds an xml pin file
    skeleton = {}
    for key, group in date_groups.items():
        # Using key date as string 
        date_string = str(key)
        # Populating the xml
        skeleton[date_string] = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
        skeleton[date_string] += '<Placemarks>\n'
        for i in group:
            skeleton[date_string] += '  <Placemark name="' + str(data_frame["SITE"][i]) + '">\n'
            skeleton[date_string] += '    <LABEL>' + str(data_frame["SITE"][i]) + '</LABEL>\n'
            skeleton[date_string] += '    <LATITUDE>' + str(data_frame["Latitude"][i]) + '</LATITUDE>\n'
            skeleton[date_string] += '    <LONGITUDE>' + str(data_frame["Longitude"][i]) + '</LONGITUDE>\n'
            skeleton[date_string] += '    <PIXEL_X />\n'
            skeleton[date_string] += '    <PIXEL_y />\n'    #
            skeleton[date_string] += '  </Placemark>\n'
        skeleton[date_string] += '</Placemarks>\n'
        filename = outdir + "pin_"+date_string+"_batched.placemark"
        # Saving to file
        try:
            with open(filename,'w') as f:
                f.write(skeleton[date_string])
        except IOError as e:
            print e
            return 0         
            
    return ("pin(s) creation done. Placemarks files in:",outdir)