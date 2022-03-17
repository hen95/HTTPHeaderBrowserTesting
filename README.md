HTTPHeaderBrowserTesting
==

This is the source code of an automated service (reachable under https://much.ninja) that allows you to test your browser behavior regarding header enforcement and duplicated headers and conflicting directives.

## Implementation

All the logic is happening in the folder [www/much.ninja](www/much.ninja).
The base class *Handle* in [www/much.ninja/handle.php](www/much.ninja/handle.php) contains the
functionality to receive and process requests.
The basic idea of the program is to reflect headers, which are requested in the URL query base64
encoded. Thus, it is possible to return different response headers for each request. The function
`b64_to_header` takes care of this functionality.

Every server-side header implementation inherits from this base class, e.g. XFO.php in
[www/much.ninja/XFO/XFO.php](www/much.ninja/XFO/XFO.php).

On the client-side, each header got its own `index.html`, e.g.
[www/much.ninja/XFO/latest/index.html](www/much.ninja/XFO/latest/index.html). Each client-side
implementation follows the following structure:

1. Download test cases.
2. For every test case send a request with the base64 encoded header in the URL query.
3. Check Header enforcement. (XFO & CSP: postMessage to top window, HSTS: request the ressource with
   HTTP and check for redirect to HTTPS, CORS: check if the answer is readable.)
4. Compare the browser's behavior with the target behavior in the specification.


Important steps from the specification have been implemented in
[www/much.ninja/static/parseHeaders.js](www/much.ninja/static/parseHeaders.js).


## Local setup
To run this you need to have `docker` (version 20.10 or higher) installed.

### Create trusted certificate on localhost
To set this up locally, you need to create a certificate for the domain `much.ninja` and
`sub.much.ninja`.

To do this, you first need to modify your `/etc/hosts` accordingly.
```
sudo vim /etc/hosts

127.0.0.1       much.ninja
127.0.0.1       sub.much.ninja
```

Furthermore, you can use the tool `mkcert` (see https://github.com/FiloSottile/mkcert) to create trusted certificates.
For Linux:
```
sudo apt install libnss3-tools
git clone https://github.com/FiloSottile/mkcert && cd mkcert
go build -ldflags "-X main.Version=$(git describe --tags)"
```

Use the following approach to get `fullchain.pem` and `privkey.pem` (see
https://github.com/FiloSottile/mkcert/issues/76#issuecomment-546054007).
```
./mkcert much.ninja sub.much.ninja
cat much.ninja+1.pem > fullchain.pem 
cat "$(./mkcert -CAROOT)/rootCA.pem" >> fullchain.pem
cat much.ninja+1-key.pem > privkey.pem
```
Move `fullchain.pem` and `privkey.pem` to `~/HTTPHeaderBrowserTesting/nginx-proxy/certs`.
Then `docker-compose up -d`.


## BrowserStack
A BrowserStack account is needed to automate it.
The script that is used to automate the testing process is in [automateit/](automateit/).

## analyze-tranco
Martin prepared a Dockerfile to download the newest version of tranco 1m responses.
In `/analyze-tranco/analyze.py` you can find how we looked for possible conflicts in the tranco 1m.
