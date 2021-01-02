# TelegramBotCoronaAir

This is the Telegram Bot for the CoronaAir project

Requirements (tested with version):

- [x] pandas==1.2.0

- [x] pyzbar==0.1.8 #Info: You need a lib named "zbar" too

- [x] SQLAlchemy==1.3.22

- [x] numpy==1.19.4

- [x] python_telegram_bot==13.1

- [x] requests==2.21.0

- [x] matplotlib==3.3.3

- [x] seaborn==0.11.1

- [x] Pillow==8.0.1

- [x] telegram==0.0.1
  
  

I use maradb as database. The system is using SQLAlchemy, supported databases should not need a change in code. Need Tables:

# chats

| Field   | Type                | Null | Key | Default | Extra          |
| ------- | ------------------- | ---- | --- | ------- | -------------- |
| id      | int(10) unsigned    | NO   | PRI | NULL    | auto_increment |
| chat_id | bigint(15) unsigned | NO   | MUL | NULL    |                |
| state   | varchar(50)         | NO   |     | NULL    |                |
| sensor  | bigint(15) unsigned | NO   |     | NULL    |                |
| start   | varchar(45)         | NO   |     | NULL    |                |

# sgp_30

| Field       | Type                | Null | Key | Default | Extra          |
| ----------- | ------------------- | ---- | --- | ------- | -------------- |
| id          | int(10) unsigned    | NO   | PRI | NULL    | auto_increment |
| sensor_id   | bigint(16) unsigned | NO   |     | NULL    |                |
| temperature | float               | NO   |     | NULL    |                |
| eCO2        | int(5)              | NO   |     | NULL    |                |
| raw_Ethanol | int(5)              | NO   |     | NULL    |                |
| raw_H2      | int(5)              | NO   |     | NULL    |                |
| pressure    | float               | NO   |     | NULL    |                |
| humidity    | float               | NO   |     | NULL    |                |
| TVOC        | int(5)              | NO   |     | NULL    |                |
| timestamp   | varchar(45)         | NO   |     | NULL    |                |



In the **coronaAirBot.service** You have to replace the:

1. TOKEN: You have to get your own Telegram TOKEN please refer: [Telegram Bot API](https://core.telegram.org/bots/api)

2. DB_URL: You have to set your Databse URI, please refer: [Engine Configuration](https://docs.sqlalchemy.org/en/13/core/engines.html)
