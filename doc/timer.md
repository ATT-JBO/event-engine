
# timer Module


## timer.Timer Objects



### __init__ 

```Python
__init__(self, context, name, connection=None)
``` 

Create a new timer object

_parameters:_

- `runAt:` initial time out to run the timer at, when it is first created/setup
- `context:` the resource object in which context that the timer is activated
- `name:` the name of the timer, has to be unique within the specified context. 

##### `TimerEndPoint` 


### current 

```Python
current()
``` 

get the timer that triggered the current activity


_returns_: 

### getTopicStr 

```Python
getTopicStr(self)
``` 

renders 1 or more topic strings for the current object. Always returns a list 

### getTopics 

```Python
getTopics(self, divider=None, wildcard=None)
``` 

get the topics that should  the broker should monitor for this object

_parameters:_

- `divider:` the divider to use in the topic, None to use the default of the current self.context (att.Client)
- `wildcard:` same as divider bur for wildcards.


_returns_: 

### id 



### set 

```Python
set(self, delay)
``` 

start the timer and let it go off in 'value' amount of seconds.
If the timer was already running, it will be restarted.

_parameters:_

- delay:


_returns_: True upon success, false otherwise. Raises exception upon serious problems. 
