FROM nginx:1.26.3

# Install NGINX Package Archive
RUN apt update && apt-get upgrade
RUN apt install -y curl gnupg2 ca-certificates lsb-release debian-archive-keyring
RUN curl https://nginx.org/keys/nginx_signing.key | gpg --dearmor | tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] \
http://nginx.org/packages/debian `lsb_release -cs` nginx" \
    | tee /etc/apt/sources.list.d/nginx.list
RUN echo "Package: *\nPin: origin nginx.org\nPin: release o=nginx\nPin-Priority: 900\n" \
    | tee /etc/apt/preferences.d/99nginx

RUN apt update
RUN apt install -y nginx-module-otel

RUN apt update
RUN apt install -y python3

COPY ./config/nginx.conf /etc/nginx/nginx.template 
COPY ./config/site.conf /etc/nginx/conf.d/site.template

COPY ./config/rewrite-entrypoint.sh /docker-entrypoint.d/40-rewrite-endpoint.sh
COPY ./rewrite.py /rewrite.py