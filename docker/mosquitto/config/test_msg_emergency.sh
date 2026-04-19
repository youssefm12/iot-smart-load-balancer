mosquitto_pub -h localhost -t "servers/server1/metrics" -m '{"server_id":"server1","cpu":10.0,"ram":20.0,"network":50,"load_score":15.0,"timestamp":'$(date +%s)'}' -u iot_admin -P iot_secure_123
mosquitto_pub -h localhost -t "servers/server2/metrics" -m '{"server_id":"server2","cpu":99.5,"ram":99.5,"network":995,"load_score":99.5,"timestamp":'$(date +%s)'}' -u iot_admin -P iot_secure_123
