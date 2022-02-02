FROM mariadb:latest


RUN apt update
RUN apt install -y python3
RUN apt install -y python3-pip
RUN apt install -y unzip
RUN apt install -y curl
RUN pip3 install textdistance
RUN apt install -y libmariadb3 libmariadb-dev
RUN pip3 install mariadb



copy dothings.sh /dothings.sh

CMD ["bash", "/dothings.sh"]


