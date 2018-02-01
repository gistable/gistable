#!/usr/bin/env python 
function server() {
        local port="${1:-8000}"
        open "http://localhost:${port}/"
        python SimpleHTTPServer "$port"
}