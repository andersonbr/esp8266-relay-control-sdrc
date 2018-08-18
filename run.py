import machine

pins = [
    #{'label': 'GPIO16 (D0)', 'index': 16 },
    {'label': 'GPIO5 (D1)', 'index': 5 },
    {'label': 'GPIO4 (D2)', 'index': 4 },
    #{'label': 'GPIO0 (D3)', 'index': 0 },
    #{'label': 'GPIO2 (D4)', 'index': 2 },
    {'label': 'GPIO14 (D5)', 'index': 14 },
    {'label': 'GPIO12 (D6)', 'index': 12 },
    {'label': 'GPIO13 (D7)', 'index': 13 },
    #{'label': 'GPIO15 (D8)', 'index': 15 }
]
pins = [{'label': pin['label'], 'index': pin['index'], 'pin': machine.Pin(pin['index'], machine.Pin.OUT) } for pin in pins]
# iniciar desativado
for pin in pins:
    pin['pin'].value(0)

head = """HTTP/1.1 200 OK\r
Server: SDRC\r
Content-Type: text/html; charset=utf-8\r
Content-Length: %d\r
Connection: Closed\r
\r
"""

body = """<!DOCTYPE html>
<html>
    <head>
        <title>SDRC</title>
        <meta name="viewport" content="width=device-width, user-scalable=no">
        <script type="text/javascript">
            window.onload = function() {
                document.querySelectorAll(".status_0").forEach((e, i) => {
                    e.innerHTML = "Ligar"
                });
                document.querySelectorAll(".status_1").forEach((e, i) => {
                    e.innerHTML = "Desligar"
                });
                document.querySelector("table").onclick = ((e) => {
                    var t = e.target;
                    var p = t.dataset.pin;
                    var l = (t.className == "status_0")?1:0;
                    window.location.href = ("/pin/" + p + "/" + l)
                })
            }
        </script>
        <style type="text/css">
            .status_0 {
                color: white;
                background-color: red;
                cursor: pointer;
            }
            .status_1 {
                color: white;
                background-color: green;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Disciplina Sistemas Distribuidos e Redes de Comunicação</h1>
        <h2>Anderson Calixto - andersonbr@lia.ufc.br</h2>
        <table border="1" cellpadding="4" cellspacing="0" width="100%%">
            <thead>
                <tr><th>Porta</th><th>Ações</th></tr>
            </thead>
            <tbody>
%s
            </tbody>
        </table>
    </body>
</html>"""
def parse_header(line):
    ra = line.split(":")
    return (ra[0].strip(), ra[1].strip())

import socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        parts = line.decode('UTF-8').split(" ")
        if parts[0] == "GET":
            print("URL: %s\n" % parts[1])
            pinParts = parts[1].split("/")
            # exemplo: /pin/4/1 # habilitar/desabilitar pin
            if (len(pinParts) == 4 and pinParts[1] == "pin"):
                pinNum = int(pinParts[2])
                pinValue = int(pinParts[3])
                p = machine.Pin(pinNum, machine.Pin.OUT)
                p.value(pinValue)
        if not line or line == b'\r\n':
            break

    rows = ['                <tr><td>%s</td><td class="status_%d" data-pin="%d"></td></tr>' % (p['label'], p['pin'].value(), p['index']) for p in pins]
    response_body = body % ('\n'.join(rows))
    response_head = head % (len(response_body))
    response = response_head + response_body
    cl.sendall(response)
    cl.close()
