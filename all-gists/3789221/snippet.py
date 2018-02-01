# More Info: http://davydany.com/post/32287214449/matplotlibs-basemap-plotting-a-list-of-latitude
    def show_map(self, a):
 
        # 'a' is of the format [(lats, lons, data), (lats, lons, data)... (lats, lons, data)]
        lats = [ x[0] for x in a ]
        lons = [ x[1] for x in a ]
        data = [ x[2] for x in a ]
         
        lat_min = min(lats)
        lat_max = max(lats)
        lon_min = min(lons)
        lon_max = max(lons)
        data_min = min(data)
        data_max = max(data)
 
        spatial_resolution = 0.5
        fig = plt.figure()
 
        x = np.array(lats)
        y = np.array(lons)
        z = np.array(data)
       
        xinum = (lat_max - lat_min) / spatial_resolution
        yinum = (lon_max - lon_min) / spatial_resolution
        xi = np.linspace(lat_min, lat_max + spatial_resolution, xinum)        # same as [lat_min:spatial_resolution:lat_max] in matlab
        yi = np.linspace(lon_min, lon_max + spatial_resolution, yinum)        # same as [lon_min:spatial_resolution:lon_max] in matlab
        xi, yi = np.meshgrid(xi, yi)
       
        zi = griddata(x, y, z, xi, yi)
       
        m = Basemap(
            projection = 'merc',
            llcrnrlat=lat_min, urcrnrlat=lat_max,
            llcrnrlon=lon_min, urcrnrlon=lon_max,
            rsphere=6371200., resolution='l', area_thresh=10000
        )
       
        m.drawcoastlines()
        m.drawstates()
        m.drawcountries()
       
        lat, lon = m.makegrid(zi.shape[1], zi.shape[0])
        x,y = m(lat, lon)
        m.contourf(x, y, zi)
       
        plt.show()