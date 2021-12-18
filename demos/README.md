# Demos

This folder contains some example programs.

For the examples to work a remote proxy must be configured
to present the URLs as part of a single domain.

For example, if the host was `example.com`:

- example_auth_server serves on http://localhost:10001/auth/api which should be mapped to https://example.com/auth/api
- example-auth-ui serves on http://localhost:10002/auth/ui which should be mapped to https://example.com/auth/ui
- example_api_server serves on http://localhost:10010/example/api which should be mapped to https://example.com/example/api
- example-client-ui-simple/dashboard serves on http://localhost:10011/example/ui which should be mapped to https://example.com/example/ui

To try the demos, configure the reverse proxy (see below for an `haproxy` configuration),
then start all the servers (choose either the simple or dashboard client ui).
Then browse to https://example.com/example/ui (where `example.com` is your host).

Initially it will redirect to a login screen (try `tom@example.com` with the password `foo`).
On successful authentication the page gets redirected back to where you started, but with
an authentication cookie.

The servers are configured to renew tokens after a minute, and require re-authentication after two minutes.

## haproxy config

The following `haproxy` configuration sets up the path forwarding.
It requires an haproxy certificate chain.

```
global
	log /dev/log	local0
	log /dev/log	local1 notice
	chroot /var/lib/haproxy
	stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners
	stats timeout 30s
	user haproxy
	group haproxy
	daemon

	# Default SSL material locations
	ca-base /etc/ssl/certs
	crt-base /etc/ssl/private

	# See: https://ssl-config.mozilla.org/#server=haproxy&server-version=2.0.3&config=intermediate
	ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384
	ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
	ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets

	tune.ssl.default-dh-param 2048

defaults
	log	global
	mode	http
	option	httplog
	option	dontlognull
	timeout connect 5s
	timeout client  50s
	timeout server  50s
	timeout tunnel 1h
	timeout client-fin 5s
	errorfile 400 /etc/haproxy/errors/400.http
	errorfile 403 /etc/haproxy/errors/403.http
	errorfile 408 /etc/haproxy/errors/408.http
	errorfile 500 /etc/haproxy/errors/500.http
	errorfile 502 /etc/haproxy/errors/502.http
	errorfile 503 /etc/haproxy/errors/503.http
	errorfile 504 /etc/haproxy/errors/504.http

listen  stats
	bind *:9999
	stats enable
	stats hide-version
	stats uri /stats
	stats auth admin:admin

frontend www-http
	bind *:80
	option forwardfor

	redirect scheme https code 301 if !{ ssl_fc }

frontend www-https
	bind *:443 ssl crt /etc/haproxy/haproxy.pem alpn h2,http/1.1
	option forwardfor
	http-request add-header X-Forwarded-Proto https

	# Auth api on /auth/api
	acl is_auth_api_url path_beg /auth/api
	use_backend auth-api-server-http if is_auth_api_url

	# Auth ui on /auth/ui
	acl is_auth_ui_url path_beg /auth/ui
	use_backend auth-ui-server-http if is_auth_ui_url

	acl is_example_api_url path_beg /example/api
	use_backend example-api-server-http if is_example_api_url

	acl is_example_ui_url path_beg /example/ui
	use_backend example-ui-server-http if is_example_ui_url

backend auth-api-server-http
	balance roundrobin
	mode http
	http-request add-header X-Forwarded-Proto https
	server auth-api-01 127.0.0.1:10000 proto h2

backend auth-ui-server-http
	balance roundrobin
	mode http
	http-request add-header X-Forwarded-Proto https
	server auth-ui-01 127.0.0.1:10001

backend example-api-server-http
	balance roundrobin
	mode http
	http-request add-header X-Forwarded-Proto https
	server example-api-01 127.0.0.1:10010 proto h2

backend example-ui-server-http
	balance roundrobin
	mode http
	http-request add-header X-Forwarded-Proto https
	server example-ui-01 127.0.0.1:10011
```
