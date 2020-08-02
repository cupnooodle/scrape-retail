from bs4 import BeautifulSoup
import requests
import re
import smtplib
import ssl
import datetime
import base64

items = ["https://jbhifi.com.au/products/google-chromecast-charcoal-grey", "https://addictedtoaudio.com.au/products/sennheiser-hd5xx", "https://addictedtoaudio.com.au/products/sennheiser-hd6xx-open-back-headphones"]
originalPrice = [59, 299, 399]

for x in items:
    timestamp = datetime.datetime.now()

    # Filter out domain name to determine which search criteria
    try:
        domain = re.search("https://(.+?)\.", x).group(1)
    except AttributeError:
        print("Could not extrapolate domain")
        continue

    # Request http session parse contents through Beautiful soup
    page = requests.get(x)
    source = str(BeautifulSoup(page.text, 'html.parser'))
    prod_name = ''
    price = 0

    # Extract data
    if domain == "jbhifi":
        try:
            prod_name = re.search('%s(.*)%s' % ('name">', "</h1>"), source).group(1)
        except AttributeError:
            print("Could not find product name for JBHifi product")
            continue
        try:
            price = float(re.search('%s(.*)%s' % ("</sup>", "</span>"), source).group(1))
        except AttributeError:
            print("Could not find price for JBHifi product")
            continue

    if domain == "addictedtoaudio":
        try:
            prod_name = re.search('%s(.*)%s' % ('title heading h1">', "</h1>"), source).group(1)
        except AttributeError:
            print("Could not find product name for Addictedtoaudio product")
            continue
        try:
            price = re.search('%s(.*)%s' % ('<span class=\"price', "</span>"), source).group(1)
        except AttributeError:
            print("Could not find price for Addictedtoaudio product")
            continue
        price = float(re.sub('\D', '', price))

    if price < originalPrice[items.index(x)]:
        # SMTP configuration and build email message
        message = "Subject: " + prod_name + " on sale at " + domain + " for $" + "%.2f" % round(price, 2)

        f = open("scrapecred.ini", "r")
        if f.mode == 'r':
            serverAddress = str(base64.b64decode(f.readline()))[2:-1]
            sendFrom = str(base64.b64decode(f.readline()))[2:-1]
            sendTo = str(base64.b64decode(f.readline()))[2:-1]
            pwd = str(base64.b64decode(f.readline()))[2:-1]
        f.close()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL((serverAddress), 465, context=context) as server:
            server.login(sendFrom, pwd)
            server.sendmail(sendFrom, sendTo, message)
        print('[' + timestamp.strftime("%c") + "] Sale found!")
    else:
        print('[' + timestamp.strftime("%c") + "] No sale")
print("----------------------------------")


