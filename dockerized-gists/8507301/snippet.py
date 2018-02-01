def _parse_option(self,symbol):
        #option_format = r'''
        #    ^([\D]{1,6})
        #     ([\d]{2})
        #     ([\d]{2})
        #     ([\d]{2})
        #     ([PC]{1})
        #     ([\d]{5})
        #     ([\d]{3})
        #    $'''
        parsed = re.match(r'^([\D]{1,6})([\d]{2})([\d]{2})([\d]{2})([PC]{1})([\d]{5})([\d]{3})$',
                          symbol)

        ##TODO ADD: [Derivative._parse_option] Raise Appropriate Exception
        if not parsed:
            raise

        self._underlying_symbol = parsed.group(1).upper()
        year = int(parsed.group(2))
        if year > 50: year +=1900
        if year < 50: year +=2000
        self.expiration = datetime(year,
                                   int(parsed.group(3)),
                                   int(parsed.group(4)))
        self.type = parsed.group(5).upper()
        self.strike = float(parsed.group(6)) + float(parsed.group(7))/1000