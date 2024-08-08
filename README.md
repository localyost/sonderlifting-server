# Sonderlifting Webserver

Documentation for entire project setup from scratch

## Prerequisites:
- This has been tested on a Raspberry PI 4 with a 32 gb MicroSD
- PI must be connected to your router over Ethernet, **NOT WIFI!** This is important!
- Access to your router

## **Step 1:** Install Raspberry PI OS 

- Download and Install the [Raspberry PI Imager](https://www.raspberrypi.com/software/)
- Follow instructions to Install **Raspberry PI OS 64 bit**
- Make sure you enable SSH
- again, **DO NOT** configure WIFI.
- flash the OS to your SSD
- insert SSD and start the PI
- Connect over ethernet to your router and ensure you can connect over SSH

## **Step 2:** Configure PI as a WIFI access point
OS is flashed and you have connected over SSH
###  As always: ``sudo apt update apt upgrade``
###  Install necessary packages:
  - Install DNS: 
    - ``sudo apt install dnsmasq``
  - Install access point: 
    - ``sudo apt install hostapd``
  - Install DHCP server: 
    - ``sudo apt install dhcpcd5``
  - Install iptables: 
    - ``sudo apt install iptables``
### Temporarily stop services: 
  - ``sudo systemctl stop dnsmasq``
  - ``sudo systemctl stop hostapd``
  - ``sudo systemctl stop dhcpcd``
### Configure a static IP for the WIFI interface: 
  - ``sudo nano /etc/dhcpcd.conf`` file should already be populated!
  - add the following to the end of the file:

```
    interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
```

### Configure DNS:
  - Backup the existing DNS config file: 
    - ``sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig``
  - Create a new configuration file: 
    - ``sudo nano /etc/dnsmasq.conf``
  - add the following:

```
    interface=wlan0
    dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```

### Configure WIFI Access Point: 
- Create a new config for hostapd file: 
  - ``sudo nano /etc/hostapd/hostapd.conf``
- Add (**Note WIFI SSID and PASSWORD!**): 

```
    interface=wlan0
    driver=nl80211
    ssid={{YOUR_SSID}}
    hw_mode=g
    channel=7
    wmm_enabled=0
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_passphrase={{YOUR_PASSWORD}}
    wpa_key_mgmt=WPA-PSK
    rsn_pairwise=CCMP
```

- Edit the hostapd default file to point to this configuration file:
  - open:
    - ``sudo nano /etc/default/hostapd``
  - change: 
    - ``DAEMON_CONF="/etc/hostapd/hostapd.conf"``

### Enable IP Forwarding:
- ``sudo nano /etc/sysctl.conf``
- uncomment: 
  - ``net.ipv4.ip_forward=1``
- apply changed: 
  - ``sudo sysctl -p``

### Add a new NAT rule to iptables: 
 for external access to Internet.
- add new NAT Rule: 
  - ``sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE``
- Save the new rule: 
  - ``sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"``
- Edit the rc.local file to restore this rule on boot: 
  - ``sudo nano /etc/rc.local``
- Add the following line just above exit 0: 
  - ``iptables-restore < /etc/iptables.ipv4.nat``

### Unmask, restart and enable services:
 
``hostapd`` needs to be unmasked in order for the access point to work. 
Additionally, ``hostapd`` and ``dnsmasq`` need to be enabled so they start after reboot.

```
    sudo systemctl unmask hostapd
    sudo systemctl start hostapd
    sudo systemctl start dnsmasq
    sudo systemctl start dhcpcd
    sudo systemctl enable hostapd
    sudo systemctl enable dnsmasq
```

### Test Connection

In your WIFI settings on you computer, you now should be able to see the SSID you created. 
Connect to the WIFI access point using the password you created. Internet access should also work.

###  Ensure hostapd Starts After the Network Interface

hostapd trys to start before the wlan0 interface is ready. 
If you reboot the PI you won't find your access point until you run ``sudo systemctl restart hostapd``.
This needs to be fixed. We adjust the systemd service dependencies to ensure ``hostapd`` starts after the network interface is up. 

- Create a directory for the override file: 
  - ``sudo mkdir -p /etc/systemd/system/hostapd.service.d``
- Create an override.conf file: 
  - ``sudo nano /etc/systemd/system/hostapd.service.d/override.conf``
- Add to file:

```
    [Unit] 
    After=network-online.target 
    Wants=network-online.target
```
- Reload the systemd daemon to apply the changes: 
  - ``sudo systemctl daemon-reload``
- Reboot and test
  - ``sudo reboot``

You should, hopefully, now see your SSID and be able to connect after restart!

## **Step 3:** Configure DNS

In the last section, we assigned the IP Address: ``192.168.4.1`` to our ``wlan0`` interface, and, as the gateway to the ``DHCP`` Server.
We now need to point custom domain names to this IP. When the user connects to the WIFI they will be able to access these URLS.
DNS entries can, of course, be what ever you want, but keep them in mind for later!

- Edit the dnsmasq config file: 
  - ``sudo nano /etc/dnsmasq.conf``
- Add DNS entries 
```
  address=/sonderlifting/192.168.4.1
  address=/judge.sonderlifting/192.168.4.1
  address=/display.sonderlifting/192.168.4.1
  address=/api.sonderlifting/192.168.4.1
```
- Restart dnsmasq to apply changes:
  - ``sudo systemctl restart dnsmasq``

## **Step 4:** NGINX 

We have access to the WIFI Hotspot and our domains are configured. We now need to install NGINX.
This will serve our two frontends and act as a reverse proxy for the webserver.

### Install NGINX
 - Install 
   - ``sudo apt install nginx``
 - NGINX should start automatically 
   - ``sudo systemctl status nginx``
   - ``sudo systemctl start nginx`` (if not started)
 - enable NGINX to start on boot (should actually already work but to it anyway)
   - ``sudo systemctl enable nginx``

### Test

Connect to the WIFI access point and in a browser just open ``http://sonderlifting``. 
You should see the **Welcome to nginx!** default page.

### Configure Frontends

Naming is, of course, your decision. 
These steps apply to all frontends you want to add just repeat the process.

- Create a folder to place our application(s):
  - ``sudo nano /etc/nginx/sites-available/judge.sonderlifting``
- Add:
```
  server {
    listen 80;
    
    #must match what you configured in the DNS config!
    server_name judge.sonderlifting; 

    root /var/www/judge.sonderlifting;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
 ```
- Create directory for the web content
  - ``sudo mkdir -p /var/www/judge.sonderlifting``

- Set permissions for the document root:
```
    sudo chown -R www-data:www-data /var/www/judge.sonderlifting
    sudo chmod -R 755 /var/www/judge.sonderlifting
```
- Create a sample index.html file:
  - ``sudo nano /var/www/judge.sonderlifting/index.html``
- Add some content (for testing)"
```
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to judge.sonderlifting!</title>
</head>
<body>
    <h1>Success! The judge.sonderlifting server block is working!</h1>
</body>
</html>
```
- Enable the server block by creating a symbolic link:
  - ``sudo ln -s /etc/nginx/sites-available/judge.sonderlifting /etc/nginx/sites-enabled/
``
- Test the Nginx configuration for syntax errors:
  - ``sudo nginx -t``
- Restart Nginx to apply the changes:
  - ``sudo systemctl restart nginx``

### Test

Still connected to the access point Go to ``http://judge.sonderlifting/`` and you should see your content

### Configure Reverse Proxy for Backend

The backend server is also behind the NGINX Proxy. We need to configure this. 
For the backend API we have chosen the domain ``api.sonderlifting```.

- Create a configuration file:
  - ``sudo nano /etc/nginx/sites-available/api.sonderlifting``
- Enable the server block by creating a symbolic link:
  - ``sudo ln -s /etc/nginx/sites-available/judge.sonderlifting /etc/nginx/sites-enabled/``
- Add the reverse proxy configuration:
```
  server {
    listen 80;
    server_name api.sonderlifting;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
    
    location /ws/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'Upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
- Test the Nginx configuration for syntax errors:
  - ``sudo nginx -t``
- Restart Nginx to apply the changes:
  - ``sudo systemctl restart nginx``

## **Step 5:** Prepare FTP server for deployment 

For deployment to the PI we can use FTP 

### Installation and configuration:
- Install vsftpd package:
  - ``sudo apt install vsftpd``
- Create a config:
  - ``sudo nano /etc/vsftpd.conf``
- Uncomment or add the following lines (search with ctrl+W):
```
    anonymous_enable=NO
    local_enable=YES
    write_enable=YES
    local_umask=022
    chroot_local_user=YES
    user_sub_token=$USER
    # This is where our content will be served from
    local_root=/var/www
    allow_writeable_chroot=YES #TODO See what best practice for this is 
```
- Apply permissions: (#TODO: See what best practice for this is)
  ```
    sudo chown -R www-data:www-data /var/www
    sudo chmod -R 775 /var/www
    sudo chown -R $USER /var/www
  ```
- Restart FTP: 
  - ``sudo service vsftpd restart``

### Test:

Open filezilla connect to the PI. If you created some content in ``/var/www`` you will be able to see those files.

## **Step 6:** Deploy Backend

We will place our content in the ``/var/www/srv`` folder. 
- Create a directory for the backend
  - ``sudo mkdir srv``
- Over FTP add the backend files
  - ``app.py`` and ``requirements.txt``  

### Install Python libs
- in the SSH create a python virtual environment
  - ``python3 -m venv venv``
- access the environment:
  - ``source venv/bin/activate`` 
- Install the libs from the ``requirements.txt``
  - ``pip install -r requirements.txt``
### Start server and test
- Start the server:
  - ``flask run``
- Verify locally (on the PI) that the "test" endpoint works
  - ``curl http://localhost:5000/test``
- Now verify on your machine (make sure you are still connected to the WIFI!)
  - ``curl http://api.sonderlifting/test``

## **Step 7:** Build and deploy frontends

- build app. There are two (Make sure URLS are correct!)
  - ``flutter build web --release``
  - on FTP move files from ``build/web`` to appropriate app content destination
  - test
  - i hate documentation
    
