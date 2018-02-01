#!/usr/bin/env python

import lldb

def slack(debugger, command, result, internal_dict):
    frame = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame()
    path = command

    lldb.debugger.HandleCommand("""
    expr -l swift --
    func $sendToSlackForFileUpload(path: String) {
        let URL = NSURL(fileURLWithPath: NSHomeDirectory()).URLByAppendingPathComponent(path)
        let fileName = path.componentsSeparatedByString("/").last!
        guard let data = NSData(contentsOfURL: URL) else { print("not found: \(URL.absoluteString)"); return }

        var url = "https://slack.com/api/files.upload?"
        [
            "token": "<your-token>",
            "channels": "#general",
            "title": ":lldb:",
            "initial_comment": URL.absoluteString,
        ].forEach { (key, value) in
            if let encodedValue = value.stringByAddingPercentEncodingWithAllowedCharacters(NSCharacterSet.URLHostAllowedCharacterSet()) {
                url += "&\(key)=\(encodedValue)"
            }
        }

        let newline = "\\r\\n"
        let boundary = String(format: "boundary.%08x%08x", arc4random(), arc4random())
        let body = NSMutableData()
        body.appendData("--\(boundary)\(newline)".dataUsingEncoding(NSUTF8StringEncoding)!)
        body.appendData("Content-Disposition: form-data; name=\\\"file\\\"; filename=\\\"\(fileName)\\\"\(newline)\".dataUsingEncoding(NSUTF8StringEncoding)!)
        body.appendData("Content-Type: auto\(newline)\(newline)".dataUsingEncoding(NSUTF8StringEncoding)!)
        body.appendData(data)
        body.appendData(newline.dataUsingEncoding(NSUTF8StringEncoding)!)
        body.appendData("--\(boundary)--\(newline)".dataUsingEncoding(NSUTF8StringEncoding)!)

        let request = NSMutableURLRequest(URL: NSURL(string: url)!)
        request.HTTPMethod = "POST"
        request.setValue("multipart/form-data; boundary=" + boundary, forHTTPHeaderField: "Content-Type")
        request.HTTPBody = body

        print("Please run 'continue'")
        NSURLSession.sharedSession().dataTaskWithRequest(request) { (data, response, error) -> Void in
            guard error == nil else { print("failed upload: \(error)"); return }
            print("upload success")
        }.resume()
    }
    """.strip())
    expr = 'expr -l swift -- $sendToSlackForFileUpload(' + path + ')'
    lldb.debugger.HandleCommand(expr)

def __lldb_init_module(debugger,internal_dict):
    debugger.HandleCommand("command script add -f slack.slack slack")
    print"slack command enabled."