#!/usr/bin/env python

"""
Regex for URIs

These regex are directly derived from the collected ABNF in RFC3986
(except for DIGIT, ALPHA and HEXDIG, defined by RFC2234).

Additional regex are defined to validate the following schemes according to
their respective specifications:
  - http
  - https
  - file
  - data
  - gopher
  - ws
  - wss
  - mailto
  
See FIXME for areas that still need work.

They should be processed with re.VERBOSE.
"""

__license__ = """
Copyright (c) 2009-2015 Mark Nottingham (code portions)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

### basics - 

DIGIT = r"[\x30-\x39]"

ALPHA = r"[\x41-\x5A\x61-\x7A]"

HEXDIG = r"[\x30-\x39A-Fa-f]"

DQUOTE = r"\""

#   pct-encoded   = "%" HEXDIG HEXDIG
pct_encoded = r" %% %(HEXDIG)s %(HEXDIG)s"  % locals()

#   unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
unreserved = r"(?: %(ALPHA)s | %(DIGIT)s | \- | \. | _ | ~ )"  % locals()

#   gen-delims    = ":" / "/" / "?" / "#" / "[" / "]" / "@"
gen_delims = r"(?: : | / | \? | \# | \[ | \] | @ )"

#   sub-delims    = "!" / "$" / "&" / "'" / "(" / ")"
#                 / "*" / "+" / "," / ";" / "="
sub_delims = r"""(?: ! | \$ | & | ' | \( | \) |
                     \* | \+ | , | ; | = )"""

#   pchar         = unreserved / pct-encoded / sub-delims / ":" / "@"
pchar = r"(?: %(unreserved)s | %(pct_encoded)s | %(sub_delims)s | : | @ )" % locals()

#   reserved      = gen-delims / sub-delims
reserved = r"(?: %(gen_delims)s | %(sub_delims)s )" % locals()


### scheme

#   scheme        = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
scheme = r"%(ALPHA)s (?: %(ALPHA)s | %(DIGIT)s | \+ | \- | \. )*" % locals()


### authority

#   dec-octet     = DIGIT                 ; 0-9
#                 / %x31-39 DIGIT         ; 10-99
#                 / "1" 2DIGIT            ; 100-199
#                 / "2" %x30-34 DIGIT     ; 200-249
#                 / "25" %x30-35          ; 250-255
dec_octet = r"""(?: %(DIGIT)s |
                    [\x31-\x39] %(DIGIT)s |
                    1 %(DIGIT)s{2} |
                    2 [\x30-\x34] %(DIGIT)s |
                    25 [\x30-\x35]
                )
