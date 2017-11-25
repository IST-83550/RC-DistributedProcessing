## PREREQUISITES:

python (version 2.7.9) executable as:
'> python'

## PROJECT CODE ORGANIZATION:

Each individual component of the project is in a separate directory, to provide for better
organization and make it easier to migrate any specific component to a different machine

## RUN THE CODE:

#From the main directory:

CS:

> python CS/CS.py [-p CSport]

WS:

> python WS/WS.py PTC1 … PTCn [-p WSport] [-n CSname] [-e CSport]

user:

> python user/user.py [-n CSname] [-p CSport]

#Alternatively:

CS:

> cd CS
> python CS.py [-p CSport]

WS:

> cd WS
> python WS.py PTC1 … PTCn [-p WSport] [-n CSname] [-e CSport]

user:

> cd user
> python user.py [-n CSname] [-p CSport]