def screenshotFilter(poi):
    '''This looks for signs that have their first line in the 'Image:<id>' format, where <id> is an
    id from an Imgur.com image.'''
    if poi['id'] == 'Sign':
        if poi['Text1'].startswith('Image:'):
            poi['icon'] = "painting_icon.png"
            image_html = "<style>.infoWindow img[src='{icon}'] {{display: none}}</style><a href='http://imgur.com/{id}'><img src='http://imgur.com/{id}s.jpg' /></a>".format(icon=poi['icon'], id=poi['Text1'][6:])
            return "\n".join([image_html, poi['Text2'], poi['Text3'], poi['Text4']])

def playerFilter(poi):
    '''This finds the players and formats the popup bubble a bit.
    TODO:  Work in health, armor, and hunger'''
    
    def meterHelper(meter, icon, reversed=False, spacer=False):
        '''Helper function for playerFilter() that builds a pretty bar for hunger/armor/health/etc.
        We're going to make the assumption that for every icon, there is the equivalent half_icon,
        and empty_icon.'''
        if spacer:
            empty = 'blank.gif'
        else:
            empty = 'empty_{}'.format(icon)
        full_icons = ''.join(["<img src='{}' />".format(icon) for i in range(meter // 2)])
        half_icons = ''.join(["<img src='half_{}' />".format(icon) for i in range(meter % 2)])
        blank_icons = ''.join(["<img src='{}' />".format(empty) for i in range(10 - ((meter // 2) + (meter % 2)))])
        if reversed:
            return blank_icons + half_icons + full_icons
        else:
            return full_icons + half_icons + blank_icons
    
    # Dict of defese points Each row goes leather/cm/iron/diamond/gold and each column is helm/chest/pants/shoes
    # Everything is doubled so we can feed it easier into metaHelper()
    armor = {298 : 1, 299 : 3, 300 : 2, 301 : 1,
             302 : 2, 303 : 5, 304 : 4, 305 : 1,
             306 : 2, 307 : 6, 308 : 5, 309 : 2,
             310 : 3, 311 : 8, 312 : 6, 313 : 3,
             314 : 2, 315 : 5, 316 : 3, 317 : 1}
             
    if poi['id'] == 'Player':
        poi['icon'] = "http://cravatar.tomheinan.com/{}/16".format(poi['EntityId'])
        image_html = "<style>.infoWindow img[src='{}'] {{display: none}}</style><img src='http://overviewer.org/avatar/{}' />".format(poi['icon'], poi['EntityId'])
        #calculate the defense points
        defense_points = 0
        for i in poi['Inventory']:
            if i['Slot'] in (100, 101, 102, 103):
                defense_points += armor[i['id']]
        return "\n".join([image_html, meterHelper(defense_points, 'armor.png') + meterHelper(poi['Air'] // 15, 'bubble.png', reversed=True, spacer=True),
                           meterHelper(poi['Health'], 'heart.png') + meterHelper(poi['foodLevel'], 'hunger.png', reversed=True),
                           "Current location for {}".format(poi['EntityId']), "X:{} Y:{} Z:{}".format(poi['x'], poi['y'], poi['z'])])

def bedFilter(poi):
    '''This finds the beds and formats the popup bubble a bit.'''
    if poi['id'] == 'PlayerSpawn':
        poi['icon'] = 'bed_icon.png'
        image_html = "<style>.infoWindow img[src='{}'] {{display: none}}</style><img src='http://cravatar.tomheinan.com/{}/16' />".format(poi['icon'], poi['EntityId'])
        return "\n".join([image_html, "Current spawn point for {}".format(poi['EntityId']),
                           "X:{} Y:{} Z:{}".format(poi['x'], poi['y'], poi['z'])])
