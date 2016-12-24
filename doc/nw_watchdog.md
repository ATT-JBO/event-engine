
# nw_watchdog Module


## nw_watchdog.Nw_Watchdog Objects



### __init__ 

```Python
__init__(self, client, device, assetName, on_failure)
``` 

create watchdog

_parameters:_

- `client:` The att_event_engine.Client object that provides a connection to the cloud.
- `device:` The name of the device that represents the watchdog.
- `on_failure:` a callback function: def on_failure(), called when the self-ping fails.
- `assetName:`  name of the asset that represents the watchdog-pin. 

### checkPing 

```Python
checkPing(self)
``` 

check if we need to resend a ping and if we received the previous ping in time 

### on_ping_received 

```Python
on_ping_received(self, value)
``` 

check if an incomming command was a ping from the watchdog


_returns_s: if the id was that of the watchdog.
		return type: bool 

### ping 

```Python
ping(self)
``` 

send a ping to the server 

### run 

```Python
run(self)
``` 

start the watchdog.


_returns_: 

### stop 

```Python
stop the thread.
``` 



_returns_: 
