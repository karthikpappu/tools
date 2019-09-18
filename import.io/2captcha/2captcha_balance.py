import urllib.request

def balance(key):
    url = 'https://2captcha.com/res.php?key='+key+'&action=getbalance'
    f = urllib.request.urlopen(url)
    b = float(f.read().decode('utf-8'))
    return b

b = balance('eeb1ed6ba9bffdf874ccf3e9373e26b3')
print(b)

