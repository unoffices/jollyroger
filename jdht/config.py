
## Blowfish 
KEY = "superawesomesecretkeyfortestingpurposes1337"

## Socket const
PACKET_SIZE = 1024 # 65536 - IP datagram cap, 1500 MTU cap


# DHT const

## concunrency
ALPHA = 3  

## adress space - B
ADDRESS_SPACE = 160 

## max records stored per bucker
K = 20

## time after which key/value pair expires
T_EXPIRE = 86410

## after which an otherwise unaccessed bucket must be refreshed
T_REFRESH = 3600

## interval between replication event, when a node is required to publish its entire database
T_REPLICATE = 3600

## time after which original publisher must republish a key/value pair
T_REPUBLISH = 86400
