<b>Python plugin for Domoticz with Sonos</b>

With this plugin you can control your Sonos speakers with Domoticz and send TTS strings to it.

<b>Keep in mind you will need the latest beta version of Domoticz</b>
<hr/>

<b>Installation Raspberry PI</b>

For this plugin to work you need to install the http sonos api from Jimmy Shimizu.<br/>
You can find it here: https://github.com/jishi/node-sonos-http-api

After the installation I noticed I needed to update my nodejs on my pi. For this I did the following:
```bash
sudo npm cache clean -f
sudo npm install -g n
sudo n stable
```

After you have installed and tested the http sonos api you can install the Domoticz plugin
```bash
cd domoticz/plugins
git clone https://github.com/rvdvoorde/domoticz-sonos.git
```
After the installation restart Domoticz
```bash
sudo systemctl restart domoticz
```

You can now add the Sonos hardware in Domoticz


