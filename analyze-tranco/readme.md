# Analyze Tranco
This folder contains a docker image to download the newest Scott Helme Tranco 1m responses.
After downloading, the responses are then saved in a DB.

By doing `docker-compose up`, the script `dothings.sh` does its work. This might take some minutes.
After downloading the responses, you can use the script `analyze.py` to look for **possible** conflicts like we did.

Note: That does not mean that these conflicts are real conflicts in browsers. These are just potential conflicts.