""" % locals()

#  IPv4address   = dec-octet "." dec-octet "." dec-octet "." dec-octet
IPv4address = r"%(dec_octet)s \. %(dec_octet)s \. %(dec_octet)s \. %(dec_octet)s" % locals()

#  h16           = 1*4HEXDIG
h16 = r"(?: %(HEXDIG)s ){1,4}" % locals()

#  ls32          = ( h16 ":" h16 ) / IPv4address
ls32 = r"(?: (?: %(h16)s : %(h16)s ) | %(IPv4address)s )" % locals()

#   IPv6address   =                            6( h16 ":" ) ls32
#                 /                       "::" 5( h16 ":" ) ls32
#                 / [               h16 ] "::" 4( h16 ":" ) ls32
#                 / [ *1( h16 ":" ) h16 ] "::" 3( h16 ":" ) ls32
#                 / [ *2( h16 ":" ) h16 ] "::" 2( h16 ":" ) ls32
#                 / [ *3( h16 ":" ) h16 ] "::"    h16 ":"   ls32
#                 / [ *4( h16 ":" ) h16 ] "::"              ls32
#                 / [ *5( h16 ":" ) h16 ] "::"              h16
#                 / [ *6( h16 ":" ) h16 ] "::"
IPv6address = r"""(?:                         (?: %(h16)s : ){6} %(ls32)s |
                                           :: (?: %(h16)s : ){5} %(ls32)s |
       (?:                      %(h16)s )? :: (?: %(h16)s : ){4} %(ls32)s |
       (?: (?: %(h16)s : ){0,1} %(h16)s )? :: (?: %(h16)s : ){3} %(ls32)s |
       (?: (?: %(h16)s : ){0,2} %(h16)s )? :: (?: %(h16)s : ){2} %(ls32)s |
       (?: (?: %(h16)s : ){0,3} %(h16)s )? ::     %(h16)s :      %(ls32)s |
       (?: (?: %(h16)s : ){0,4} %(h16)s )? ::                    %(ls32)s |
       (?: (?: %(h16)s : ){0,5} %(h16)s )? ::                    %(h16)s  |
       (?: (?: %(h16)s : ){0,6} %(h16)s )? ::
)
""" % locals()

#   IPvFuture     = "v" 1*HEXDIG "." 1*( unreserved / sub-delims / ":" )
IPvFuture = r"v %(HEXDIG)s+ \. (?: %(unreserved)s | %(sub_delims)s | : )+" % locals()

#   IP-literal    = "[" ( IPv6address / IPvFuture  ) "]"
IP_literal = r"\[ (?: %(IPv6address)s | %(IPvFuture)s ) \]" % locals()

#   reg-name      = *( unreserved / pct-encoded / sub-delims )
reg_name = r"(?: %(unreserved)s | %(pct_encoded)s | %(sub_delims)s )*" % locals()

#   userinfo      = *( unreserved / pct-encoded / sub-delims / ":" )
userinfo = r"(?: %(unreserved)s | %(pct_encoded)s | %(sub_delims)s | : )*" % locals()

#   host          = IP-literal / IPv4address / reg-name
host = r"(?: %(IP_literal)s | %(IPv4address)s | %(reg_name)s )" % locals()

#   port          = *DIGIT
port = r"(?: %(DIGIT)s )*" % locals()

#   authority     = [ userinfo "@" ] host [ ":" port ]
authority = r"(?: %(userinfo)s @)? %(host)s (?: : %(port)s)?" % locals()



### Path

#   segment       = *pchar
segment = r"%(pchar)s*" % locals()

#   segment-nz    = 1*pchar
segment_nz = r"%(pchar)s+" % locals()

#   segment-nz-nc = 1*( unreserved / pct-encoded / sub-delims / "@" )
#                 ; non-zero-length segment without any colon ":"
segment_nz_nc = r"(?: %(unreserved)s | %(pct_encoded)s | %(sub_delims)s | @ )+" % locals()

#   path-abempty  = *( "/" segment )
path_abempty = r"(?: / %(segment)s )*" % locals()

#   path-absolute = "/" [ segment-nz *( "/" segment ) ]
path_absolute = r"/ (?: %(segment_nz)s (?: / %(segment)s )* )?" % locals()

#   path-noscheme = segment-nz-nc *( "/" segment )
path_noscheme = r"%(segment_nz_nc)s (?: / %(segment)s )*" % locals()

#   path-rootless = segment-nz *( "/" segment )
path_rootless = r"%(segment_nz)s (?: / %(segment)s )*" % locals()

#   path-empty    = 0<pchar>
path_empty = r""  ### FIXME

#   path          = path-abempty    ; begins with "/" or is empty
#                 / path-absolute   ; begins with "/" but not "//"
#                 / path-noscheme   ; begins with a non-colon segment
#                 / path-rootless   ; begins with a segment
#                 / path-empty      ; zero characters
path = r"""(?: %(path_abempty)s |
               %(path_absolute)s |
               %(path_noscheme)s |
               %(path_rootless)s |
               %(path_empty)s
            )
