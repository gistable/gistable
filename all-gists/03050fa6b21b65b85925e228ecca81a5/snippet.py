import socket, machine

# This is the HTML, CSS and js to deliver to the client.
# You can (should) store this in another file and read from there,
# but I am lazy.
# The CSS and HTML to display pretty code is from pygments.
upy = """<!DOCTYPE html>
<html>
<head>
  <title>I'm a website running on a Microcontroller.</title>
  <meta charset="utf-8">

  <style>
    body {
      display: table;
      height: 100%;
      width: 100%;
      position: absolute;
      overflow: hidden;
      font-family: Source Serif Pro;
    }
    slides {
      display: table-cell;
      vertical-align: middle;
    }
    slide {
      margin: 0 auto;
    }
    article {
      margin: 10%;
    }
    h1 {
      text-align: center;
      font-size: 5em;
    }
    h2 {
      text-align: center;
      font-size: 5em;
    }
    p {
      font-size: 3em;
    }
pre { font-size: 2em }
pre .c { color: #60a0b0; font-style: italic } /* Comment */
pre .err { border: 1px solid #FF0000 } /* Error */
pre .k { color: #007020; font-weight: bold } /* Keyword */
pre .o { color: #666666 } /* Operator */
pre .ch { color: #60a0b0; font-style: italic } /* Comment.Hashbang */
pre .cm { color: #60a0b0; font-style: italic } /* Comment.Multiline */
pre .cp { color: #007020 } /* Comment.Preproc */
pre .cpf { color: #60a0b0; font-style: italic } /* Comment.PreprocFile */
pre .c1 { color: #60a0b0; font-style: italic } /* Comment.Single */
pre .gd { color: #A00000 } /* Generic.Deleted */
pre .ge { font-style: italic } /* Generic.Emph */
pre .gr { color: #FF0000 } /* Generic.Error */
pre .gh { color: #000080; font-weight: bold } /* Generic.Heading */
pre .gi { color: #00A000 } /* Generic.Inserted */
pre .go { color: #888888 } /* Generic.Output */
pre .gp { color: #c65d09; font-weight: bold } /* Generic.Prompt */
pre .gs { font-weight: bold } /* Generic.Strong */
pre .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
pre .gt { color: #0044DD } /* Generic.Traceback */
pre .kc { color: #007020; font-weight: bold } /* Keyword.Constant */
pre .kd { color: #007020; font-weight: bold } /* Keyword.Declaration */
pre .kn { color: #007020; font-weight: bold } /* Keyword.Namespace */
pre .kp { color: #007020 } /* Keyword.Pseudo */
pre .kr { color: #007020; font-weight: bold } /* Keyword.Reserved */
pre .kt { color: #902000 } /* Keyword.Type */
pre .m { color: #40a070 } /* Literal.Number */
pre .s { color: #4070a0 } /* Literal.String */
pre .na { color: #4070a0 } /* Name.Attribute */
pre .nb { color: #007020 } /* Name.Builtin */
pre .nc { color: #0e84b5; font-weight: bold } /* Name.Class */
pre .no { color: #60add5 } /* Name.Constant */
pre .nd { color: #555555; font-weight: bold } /* Name.Decorator */
pre .ni { color: #d55537; font-weight: bold } /* Name.Entity */
pre .ne { color: #007020 } /* Name.Exception */
pre .nf { color: #06287e } /* Name.Function */
pre .nl { color: #002070; font-weight: bold } /* Name.Label */
pre .nn { color: #0e84b5; font-weight: bold } /* Name.Namespace */
pre .nt { color: #062873; font-weight: bold } /* Name.Tag */
pre .nv { color: #bb60d5 } /* Name.Variable */
pre .ow { color: #007020; font-weight: bold } /* Operator.Word */
pre .w { color: #bbbbbb } /* Text.Whitespace */
pre .mb { color: #40a070 } /* Literal.Number.Bin */
pre .mf { color: #40a070 } /* Literal.Number.Float */
pre .mh { color: #40a070 } /* Literal.Number.Hex */
pre .mi { color: #40a070 } /* Literal.Number.Integer */
pre .mo { color: #40a070 } /* Literal.Number.Oct */
pre .sb { color: #4070a0 } /* Literal.String.Backtick */
pre .sc { color: #4070a0 } /* Literal.String.Char */
pre .sd { color: #4070a0; font-style: italic } /* Literal.String.Doc */
pre .s2 { color: #4070a0 } /* Literal.String.Double */
pre .se { color: #4070a0; font-weight: bold } /* Literal.String.Escape */
pre .sh { color: #4070a0 } /* Literal.String.Heredoc */
pre .si { color: #70a0d0; font-style: italic } /* Literal.String.Interpol */
pre .sx { color: #c65d09 } /* Literal.String.Other */
pre .sr { color: #235388 } /* Literal.String.Regex */
pre .s1 { color: #4070a0 } /* Literal.String.Single */
pre .ss { color: #517918 } /* Literal.String.Symbol */
pre .bp { color: #007020 } /* Name.Builtin.Pseudo */
pre .vc { color: #bb60d5 } /* Name.Variable.Class */
pre .vg { color: #bb60d5 } /* Name.Variable.Global */
pre .vi { color: #bb60d5 } /* Name.Variable.Instance */
pre .il { color: #40a070 } /* Literal.Number.Integer.Long */
.syntax pre .c { color: #60a0b0; font-style: italic } /* Comment */
.syntax pre .err { border: 1px solid #FF0000 } /* Error */
.syntax pre .k { color: #007020; font-weight: bold } /* Keyword */
.syntax pre .o { color: #666666 } /* Operator */
.syntax pre .ch { color: #60a0b0; font-style: italic } /* Comment.Hashbang */
.syntax pre .cm { color: #60a0b0; font-style: italic } /* Comment.Multiline */
.syntax pre .cp { color: #007020 } /* Comment.Preproc */
.syntax pre .cpf { color: #60a0b0; font-style: italic } /* Comment.PreprocFile */
.syntax pre .c1 { color: #60a0b0; font-style: italic } /* Comment.Single */
.syntax pre .gd { color: #A00000 } /* Generic.Deleted */
.syntax pre .ge { font-style: italic } /* Generic.Emph */
.syntax pre .gr { color: #FF0000 } /* Generic.Error */
.syntax pre .gh { color: #000080; font-weight: bold } /* Generic.Heading */
.syntax pre .gi { color: #00A000 } /* Generic.Inserted */
.syntax pre .go { color: #888888 } /* Generic.Output */
.syntax pre .gp { color: #c65d09; font-weight: bold } /* Generic.Prompt */
.syntax pre .gs { font-weight: bold } /* Generic.Strong */
.syntax pre .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
.syntax pre .gt { color: #0044DD } /* Generic.Traceback */
.syntax pre .kc { color: #007020; font-weight: bold } /* Keyword.Constant */
.syntax pre .kd { color: #007020; font-weight: bold } /* Keyword.Declaration */
.syntax pre .kn { color: #007020; font-weight: bold } /* Keyword.Namespace */
.syntax pre .kp { color: #007020 } /* Keyword.Pseudo */
.syntax pre .kr { color: #007020; font-weight: bold } /* Keyword.Reserved */
.syntax pre .kt { color: #902000 } /* Keyword.Type */
.syntax pre .m { color: #40a070 } /* Literal.Number */
.syntax pre .s { color: #4070a0 } /* Literal.String */
.syntax pre .na { color: #4070a0 } /* Name.Attribute */
.syntax pre .nb { color: #007020 } /* Name.Builtin */
.syntax pre .nc { color: #0e84b5; font-weight: bold } /* Name.Class */
.syntax pre .no { color: #60add5 } /* Name.Constant */
.syntax pre .nd { color: #555555; font-weight: bold } /* Name.Decorator */
.syntax pre .ni { color: #d55537; font-weight: bold } /* Name.Entity */
.syntax pre .ne { color: #007020 } /* Name.Exception */
.syntax pre .nf { color: #06287e } /* Name.Function */
.syntax pre .nl { color: #002070; font-weight: bold } /* Name.Label */
.syntax pre .nn { color: #0e84b5; font-weight: bold } /* Name.Namespace */
.syntax pre .nt { color: #062873; font-weight: bold } /* Name.Tag */
.syntax pre .nv { color: #bb60d5 } /* Name.Variable */
.syntax pre .ow { color: #007020; font-weight: bold } /* Operator.Word */
.syntax pre .w { color: #bbbbbb } /* Text.Whitespace */
.syntax pre .mb { color: #40a070 } /* Literal.Number.Bin */
.syntax pre .mf { color: #40a070 } /* Literal.Number.Float */
.syntax pre .mh { color: #40a070 } /* Literal.Number.Hex */
.syntax pre .mi { color: #40a070 } /* Literal.Number.Integer */
.syntax pre .mo { color: #40a070 } /* Literal.Number.Oct */
.syntax pre .sb { color: #4070a0 } /* Literal.String.Backtick */
.syntax pre .sc { color: #4070a0 } /* Literal.String.Char */
.syntax pre .sd { color: #4070a0; font-style: italic } /* Literal.String.Doc */
.syntax pre .s2 { color: #4070a0 } /* Literal.String.Double */
.syntax pre .se { color: #4070a0; font-weight: bold } /* Literal.String.Escape */
.syntax pre .sh { color: #4070a0 } /* Literal.String.Heredoc */
.syntax pre .si { color: #70a0d0; font-style: italic } /* Literal.String.Interpol */
.syntax pre .sx { color: #c65d09 } /* Literal.String.Other */
.syntax pre .sr { color: #235388 } /* Literal.String.Regex */
.syntax pre .s1 { color: #4070a0 } /* Literal.String.Single */
.syntax pre .ss { color: #517918 } /* Literal.String.Symbol */
.syntax pre .bp { color: #007020 } /* Name.Builtin.Pseudo */
.syntax pre .vc { color: #bb60d5 } /* Name.Variable.Class */
.syntax pre .vg { color: #bb60d5 } /* Name.Variable.Global */
.syntax pre .vi { color: #bb60d5 } /* Name.Variable.Instance */
.syntax pre .il { color: #40a070 } /* Literal.Number.Integer.Long */
  </style>

</head>
<body>

<slides>

  <slide>
    <article>
      <h1>Micro Python</h1>
    </article>
  </slide>

  <slide>
    <article>
      <p><em>small</em> implementation of Python 3<p>
      <p>binary size 250kb vs. 1Mb</p>
      <p>RAM 100kb vs. 3Mb<p>
    </article>
  </slide>

  <slide>
    <article>
      <h2>Pyboard</h2>
      <p>ARM 32bit µC<p>
      <p>160MHz, 1Mb Flash, 196kb RAM</p>
      <p>ADCs, I2C, SPI, UART, IRQ, ...<p>
    </article>
  </slide>

  <slide>
    <article>
      <h2>ESP8266</h2>
      <p>ARM 32bit µC<p>
      <p>80MHz, 4Mb Flash, 64kb RAM</p>
      <p>WiFi!!!<p>
      <p>€2.5!!!!!!<p>
    </article>
  </slide>

  <slide>
    <article>
      <code>
<div class="hlcode">
<div class="syntax"><pre><span></span><span class="kn">import</span> <span class="nn">socket</span>

<span class="n">sock</span><span class="o">.</span><span class="n">bind</span><span class="p">((</span><span class="s1">&#39;192.168.1.1&#39;</span><span class="p">,</span> <span class="mi">8080</span><span class="p">))</span>
<span class="n">sock</span><span class="o">.</span><span class="n">listen</span><span class="p">()</span>

<span class="k">while</span> <span class="kc">True</span><span class="p">:</span>
    <span class="n">conn</span><span class="p">,</span> <span class="n">addr</span> <span class="o">=</span> <span class="n">sock</span><span class="o">.</span><span class="n">accept</span><span class="p">()</span>
    <span class="n">conn</span><span class="o">.</span><span class="n">sendall</span><span class="p">(</span><span class="s2">&quot;HTTP/1.0 200 OK</span><span class="se">\n</span><span class="s2">Content-Type: text/html</span><span class="se">\n\n</span><span class="s2">Hello World!&quot;</span><span class="p">)</span>
    <span class="n">conn</span><span class="o">.</span><span class="n">close</span><span class="p">()</span>
</pre></div>
</div>
      <code>
    </article>
  </slide>

</slides>

</body>
</html>

  <script>
document.onkeydown = checkKey;

var slides = document.getElementsByTagName("slide");
for (var i=1; i<slides.length; i++) { slides[i].style.display = "None" };

var sno = 0;

function checkKey(e) {

    e = e || window.event;

    if (e.keyCode == '37') {
        // left arrow
        slides[sno].style.display = "None";
        if (sno==0) {sno=slides.length};
        sno--;
        slides[sno].style.display = "";
    }
    else if (e.keyCode == '39') {
        // rigth arrow
        slides[sno].style.display = "None";
        sno++;
        if (sno==slides.length) {sno=0};
        slides[sno].style.display = "";
    }
}
  </script>"""

# This is the actual 'webserver' to deliver the site.
# This is a minimal example on how to handle a GET request.
# Build your own awesome server from here.
# This is tested on the WiPy board, but will also run on all other boards
# with WiFi, but you will need to take care of setting up the WiFi accordingly.

# create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
try:
    sock.bind(('192.168.1.1', 8080))
except OSError:
    machine.reset()
sock.listen()

# helper to create HTML message from payload
def message(payload):
    return """HTTP/1.0 200 OK
Content-Type: text/html

""" + payload

# dictonary for different payloads
# you can fill this with all the sites you want
payload = {'/': 'This works.',
           '/uPy': upy}

# the actual webserver recieve requests and answer them
# this is blocking - try to make it non-blocking!
def webserver():
    while True:
        try:
            conn, addr = sock.accept()
            req = str(conn.recv(1024)).split()[1]
            # dirty trick to quit the webserver
            if req == '/quit':
                conn.close()
                break
            try:
                conn.sendall(message(payload[req]))
            except KeyError:
                conn.sendall(message('404'))
                print('wrong URL')
        except OSError:
            pass

webserver()