HTTPHeaderBrowserTesting
==

## About

This is the source code of an automated service (reachable under https://much.ninja) that allows you to test your browser behavior regarding header enforcement and duplicated headers and conflicting directives.

Duplicated headers are multiple headers with the same name in a HTTP response:
```
X-Frame-Options: deny
X-Frame-Options: sameorigin
```
An example for conflicting directives within a header would be:
`X-Frame-Options: deny, sameorigin`

We also test what happens, if the browser encounters invalid directives or invalid header values:
`X-Frame-Options: random, deny`
or
`Strict-Transport-Security: max-age: 60, includeSubdomains` (a comma is used as separator)


In particular, we test the following headers:
- Duplicated X-Frame-Options (XFO) headers and conflicting directives
- X-Frame-Options via meta tag
- Content-Security-Policy (CSP) frame-ancestors
- Content-Security-Policy frame-ancestors via meta tag
- X-Frame-Options and Content-Security-Policy frame-ancestors (both set)
- Duplicated Strict-Transport-Security (HSTS) headers and conflicting directives
- Duplicated CORS headers and conflicting directives (SOP subset XMLHttpRequest)
	- Access-Control-Allow-Origin
	- Access-Control-Allow-Credentials
	- Access-Control-Allow-Headers
	- Access-Control-Allow-Methods
	- Access-Control-Expose-Headers

## Methodology

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

1. Edit `/etc/hosts`
```
sudo vim /etc/hosts

127.0.0.1       much.ninja
127.0.0.1       sub.much.ninja
```
2. Clone it
```
git clone git@github.com:hen95/HTTPHeaderBrowserTesting.git
```

3. Create local certificates (tested on Chromium/Chrome)

You can use the tool `mkcert` (see https://github.com/FiloSottile/mkcert) to create trusted certificates.
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


3. Run it
```
cd ~/HTTPHeaderBrowserTesting && docker-compose up
```
## BrowserStack
We automated the testing process with BrowserStack. A BrowserStack account is needed to automate it.
The script that is used to automate the testing process is in [automateit/](automateit/).

## analyze-tranco
Martin prepared a Dockerfile to download the newest version of tranco 1m responses.
In `/analyze-tranco/analyze.py` you can find how we looked for possible conflicts in the tranco 1m.
