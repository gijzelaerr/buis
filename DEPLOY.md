# setting up demo.pythonic.nl

* Create instance
* modify domain to point to IPv4 and IPv6 address
* create unpriviliged user (srv)
* enable automatic updates: `# sudo dpkg-reconfigure --priority=low unattended-upgrades`
* `# apt-get install rabbitmq-server python3 virtualenv npm python3-dev nginx git`
* `$ cd ~ && git clone https://github.com/gijzelaerr/buis $$ cd buis`
* `$ make django-migrate`

* install certbot: https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx
```
# add-apt-repository ppa:certbot/certbot
# apt-get install python-certbot-nginx 
# certbot --nginx
```
* modify `/etc/nginx/sites-enabled/default` to look something like this:
```
upstream django {
    server unix:///home/gijs/buis/buis/wsgi.sock;
}


server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /var/www/html;
    index index.html index.htm index.nginx-debian.html;
    server_name _;

    location / {
        try_files $uri $uri/ =404;
    }
}

server {
    server_name demo.pythonic.nl;

    location /static {
        alias /home/gijs/buis/static;
    }

    location / {
        uwsgi_pass  django;
        include     /home/gijs/buis/buis/uwsgi_params;
    }

    listen [::]:443 ssl ipv6only=on;
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/demo.pythonic.nl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/demo.pythonic.nl/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = demo.pythonic.nl) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    listen [::]:80;
    server_name demo.pythonic.nl;
    return 404;
}
```
