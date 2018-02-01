from cssutils import profile
from cssutils.profiles import Profiles, properties, macros
#patch um up
properties[Profiles.CSS_LEVEL_2]['-ms-interpolation-mode'] = r'none|bicubic|nearest-neighbor'
properties[Profiles.CSS_LEVEL_2]['-ms-text-size-adjust'] = r'none|auto|{percentage}'
properties[Profiles.CSS_LEVEL_2]['mso-table-lspace'] = r'0|{num}(pt)'
properties[Profiles.CSS_LEVEL_2]['mso-table-rspace'] = r'0|{num}(pt)'
properties[Profiles.CSS_LEVEL_2]['-webkit-text-size-adjust'] = r'none|auto|{percentage}'
#re-add
profile.addProfiles([(Profiles.CSS_LEVEL_2,
                           properties[Profiles.CSS_LEVEL_2],
                           macros[Profiles.CSS_LEVEL_2]
                           )])