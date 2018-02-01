def SetBrowserObj(self):
        try:
            if self.browserdriver.strip().upper() == "CHROME":
                options = webdriver.chrome.options.Options()
                options.add_argument("-incognito")
                browser = webdriver.Chrome(chrome_options=options)

            if self.browserdriver.strip().upper() == "FIREFOX":
                browser = webdriver.Firefox()
            self.driver = browser
        except Exception as e:
            self.log.error("****** Unable to load browser object error is: {0}".format(e.message))
            raise e