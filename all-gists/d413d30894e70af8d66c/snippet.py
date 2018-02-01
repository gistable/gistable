        param = self.request.get("ch10")
        referer = self.request.referer
        xreferer = self.request.headers.get('X-Referer')
        valid_referer = "http://pentesteracademylab.appspot.com/lab/webapp/csrf/10"

        if referer or xreferer:
            if param == flag and (referer == valid_referer or str(xreferer) == valid_referer) :
                cid = "success"
                self.response.headers.add_header("Set-Cookie", "cid-csrf10="+cid)
                self.redirect("/lab/webapp/csrf/10")
                return
