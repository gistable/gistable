from keen.client import KeenClient
keen = KeenClient(
    project_id="123",
    write_key="abc"
)

@app.before_request
def before_request():
    if "/static/" in request.path:
        return

    g.start_time = time.time()

@app.after_request
def send_to_keen(response):
    if request.path.startswith("/static"):
        return response

    keen.add_event("request", {
        "keen" : {
            "addons" : [
                    {
                        "name" : "keen:ip_to_geo",
                        "input" : {
                            "ip" : "ip_address"
                        },
                        "output" : "ip_geo_info"
                    },
                    {
                        "name" : "keen:url_parser",
                        "input" : {
                            "url" : "url"
                        },
                        "output" : "parsed_page_url"
                    }
                ]
        },
        "status": response.status_code,
        "method": request.method,
        "url": request.url,
        "ip_address" : request.remote_addr,
        "response_time_ms": (time.time() - g.start_time) * 1000,
        "endpoint": request.endpoint
    })

    return response