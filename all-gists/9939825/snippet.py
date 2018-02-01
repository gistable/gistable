# 又拍云 python sdk 添加更新缓存的接口
def update_cache(self, urls):
    """
    >>>    url1 = "http://kaka.b0.upaiyun.com/kaka_001.flv"
    >>>    url2 = "http://kaka.b0.upaiyun.com/kaka_002.flv"
    >>>    urls = [url1, url2]
    >>>    res = up.update_cache(urls)
    >>>    return tuple (status, content)
    """

    purge_host = "purge.upyun.com"
    # Date Format: RFC 1123
    dt = httpdate_rfc1123(datetime.datetime.utcnow())

    # 每个url之间用"\n"分割，并且每个url都必须以为http开头，否则不会加入刷新队列，
    # 刷新的url数量每分钟有600个限制，且每次最多不超过50个。
    # url = "文件url的完整路径1\n文件url的完整路径2\n"
    purge_str = "\n".join(urls)

    # sign = md5(url + "&" + bucket + "&" + date + "&" + token);
    signature = hashlib.md5("&".join([purge_str, self.bucket, dt, self.password])).hexdigest()
    authorization = 'UpYun ' + self.bucket + ":" + self.username + ":" + signature
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Date": dt,
        "Authorization": authorization
    }

    body = {"purge": purge_str}
    body = urllib.urlencode(body)

    content, msg, err, status = None, None, None, None
    if HTTP_EXTEND is True:
        URL = "http://" + purge_host + "/purge/"
        requests.adapters.DEFAULT_RETRIES = 5
        try:
            response = self.session.request("POST", URL, data=body,
                                            headers=headers,
                                            timeout=self.timeout)
            content = (response.status_code, response.content)
        except requests.exceptions.ConnectionError as e:
            raise UpYunClientException(str(e))
        except requests.exceptions.RequestException as e:
            raise UpYunClientException(str(e))
        except Exception as e:
            raise UpYunClientException(str(e))
    else:
        try:
            connection = httplib.HTTPConnection(purge_host, timeout=self.timeout)
            # connection.set_debuglevel(1)
            connection.request("POST", "/purge/", body, headers)
            response = connection.getresponse()
            content = (response.status, response.read())
        except (httplib.HTTPException, socket.error, socket.timeout) as e:
            raise UpYunClientException(str(e))
        except Exception as e:
            raise UpYunClientException(str(e))
        finally:
            if connection:
                connection.close()

    return content
    
