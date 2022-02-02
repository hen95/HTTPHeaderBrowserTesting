BASEURL="https://sslstudy.s3.eu-central-003.backblazeb2.com"
indexurl="$BASEURL/index.html"
echo "getting list of all scans"
curl -L  $indexurl  --output overview.html
current=$(grep  -oe '[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]\.zip' overview.html | head -1)
echo "getting the current scan - this might take a while"
currenturl="$BASEURL/$current"
curl -L  $currenturl --output dataset.zip
echo "unzipping"
unzip dataset.zip
gunzip crawler.sql.gz

echo "writing to db in db-container"

mariadb -u root -h db -plightinthehead -e "SOURCE crawler.sql"
