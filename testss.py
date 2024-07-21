from datetime import date , datetime , timedelta

h = datetime.now()
print(h)
f = date.today()
print(f)
x = f - timedelta(days=1)
print(x)

y = h - timedelta(hours=4 , days=1)
print(y)
