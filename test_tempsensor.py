import Adafruit_DHT
s = Adafruit_DHT.AM2302
p = 15
fa_code, color  = '', ''
result = {}
humidity, temperature = Adafruit_DHT.read_retry(s,p)
print(humidity, temperature)
