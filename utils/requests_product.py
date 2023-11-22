import requests
import urllib.parse

file = 'utils/headers'
header = {}
with open(file, 'r') as read:
    is_end = True
    curr_header = ''
    for line in read.readlines():
        line = line.strip()
        if line.startswith('POST') or line.startswith('GET'):
            header[line] = {}
            curr_header = line
            is_end = False
        elif not line:
            is_end = True
        elif not is_end:
            x = line.split(':', 1)
            # if x[0] == 'Cookie':
            #     continue
            try:
                header[curr_header][x[0]] = x[1].strip()
            except:
                print(x[0])


def get_product(product):
    product = urllib.parse.quote(product)

    with requests.session() as s:
        url = "https://kaspi.kz/shop/ab/tests/script-cookie?ui=DESKTOP&tg=none"
        response = s.get(url, headers=header['GET /shop/ab/tests/script-cookie?ui=DESKTOP&tg=none HTTP/1.1'])

        if response.status_code != 200:
            print(f"Failed to retrieve the page. \nURL: {url} \nStatus code: {response.status_code}")
            return None

        url = 'https://kaspi.kz/yml/product-view/pl/filters?text='+product+'&page=0&all=false&fl=true&ui=d&q=%3AavailableInZones%3AMagnum_ZONE1&i=-1&c=750000000'    
        response = s.get(url, headers=header['GET /yml/product-view/pl/filters?text=sony%20wh-1000xm&page=0&all=false&fl=true&ui=d&q=%3AavailableInZones%3AMagnum_ZONE1&i=-1&c=750000000 HTTP/1.1'])
        if response.status_code == 200:
            json_data = response.json()
            # print(len(json_data['data']['cards'])) #priceFormatted, unitPrice, unitSalePrice, title, shopLink, previewImages[0]['medium']
            # for data in json_data['data']['cards']:
            #     print(f'''title: {data["title"]} 
            #         \nunitPrice: {data["unitPrice"]} 
            #         \nunitSalePrice: {data["unitSalePrice"]} 
            #         \npriceFormatted: {data["priceFormatted"]} 
            #         \n shopLink: {data["shopLink"]} 
            #         \npreviewImages[0]["medium"] : {data["previewImages"][0]["medium"]}  
            #         ''')
            #     print(50*'-')
            return json_data['data']['cards']
        else:
            print(f"Failed to retrieve the page. \nURL: {url} \nStatus code: {response.status_code}")
            return None

# print(get_product('iphone'))