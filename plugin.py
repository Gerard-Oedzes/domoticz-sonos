##           Sonos Plugin
##
##           Author:         Raymond Van de Voorde
##           Version:        1.0.1
##           Last modified:  05-04-2017
##

"""
<plugin key="domoticz-sonos" name="Sonos (With http api)" author="Wobbles" version="1.0.1" externallink="http://www.sonos.com/">
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1" />	
	<param field="Port" label="Port" width="10px" required="true" default="5005" />

        <param field="Mode1" label="Poll interval" width="100px" required="true" default=10 />        
        
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import json
import http.client

class BasePlugin:
    enabled = True

    Startup = True;
    isConnected = False
    SonosCount = 0
    LastCommand = ""
    Port = "5005"
    
    # HTTP headers
    Headers = {"Connection": "keep-alive", "Accept": "Content-Type: text/html; charset=UTF-8"}
    
    
    def __init__(self):        
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        # Connect and get all connected Sonos devices
        self.SendMessage("/zones")

        return

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Status, Description):
        Domoticz.Log("onConnect called")        
        
        self.isConnected = True;
        Domoticz.Send("", "GET", self.LastCommand, self.Headers)        

    def onMessage(self, Data, Status, Extra):
        Domoticz.Log("onMessage called")

        try:
            strData = Data.decode("utf-8", "ignore")
            Response = json.loads(strData)
        except:
            Domoticz.Error("Invalid data received!")
            return

        # First startup?
        if ( self.LastCommand == "/zones" and self.Startup ):            
            self.SonosCount = len(Response)
            Domoticz.Log("No. of Sonos devices detected: " + str(self.SonosCount))

            #Start adding new devices and set the status
            self.InitSonos(Response)
            self.Startup = False

        # Standard poll?
        elif ( self.LastCommand == "/zones" and self.Startup == False ):
            Domoticz.Debug("Handling /zone response")

        return

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        # Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)
        return

    def onDisconnect(self):
        Domoticz.Log("onDisconnect called")
        self.isConnected = False
        
    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        self.SendMessage("/zones")

    def SendMessage(self, command):
        if ( self.isConnected == False ):
            self.Port = Paramters["Port"]
            Domoticz.Transport(Transport="TCP/IP", Address=Parameters["Address"], Port=self.Port)
            Domoticz.Protocol("HTTP")        
            Domoticz.Connect()

            self.LastCommand = command
            Domoticz.Debug("Sending command: "+str(command))            
            return
        
            
        try:
            Domoticz.Send("", "GET", command, self.Headers)
        except:
            Domoticz.Debug("Failed to communicate to system at ip " + Parameters["Address"] + ". Command " + command )
            return False

        return True


    def InitSonos(self, jsonData):
        Domoticz.Debug("InitSonos called")

        for Sonos in (0, int(self.SonosCount)-1):
            try:
                Domoticz.Log("Sonos ID: " + str(Sonos))
                Name = jsonData[Sonos]["coordinator"]["roomName"]
                Value = jsonData[Sonos]["coordinator"]["state"]["volume"]
                Mute = jsonData[Sonos]["coordinator"]["state"]["mute"]
                State = jsonData[Sonos]["coordinator"]["state"]["playbackState"]
                
                Domoticz.Log("Adding Sonos " + Name)
            except:
                Domoticz.Error("Error adding Sonos " + Name)



        
    def GetValue(self, arr, sKey, defValue):
        try:
            if str(sKey) in arr:
                if ( str(arr[str(sKey)]).lower() == "none" ):
                    return defValue
                else:
                    return arr[str(sKey)]
            else:
                return defValue
        except:
            return defValue



        
global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Status, Description):
    global _plugin
    _plugin.onConnect(Status, Description)

def onMessage(Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect():
    global _plugin
    _plugin.onDisconnect()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def UpdateDevice(Unit, nValue, sValue, AlwaysUpdate=False):    
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if ((Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue) or (AlwaysUpdate == True)):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

