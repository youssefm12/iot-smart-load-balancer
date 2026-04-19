import urllib.request
req = urllib.request.Request(
    'http://localhost:8086/api/v2/write?org=iot-org&bucket=server-metrics&precision=s',
    data=b"server_metrics,server_id=test cpu=50.0 1713500000",
    headers={'Authorization': 'Token my-super-secret-auth-token'}
)
print(urllib.request.urlopen(req).read())
