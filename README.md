# Krishna
A simplistic distributed bus tracking system. Built on top pf RTI DDS middleware. A WSU CPTS464 project.

## Setup
Krishna is the repository name for WSU's CPTS464 class project under Prof. Dave Bakken. I built this on using RTI's DDS middleware and Python. 

To use RTI's python middleware. Install with pip \
`$ pip3 install rticonnextdds_connector`

More on RTI's DDS connector [here](https://github.com/rticommunity/rticonnextdds-connector-py)
## Run

1. Run Publisher.py \
`$ python3 Publisher.py`

2. Run OperatorSubscriber.py \
`$ python3 OperatorSubscriber.py`

3. Run User.py \
`$ python3 User.py`
