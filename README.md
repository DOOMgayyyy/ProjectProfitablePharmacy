# Технологический стек
- Backend:Node Express
- Frontend: React
- DataBase: Postgres
- Parsers: Playwright, Selenium, Scrapy, Bs4
## На расмотрении
- ORM Prisma
- Tailwind (для него Flowbite, HeroUI)


Как сделать без этой мороки

Сделай себе короткую команду в PowerShell на текущую сессию:

powershell
function vpy { .\.venv\Scripts\python.exe @args }

После этого вместо простыни ты пишешь:

powershell
vpy -m pip install scrapy
vpy -m scrapy startproject parsers src
vpy -m scrapy crawl gosapteka


python -m playwright install --with-deps — установит браузеры и сразу попытается докачать недостающие системные зависимости (актуально для Linux/Ubuntu).