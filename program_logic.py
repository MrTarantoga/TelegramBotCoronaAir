from PIL import Image
from pyzbar.pyzbar import decode
from io import BytesIO
from DBConnection import DBConnection
from datetime import datetime
from typing import Callable
from threading import Thread, Event
import time
from queue import Queue
from datetime import datetime, timedelta
from Picture import GetPictureOfeCO2
from base64 import b64encode


class State(object):
    def __init__(self, chat_id: int, db: DBConnection):
        self.state_id = str()
        self.chat_id = chat_id
        self.db = db
        self.message = str()
    
    def run(self, data):
        assert 0, "Define run"
    
    def nextState(self) -> str:
        assert 0, "Define next state"
    
class logIn(State):
    def __init__(self, chat_id: int, db: DBConnection):
        super().__init__(chat_id, db)
        self.state_id = "LogIn"

    def run(self, data: bytes):
        try:
            sensor_id = int(decode(Image.open(BytesIO(data)))[-1].data.decode("ascii"))
        except:
            self.next_State = "LogIn"
            self.message = "I'm sorry I could not recognize the qr code"
        else:
            elems = self.db.getChatSession(self.chat_id)
            self.next_State = "check exceed value"
            if len(elems) == 0:
                self.db.createChatSession({
                    "state": self.state_id,
                    "sensor": sensor_id,
                    "chat_id": self.chat_id
                })
            else:
                self.db.modifyChatSession({
                    "state":  self.next_State,
                    "sensor": sensor_id,
                    "chat_id": self.chat_id
                })
            self.message = "Log-In successful"
            
    def nextState(self) -> str:            
        return self.next_State

class checkExceedValue(State):
    def __init__(self, chat_id: int, db: DBConnection):
        super().__init__(chat_id, db)
        self.state_id = "check exceed value"
        self.send_message = False
        self.eCO2_limit = 1200
    
    def run(self):
        sensor_id = self.db.getChatSession(self.chat_id)[-1]["sensor"]
        eCO2 = self.db.getLasteCO2(sensor_id)
        if (eCO2 > self.eCO2_limit and self.send_message == False):
            self.message = "Please open the window!"
            self.next_State = "check fall below value"
            self.send_message = True
        else:
            self.message = ""
            self.next_State = "check exceed value"
            
        self.db.modifyChatSession({
            "state": self.next_State,
            "chat_id": self.chat_id
        })
    
    def nextState(self) -> str:
        self.send_message = False
        return self.next_State

class checkFallBelowValue(State):
    def __init__(self, chat_id: int, db: DBConnection):
        super().__init__(chat_id, db)
        self.state_id = "check fall below value"
        self.send_message = False
        self.eco2_limit = 1200

    def run(self):
        sensor_id = self.db.getChatSession(self.chat_id)[-1]["sensor"]
        eCO2 = self.db.getLasteCO2(sensor_id)
        if (eCO2 > self.eco2_limit and self.send_message == False):
            self.message = ""
            self.next_State = "check fall below value"
        else:
            self.message = "Well done, you can close the window"
            self.next_State = "check exceed value"
            self.send_message = True
        self.db.modifyChatSession({
            "start": datetime.now(),
            "state": self.next_State,
            "chat_id": self.chat_id
        })

    def nextState(self) -> str:
        self.send_message = False
        return self.next_State

class Interaction(object):
    def __init__(self, chat_id: int, db: DBConnection, picture: bytes, output_queue: Queue):
        self.chat_id = chat_id 
        self.db = db
        self.state = {
            "LogIn":                    logIn(self.chat_id, self.db),
            "check exceed value":       checkExceedValue(self.chat_id, self.db),
            "check fall below value":   checkFallBelowValue(self.chat_id, self.db)
        }
        self.output_queue = output_queue
        self.current_state = "LogIn"
        self.state[self.current_state].run(picture)
        self.output_queue.put({"text_message":self.state[self.current_state].message})
        #if isinstance(self.state[self.current_state], logIn) and self.current_state == "check exceed value":
        output_queue.put({"log_in":None})
        self.current_state = self.state[self.current_state].nextState()
        self.getMessageEvent = Event()
        self.sendPictureEvent = Event()
        if self.current_state != "LogIn":
            self.getMessageEvent.set()
            self.sendPictureEvent.set()
            Thread(target=self.__getMessage,args=[60*5, self.getMessageEvent],daemon=True).start()
            Thread(target=self.__sendPicture,args=[60*90, self.sendPictureEvent, self.db.database_URL],daemon=True).start()
    
    def __getMessage(self, sleep_time: int, event: Event) -> str:
        while event.is_set():
            if event.is_set():
                self.state[self.current_state].run()
                self.message = self.state[self.current_state].message
                if self.message != "":
                    self.output_queue.put({"text_message":self.message})
                self.current_state = self.state[self.current_state].nextState()
                time.sleep(sleep_time)

    def __sendPicture(self, after_time: int, event: Event, DB_URL: str):
        while event.is_set():
            time.sleep(after_time)
            if event.is_set(DB_URL):
                photo = GetPictureOfeCO2(DB_URL).getPicture(datetime.now() - timedelta(seconds=after_time), datetime.now(), self.db.getChatSession(self.chat_id)[-1]["sensor"])[-1]
                self.output_queue.put({"photo_message":bytearray(b64encode(photo.read()))})
    
    def __del__(self):
        self.getMessageEvent.clear()
        self.sendPictureEvent.clear()

            