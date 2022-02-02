HTTPHeaderBrowserTesting
==

This tool is the source code of an automated service (reachable under https://much.ninja) that allows you to test your browser behavior regarding header enforcement and duplicated headers and conflicting directives.

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
cat ninja+1-key.pem > privkey.pem
```
Move `fullchain.pem` and `privkey.pem` to `~/HTTPHeaderBrowserTesting/nginx-proxy/certs`.
Then `docker-compose up -d`.


## BrowserStack
A BrowserStack account is needed to automate it.
The script that is used to automate the testing process is in `/automateit`.

## analyze-tranco
Martin prepared a Dockerfile to download the newest version of tranco 1m responses.
In `/analyze-tranco/analyze.py` you can find how we looked for possible conflicts in the tranco 1m.
