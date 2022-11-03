
import socket
import pickle
from typing import Union
from plyer import storagepath
from uuid import uuid4
import os
import json

def app_information() :
	infos = [
		"\n",
		"You Must Read It First !\n\n" ,
		"This App Are Created To Have Fun And To Tell Your Thoughts , It Just Like A Free Wall But In Online.\n" ,
		"If You Have Any Concern Just Visit Junior Programming Club Or Ask Personally The Developers.\n",
		"\n",
		"Developers : \n" ,
		"    Ericson Mark Guanzon\n" ,
		"    Jeremiah Aguilar\n",
		"Year Level : 3rd Year - B.S.C.S.",
		"\n\n",
		"Configure : \n" ,
		"    If You Found The App Having Issue You Must Check The Following First.\n",
		" -> Must Be Connected To Internet\n",
		" -> Maybe Server Is Down ( Not Open )\n"
	]
	information = ""
	for info in infos :
		information += info
	return information

class ManageAppData :
	__app_data : dict = {}
	
	def __init__(self) :
		self.path : str = storagepath.get_documents_dir()
		self.filename = "freewall.ericson"
	
	def show_data(self) : # Debugging
		print(self.__app_data)
	
	def register_acc(self) :
		self.__app_data["registered"] = True
		
	def is_registed(self) :
		if self.__app_data["registered"] :
			return True
		return False
	
	def get_id(self) :
		return self.__app_data["user id"]
	
	def create_data(self) :
		self.__app_data["user id"] = str(uuid4())
		self.__app_data["registered"] = False
		
		with open(os.path.join(self.path , self.filename) , "w" ) as jf :
			json.dump( self.__app_data , jf)
			
	def load_data(self) :
		with open(os.path.join(self.path , self.filename) , "r" ) as jf :
			self.__app_data = json.load(jf)
	
	def save_data(self) :
		with open(os.path.join(self.path , self.filename) , "w" ) as jf :
			json.dump( self.__app_data , jf)
	
	def create_path(self) :
		os.makedirs(self.path , exist_ok=True)
	
	def data_exist(self) -> bool :
		if os.path.exists(os.path.join(self.path , self.filename)) :
			return True
		return False
	

class TransferData :
	BYTES = 16
	transfer = None
	
	def close(self) :
		self.transfer.close()
	
	@staticmethod
	def turn_to_accessable(datas : bytearray) -> Union[ None , dict] :
		try :
			return pickle.loads(b"".join(datas))
		except Exception :
			return None
		
	def recieved(self) :
		datas : bytearray = []
		while True :
			try :
				data = self.transfer.recv(self.BYTES)
				if not data :
					raise Exception("Error Transfer")
				datas.append(data)
			except Exception as e:
				print(f"[ ! ] Recieved : {e}")
				return None
			else :
				access : Union[ dict , list ] = self.turn_to_accessable(datas)
				if access != None :
					return access
		
	def send(self , data : dict) -> bool :
		try :
			self.transfer.send(pickle.dumps(data))
		except Exception as e:
			print(f"[ ! ] Send : {e}")
			return False
		return True
	
	def set_ip(self , ip : str , port : int) -> bool :
		try :
			self.transfer = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
			self.transfer.connect((ip , port))
		except Exception as e:
			print(f"[ ! ] Set Ip : {e}")
			return False
		else:
			return True

if __name__ == "__main__" :
	test = TransferData()
	print(test.send("5"))