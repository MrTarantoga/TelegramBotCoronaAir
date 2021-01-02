from os import stat_result
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, cast
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import date, datetime, timedelta
Base = declarative_base()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Sensor_Value(Base):
    __tablename__ = "sgp_30"

    id          = Column(Integer, primary_key=True)
    temperature = Column(Float)
    eCO2        = Column(Integer)
    raw_Ethanol = Column(Integer)
    raw_H2      = Column(Integer)
    pressure    = Column(Float)
    humidity    = Column(Float)
    TVOC        = Column(Integer)
    sensor_id   = Column(Integer)
    timestamp   = Column(DateTime(timezone=True), default=func.now())

class chats(Base):
    __tablename__ = "chats"

    id          = Column(Integer, primary_key=True)
    start       = Column(DateTime(timezone=True), default=func.now())
    sensor      = Column(Integer)
    chat_id     = Column(Integer)
    state       = Column(String(50))


class DBConnection(object):
    def __init__(self, database_URL: str):
        self.database_URL = database_URL
        self.engine = create_engine(self.database_URL)

    def getPictureOfTimeSeries(self, start: datetime, end: datetime, sensor: int) -> list:
        session = sessionmaker(bind=self.engine)()
        query  = session.query(Sensor_Value).filter(Sensor_Value.sensor_id == sensor).filter(Sensor_Value.timestamp >= start).filter(Sensor_Value.timestamp <= end)
        data = query.all()
        retValue = list()
        for elem in data:
            retValue.append(
                {
                    "timestamp"  :  elem.timestamp,
                    "temperature":  elem.temperature,
                    "eCO2":         elem.eCO2,
                    "raw_Ethanol":  elem.raw_Ethanol,
                    "raw_H2"     :  elem.raw_H2,
                    "pressure"   :  elem.pressure,
                    "humidity"   :  elem.humidity,
                    "TVOC"       :  elem.TVOC
                }
            )
        session.close()
        return retValue

    def getDataRawH2(self, start: datetime, end: datetime, sensor: int):
        session = sessionmaker(bind=self.engine)()
        query  = session.query(Sensor_Value.timestamp, Sensor_Value.raw_H2).filter(Sensor_Value.sensor_id == sensor).filter(Sensor_Value.timestamp >= start).filter(Sensor_Value.timestamp <= end)
        data = query.all()
        retValue = list()
        for elem in data:
            retValue.append(
                {
                    "timestamp"  :  elem.timestamp,
                    "raw_H2"     :  elem.raw_H2
                }
            )
        session.close()
        return retValue

    def getDataRawEthanol(self, start: datetime, end: datetime, sensor: int):
        session = sessionmaker(bind=self.engine)()
        query  = session.query(Sensor_Value.timestamp, Sensor_Value.raw_Ethanol).filter(Sensor_Value.sensor_id == sensor).filter(Sensor_Value.timestamp >= start).filter(Sensor_Value.timestamp <= end)
        data = query.all()
        retValue = list()
        for elem in data:
            retValue.append(
                {
                    "timestamp"  :  elem.timestamp,
                    "raw_Ethanol":  elem.raw_Ethanol
                }
            )
        session.close()
        return retValue

    def getDataTVOC(self, start: datetime, end: datetime, sensor: int):
        session = sessionmaker(bind=self.engine)()
        query  = session.query(Sensor_Value.timestamp, Sensor_Value.TVOC).filter(Sensor_Value.sensor_id == sensor).filter(Sensor_Value.timestamp >= start).filter(Sensor_Value.timestamp <= end)
        data = query.all()
        retValue = list()
        for elem in data:
            retValue.append(
                {
                    "timestamp"  :  elem.timestamp,
                    "TVOC"       :  elem.TVOC
                }
            )
        session.close()
        return retValue

    def getLastTVOC(self):
        session = sessionmaker(bind=self.engine)()
        retValue  = session.query(Sensor_Value.TVOC).order_by(Sensor_Value.id.desc()).first()[0]
        session.close()
        return retValue
    
    def getLasteCO2(self, sensorID: int):
        session = sessionmaker(bind=self.engine)()
        retValue = session.query(Sensor_Value.eCO2).filter(Sensor_Value.sensor_id == sensorID).order_by(Sensor_Value.id.desc()).first()[0]
        session.close()
        return retValue

    def getDataTemperature(self, start: datetime, end: datetime, sensor: int):
        session = sessionmaker(bind=self.engine)()
        query  = session.query(Sensor_Value.timestamp, Sensor_Value.temperature).filter(Sensor_Value.sensor_id == sensor).filter(Sensor_Value.timestamp >= start).filter(Sensor_Value.timestamp <= end)
        data = query.all()
        retValue = list()
        for elem in data:
            retValue.append(
                {
                    "timestamp"  :  elem.timestamp,
                    "temperature":  elem.temperature
                }
            )
        session.close()
        return retValue


    def getDataHumidity(self, start: datetime, end: datetime, sensor: int):
        session = sessionmaker(bind=self.engine)()
        query  = session.query(Sensor_Value.timestamp, Sensor_Value.humidity).filter(Sensor_Value.sensor_id == sensor).filter(Sensor_Value.timestamp >= start).filter(Sensor_Value.timestamp <= end)
        data = query.all()
        retValue = list()
        for elem in data:
            retValue.append(
                {
                    "timestamp"  :  elem.timestamp,
                    "humidity"   :  elem.humidity
                }
            )
        session.close()
        return retValue


    def getDataeCO2(self, start: datetime, end: datetime, sensor: int):
        session = sessionmaker(bind=self.engine)()
        query  = session.query(Sensor_Value.timestamp, Sensor_Value.eCO2).filter(Sensor_Value.sensor_id == sensor).filter(Sensor_Value.timestamp >= start).filter(Sensor_Value.timestamp <= end)
        data = query.all()
        retValue = list()
        for elem in data:
            retValue.append(
                {
                    "timestamp"  :  elem.timestamp,
                    "eCO2"       :  elem.eCO2
                }
            )
        session.close()
        return retValue
    
    def getChatSession(self, chat_id: int):
        session = sessionmaker(bind=self.engine)()
        query = session.query(chats).filter(chats.chat_id == chat_id)
        data = query.all()
        retValue = list()
        for elem in data:
            retValue.append(
                {
                    "chat_id"  : elem.chat_id,
                    "sensor"   : elem.sensor,
                    "state"    : elem.state,
                    "start"    : elem.start
                })
        session.close()
        return retValue
    
    def modifyChatSession(self, chat_session: dict):
        session = sessionmaker(bind=self.engine)()

        if "state" in chat_session.keys():
            session.query(chats).filter(chats.chat_id == chat_session["chat_id"]).update({chats.state: chat_session["state"]})
        if "sensor" in chat_session.keys():
            session.query(chats).filter(chats.chat_id == chat_session["chat_id"]).update({chats.sensor: chat_session["sensor"]})

        session.query(chats).filter(chats.chat_id == chat_session["chat_id"]).update({chats.start: datetime.now()})


        session.commit()
        session.close()
    
    def createChatSession(self, chat_session: dict):
        session = sessionmaker(bind=self.engine)()
        new_chat = chats(
                    sensor  = chat_session["sensor"],
                    chat_id = chat_session["chat_id"],
                    state   = chat_session["state"]
        )
        session.add(new_chat)
        session.commit()
        session.close()
        
