server {
        listen 80;
        server_name example.com;

        access_log /var/log/nginx/example.com.access.log;
        error_log /var/log/nginx/example.com.error.log;

        root /var/www/example.com;
        index index.php;

        #browse folders if no index file
        autoindex on;

        # serve static files directly
        location ~* \.(jpg|jpeg|gif|css|png|js|ico|html)$ {
                access_log off;
                expires max;
        }

	# removes trailing slashes (prevents SEO duplicate content issues)
        if (!-d $request_filename)
        {
                rewrite ^/(.+)/$ /$1 permanent;
        }

	# removes trailing "index" from all controllers
        if ($request_uri ~* index/?$)
        {
                rewrite ^/(.*)/index/?$ /$1 permanent;
        }

	# unless the request is for a valid file (image, js, css, etc.), send to bootstrap
        if (!-e $request_filename)
        {
                rewrite ^/(.*)$ /index.php?/$1 last;
                break;
        }

	location ~ \.php$ {
                root   /var/www/example.com;
                fastcgi_pass   unix:/var/run/php-fpm/php-fpm.sock;
                fastcgi_index  index.php;
                fastcgi_param  QUERY_STRING	  $query_string;
                fastcgi_param  REQUEST_METHOD     $request_method;
                fastcgi_param  CONTENT_TYPE	  $content_type;
                fastcgi_param  CONTENT_LENGTH     $content_length;

                fastcgi_param  SCRIPT_NAME        $fastcgi_script_name;
                fastcgi_param  SCRIPT_FILENAME    $document_root$fastcgi_script_name;
                fastcgi_param  REQUEST_URI        $request_uri;
                fastcgi_param  DOCUMENT_URI	  $document_uri;
                fastcgi_param  DOCUMENT_ROOT	  $document_root;
                fastcgi_param  SERVER_PROTOCOL    $server_protocol;

                fastcgi_param  GATEWAY_INTERFACE  CGI/1.1;
                fastcgi_param  SERVER_SOFTWARE    nginx;

                fastcgi_param  REMOTE_ADDR        $remote_addr;
                fastcgi_param  REMOTE_PORT        $remote_port;
                fastcgi_param  SERVER_ADDR        $server_addr;
                fastcgi_param  SERVER_PORT        $server_port;
                fastcgi_param  SERVER_NAME        $server_name;
                include        fastcgi_params;
        }
}