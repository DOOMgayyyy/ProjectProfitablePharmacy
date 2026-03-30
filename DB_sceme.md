**prices**
| name | type | comment | Description |
|-|-|-|-|
| id | integer | primary key | Уникальный id ценника |
| price | DOUBLE | | цена позиции|
| pharmancys_id | integer | foreign key | id аптеки откуда цена лекарства |
| medecines_id | integer | foreign key | id лекарства  |
| date_parse | date |  | время последнего парсинга |
| medecine_url | string |  | юрл на конкретное лекарство |

**pharmancys**
| name | type | comment | Description |
|-|-|-|-|
| id | integer | primary key | Уникальный id аптеки |
| name | string | unique | название атеки  |
| url | string | unique | url на сайт конкретной аптеки |

**medicines**
| name | type | comment | Description |
|-|-|-|-|
| id | integer | primary key | Уникальный id лекарства |
| name | string |  | название лекарства  |
| normalize_name | string |  | транслитовое имя |
| description | string |  | описание лекарства |
| manufacturer | string |  | производитель лекарства |
| categories | string | | категория для лекарств |

таблица посвящена различным категориям, откуда можно начинать парсинг
**categories**
| name | type | comment | Description |
|-|-|-|-|
| id | integer | primary key | Уникальный id лекарства |
| categories | string | | категория для лекарств |
| pharmancys_id | foreign key | | id аптеки откуда спаршена категория |
