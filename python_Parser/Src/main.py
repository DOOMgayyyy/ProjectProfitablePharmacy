import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
}

def get_product_data(url):
    # Получаем HTML страницы
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {'error': f'Failed to load page, status code: {response.status_code}'}
    
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # Извлекаем ID товара
    product_id = None
    product_container = soup.find(class_='js-product')
    if product_container and product_container.has_attr('data-product-id'):
        product_id = product_container['data-product-id']
    else:
        # Альтернативный поиск ID в скриптах
        script_tag = soup.find('script', string=lambda t: t and 'productId' in str(t))
        if script_tag:
            match = re.search(r'productId\s*=\s*(\d+)', str(script_tag))
            if match:
                product_id = match.group(1)
    
    if not product_id:
        return {'error': 'Product ID not found'}

    # Извлекаем название
    title = soup.find('h1', class_='product-card__title')
    title = title.text.strip() if title else 'Название не найдено'
    
    # Извлекаем изображение
    image_url = None 
    image_container = soup.find('img', class_='product-card__image')
    if image_container and 'src' in image_container.attrs:
        image_url = image_container['src']
    else:
        meta_og_image = soup.find('meta', property='og:image')
        if meta_og_image and meta_og_image.get('content'):
            image_url = meta_og_image['content']

    # Извлекаем цену - новый подход
    price = None
    price_container = soup.find('div', class_='product-card__price')
    
    if price_container:
        # Удаляем дочерние элементы (старая цена)
        for child in price_container.find_all(class_='product-card__price-old'):
            child.decompose()
        
        # Извлекаем основной текст
        price_text = price_container.get_text(strip=True)
        # Удаляем всё, кроме цифр
        price = re.sub(r'[^\d]', '', price_text)
    
    # Если не нашли - альтернативный метод
    if not price:
        price_element = soup.find('meta', itemprop='price')
        if price_element and price_element.get('content'):
            price = price_element['content']

    # Извлекаем список аптек
    drugstores = []
    store_list = soup.find('div', class_='store-list')
    
    if store_list:
        store_items = store_list.find_all('div', class_='store-list__item')
        
        for item in store_items:
            store_id = item.get('data-store-id', '')
            name = item.find('div', class_='store-list__name')
            address = item.find('div', class_='store-list__address')
            quantity = item.find('div', class_='store-list__quantity')
            status = item.find('div', class_='store-list__status')
            
            # Обработка статуса
            status_text = 'В наличии'
            if status and 'store-list__status_empty' in status.get('class', []):
                status_text = 'Нет в наличии'
            
            drugstore = {
                'id': store_id,
                'name': name.text.strip() if name else '',
                'address': address.text.strip() if address else '',
                'quantity': quantity.text.strip() if quantity else '0',
                'status': status_text
            }
            drugstores.append(drugstore)

    # Формирование результата
    result = {
        'title': title,
        'image_url': image_url,
        'price': price,
        'drugstores': drugstores,
        'product_id': product_id
    }

    return result

# URL товара
url = 'https://gosapteka18.ru/catalog/rengalin_tab_d_rassas_20.html'

# Получаем данные
result = get_product_data(url)
print(json.dumps(result, indent=2, ensure_ascii=False))