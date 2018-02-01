class FbInfoParser(object):

    def __init__(self, infoDict):
        self.info_dict = infoDict
        
    def _getItem(self, item):
        return self.info_dict.get(item, None)
    
    def getUserName(self):
        return self._getItem("username")
        
    def getFirstName(self):
        return self._getItem("first_name")
        
    def getLastName(self):
        return self._getItem("last_name")
        
    def getVerified(self):
        return self._getItem("verified")
        
    def getEmail(self):
        return self._getItem("email")
    
    def getBirthDate(self):
        if self.info_dict.has_key("birthday"):
             
            month, day, year = self.info_dict.get("birthday").split("/")
            birthdate = datetime.date(int(year), int(month), int(day))
            
            return birthdate
        return None
    
    def getLanguages(self):
        language_list = []
        if self.info_dict.has_key("languages"):
            for language in self.info_dict.get("languages"):
            language_list.append(language.get("name"))
        return language_list

    def getLocation(self):
        if self.info_dict.has_key("location"):
            return self.info_dict.get("location").get("name")
        return None