""" % locals()



### Query and Fragment

#   query         = *( pchar / "/" / "?" )
query = r"(?: %(pchar)s | / | \? )*" % locals()

#   fragment      = *( pchar / "/" / "?" )
fragment = r"(?: %(pchar)s | / | \? )*" % locals()



### URIs

#   hier-part     = "//" authority path-abempty
#                 / path-absolute
#                 / path-rootless
#                 / path-empty
hier_part = r"""(?: (?: // %(authority)s %(path_abempty)s ) |
                    %(path_absolute)s |
                    %(path_rootless)s |
                    %(path_empty)s
                )
""" % locals()

#   relative-part = "//" authority path-abempty
#                 / path-absolute
#                 / path-noscheme
#                 / path-empty
relative_part = r"""(?: (?: // %(authority)s %(path_abempty)s ) |
                        %(path_absolute)s |
                        %(path_noscheme)s |
                        %(path_empty)s
                    )
""" % locals()

#   relative-ref  = relative-part [ "?" query ] [ "#" fragment ]
relative_ref = r"%(relative_part)s (?: \? %(query)s)? (?: \# %(fragment)s)?" % locals()

#   URI           = scheme ":" hier-part [ "?" query ] [ "#" fragment ]
URI = r"(?: %(scheme)s : %(hier_part)s (?: \? %(query)s )? (?: \# %(fragment)s )? )" % locals()

#   URI-reference = URI / relative-ref
URI_reference = r"(?: %(URI)s | %(relative_ref)s )" % locals()

#   absolute-URI  = scheme ":" hier-part [ "?" query ]
absolute_URI = r"(?: %(scheme)s : %(hier_part)s (?: \? %(query)s )? )" % locals()



### HTTP[S] - RFC7230

# http-URI = "http:" "//" authority path-abempty [ "?" query ]
#             [ "#" fragment ]

http_URI = r"(?: http: // %(authority)s %(path_abempty)s (?: \? %(query)s )? (?: \# %(fragment)s )? )" % locals()

# https-URI = "https:" "//" authority path-abempty [ "?" query ]
#              [ "#" fragment ]

https_URI = r"(?: https: // %(authority)s %(path_abempty)s (?: \? %(query)s )? (?: \# %(fragment)s )? )" % locals()



### WS[S] - RFC6455

# ws-URI = "ws:" "//" host [ ":" port ] path [ "?" query ]

ws_URI = r"(?: ws: // %(host)s (?: : %(port)s )? %(path)s (?: \? %(query)s )? )" % locals()

# wss-URI = "wss:" "//" host [ ":" port ] path [ "?" query ]

wss_URI = r"(?: wss: // %(host)s (?: : %(port)s )? %(path)s (?: \? %(query)s )? )" % locals()



### mailto - RFC6068

# some-delims  = "!" / "$" / "'" / "(" / ")" / "*"
#            / "+" / "," / ";" / ":" / "@"

some_delims = r"""(?: ! | \$ | ' | \( | \) | \*
                      \+ | , | ; | : | @ )"""

# qchar        = unreserved / pct-encoded / some-delims

qchar = r"(?: %(unreserved)s | %(pct_encoded)s | %(some_delims)s )" % locals()

# dtext-no-obs = %d33-90 / ; Printable US-ASCII
#              %d94-126  ; characters not including
#                        ; "[", "]", or "\"

dtext_no_obs = r"(?: [\x21-\x5B\x5E-\x7E] )"

# atext           =   ALPHA / DIGIT /    ; Printable US-ASCII
#                     "!" / "#" /        ;  characters not including
#                     "$" / "%" /        ;  specials.  Used for atoms.
#                     "&" / "'" /
#                     "*" / "+" /
#                     "-" / "/" /
#                     "=" / "?" /
#                     "^" / "_" /
#                     "`" / "{" /
#                     "|" / "}" /
#                     "~"
# 
# dot-atom-text   =   1*atext *("." 1*atext)

rfc5322_atext = r"""(?: 
    %(ALPHA)s | %(DIGIT)s | 
    ! | # | 
    \$ | %% | 
    & | ' | 
    \* | \+ | 
    - | / | 
    = | \? | 
    \^ | _ | 
    ` | { | 
    \| | } | 
    ~ )""" % locals()
rfc5322_dot_atom_text = r"(?: %(rfc5322_atext)s{1,} (?: . %(rfc5322_atext)s{1,} )* )" % locals()

# FWS             =   ([*WSP CRLF] 1*WSP) /  obs-FWS
#                                        ; Folding white space
# 
# ctext           =   %d33-39 /          ; Printable US-ASCII
#                     %d42-91 /          ;  characters not including
#                     %d93-126 /         ;  "(", ")", or "\"
#                     obs-ctext
# 
# ccontent        =   ctext / quoted-pair / comment
# 
# comment         =   "(" *([FWS] ccontent) [FWS] ")"
# 
# CFWS            =   (1*([FWS] comment) [FWS]) / FWS

qcontent = rfc5322_FWS = rfc5322_CFWS = r"(?: )"  ## FIXME

# quoted-string   =   [CFWS]
#                     DQUOTE *([FWS] qcontent) [FWS] DQUOTE
#                     [CFWS]

rfc5322_quoted_string = r"""(?:
    (?: %(rfc5322_CFWS)s )? 
    %(DQUOTE)s (?: (?: %(rfc5322_FWS)s )? %(qcontent)s )* (?: %(rfc5322_FWS)s )? %(DQUOTE)s 
    (?: %(rfc5322_CFWS)s )? )
""" % locals()

# domain       = dot-atom-text / "[" *dtext-no-obs "]"

domain = r"(?: %(rfc5322_dot_atom_text)s | (?: \[ %(dtext_no_obs)s* \] ) )" % locals()

# local-part   = dot-atom-text / quoted-string

local_part = r"(?: %(rfc5322_dot_atom_text)s | %(rfc5322_quoted_string)s )" % locals()

# addr-spec    = local-part "@" domain

addr_spec = r"(?: %(local_part)s @ %(domain)s )" % locals()

# hfvalue      = *qchar

hfvalue = r"(?: %(qchar)s* )" % locals()

# hfname       = *qchar

hfname = r"(?: %(qchar)s* )" % locals()

# hfield       = hfname "=" hfvalue

hfield = r"(?: %(hfname)s = %(hfvalue)s )" % locals()

# to           = addr-spec *("," addr-spec )

to = r"(?: %(addr_spec)s (?: , %(addr_spec)s )* )" % locals()

# hfields      = "?" hfield *( "&" hfield )

hfields = r"(?: \? %(hfield)s (?: & %(hfield)s )* )" % locals()

# mailtoURI    = "mailto:" [ to ] [ hfields ]

mailto_URI = r"(?: mailto : (?: %(to)s )? (?: %(hfields)s )? )" % locals()


### data - RFC2397 (+ RFC2045)

# ietf-token := <An extension token defined by a
#                standards-track RFC and registered
#                with IANA.>

rfc2045_token = r"(?: [\x30-\x7A]+ )" #FIXME
rfc2045_ietf_token = rfc2045_token
rfc2045_iana_tokens = rfc2045_token
 
# x-token := <The two characters "X-" or "x-" followed, with
#             no intervening white space, by any token>

rfc2045_x_token = r"(?: [xX] - %(rfc2045_token)s )" % locals()

# extension-token := ietf-token / x-token

rfc2045_extension_token = r"(?: %(rfc2045_ietf_token)s | %(rfc2045_x_token)s )" % locals()

# discrete-type := "text" / "image" / "audio" / "video" /
#                  "application" / extension-token

rfc2045_discrete_type = r"(?: text | image | audio | video | application | %(rfc2045_extension_token)s )" % locals()

# composite-type := "message" / "multipart" / extension-token

rfc2045_composite_type = r"(?: message | multipart | %(rfc2045_extension_token)s )" % locals()

# type := discrete-type / composite-type

rfc2045_type = r"(?: %(rfc2045_discrete_type)s | %(rfc2045_composite_type)s )" % locals()

# subtype := extension-token / iana-token

rfc2045_subtype = r"(?: %(rfc2045_extension_token)s | %(rfc2045_iana_tokens)s )" % locals()

# parameter  := attribute "=" value
# attribute := token
#              ; Matching of attributes
#              ; is ALWAYS case-insensitive.
# 
# value := token / quoted-string

rfc2045_quoted_string = r"(?: )" # FIXME
rfc2045_attribute = r"(?: %(rfc2045_token)s )" % locals()
rfc2045_value = r"(?: %(rfc2045_token)s | %(rfc2045_quoted_string)s )" % locals()
rfc2045_parameter = r"(?: %(rfc2045_attribute)s = %(rfc2045_value)s )" % locals()

# mediatype  := [ type "/" subtype ] *( ";" parameter )

mediatype = r"""(?: 
                    (?: %(rfc2045_type)s / %(rfc2045_subtype)s )? 
                    (?: ; %(rfc2045_parameter)s )*
                )""" % locals()

# uric          = reserved | unreserved | escaped  // 2396
# data       := *urlchar

rfc2396_uric = r"(?: %(reserved)s | %(unreserved)s | %(pct_encoded)s )" % locals()
data = r"(?: %(rfc2396_uric)s* )" % locals()

# dataurl    := "data:" [ mediatype ] [ ";base64" ] "," data

data_URI = r"(?: data : (?: %(mediatype)s )? (?: ;base64 )? , %(data)s )" % locals()

### gopher - RFC4266

# gopher://<host>:<port>/<gopher-path>

gopher_path = path
gopher_URI = r"(?: gopher :// %(host)s : %(port)s / %(gopher_path)s )" % locals()


### file - draft-kerwin-file-scheme-13

# f-scheme       = "file"

file_f_scheme = r"(?: file )"
 
# f-auth         = [ userinfo "@" ] host

file_f_auth = r"(?: (?: %(userinfo)s @ )? %(host)s )" % locals()
 
# unc-path       = 2*3"/" authority path-absolute

file_unc_path = r"(?: /{2,3} %(authority)s %(path_absolute)s )" % locals()
 
# drive-marker   = ":" / "|"

file_drive_marker = r"(?: : | \| )"

# drive-letter   = ALPHA [ drive-marker ]

file_drive_letter = r"(?: %(ALPHA)s (?: %(file_drive_marker)s )? )" % locals()

# windows-path   = drive-letter path-absolute

file_windows_path = r"(?: %(file_drive_letter)s %(path_absolute)s )" % locals()

# local-path     = path-absolute
#                / windows-path

file_local_path = r"(?: %(path_absolute)s | %(file_windows_path)s )" % locals()

# auth-path      = [ f-auth ] path-absolute
#                / unc-path
#                / windows-path

file_auth_path = r"""(?: 
                          (?: %(file_f_auth)s? %(path_absolute)s ) 
                          | %(file_unc_path)s 
                          | %(file_windows_path)s 
                       )""" % locals()

# f-hier-part    = "//" auth-path
#                / local-path

file_f_hier_part = r"(?: (?: // %(file_auth_path)s ) | %(file_local_path)s )" % locals()

# file-URI       = f-scheme ":" f-hier-part [ "?" query ]

file_URI = r"(?: %(file_f_scheme)s : %(file_f_hier_part)s (?: \? %(query)s )? )" % locals()



if "__main__" == __name__:
        import re
        import sys
        try:
                instr = sys.argv[1]
        except IndexError:
                print "usage: %s test-string" % sys.argv[0]
                sys.exit(1)
        
        print 'testing: "%s"' % instr
        
        print "URI:",
        if re.match("^%s$" % URI, instr, re.VERBOSE):
                print "yes"
        else:
                print "no"
        
        print "URI reference:",
        if re.match("^%s$" % URI_reference, instr, re.VERBOSE):
                print "yes"
        else:
                print "no"
        
        print "Absolute URI:",
        if re.match("^%s$" % absolute_URI, instr, re.VERBOSE):
                print "yes"
        else:
                print "no"

        scheme = instr.split(":", 1)[0].lower()
        scheme_validator = locals().get("%s_URI" % scheme, None)
        if scheme_validator:
            print "'%s' URI: " % scheme,
            if re.match("^%s$" % scheme_validator, instr, re.VERBOSE):
                print "yes"
            else:
                print "no"