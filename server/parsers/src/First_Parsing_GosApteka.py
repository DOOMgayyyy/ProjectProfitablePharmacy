import re
from playwright.sync_api import sync_playwright

class First_Parsing_GosApteka:
  def __init__(self):
    #указываем ссылку ан нашу целевую страницу
    self.link  = "https://gosapteka.ru/"

  def getCategories(self):
    #задаём сокращённое обращение к функции 
    with sync_playwright() as p:
      # указываем, нужный браузер для использования кодом
      browser = p.chromium.launch(headless=False)
      # для работы с ссылкой открываем новую страницу
      page = browser.new_page()
      # получаем данные по ссылке тк код синхрпонный ждём пока странница полностью прогрузится
      page.goto(self.link)
      # получаем содержимое внутри интересующего нас div 
      menu = page.locator("div.catalog_sub_menu")
      # обращаемся к более конкретным подкатегориям и получаем a элемент содержащий в себе и ссылку на категорю и русифицированное название
      links = page.locator("div.sub_menu_item a")
      # перебираем все получившиеся ответы по их количеству
      for i in range(links.count()):
        # получаем содержание поля a название
        a = links.nth(i)
        # выводим полученный результат через оединения текста и ссылки из её блока
        print(a.inner_text().strip(), a.get_attribute("href"))
      browser.close()