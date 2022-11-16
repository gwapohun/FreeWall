__version__ = 1.0

import kivy
kivy.require("2.0.0")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager 
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.core.text import LabelBase

from kivy.lang.builder import Builder
from kivy.utils import get_color_from_hex as ghex

from threading import Thread
from backend import ManageAppData , TransferData
from list_of_screens import WallViewer , MyProfile , ProfileEditor

# ===== Navigation Button
class NavigationButton(Button) :
	pass
	
# ===== Screen Manager
class ScreensHandler(ScreenManager) :
	# Screen Editor Vars
	addr = ""
	port = 0
	
	processing = False # If Processing , No Transaction Must Occur 
	
	def __init__(self , **kwargs) :
		super(ScreensHandler , self).__init__(**kwargs)
		self.add_widget(ProfileEditor(name = "editor"))
		self.add_widget(MyProfile(name = "profile"))
		self.add_widget(WallViewer(name = "view"))
		Clock.schedule_interval(self.checking_process , 1 )
	
	def processNow(self) :
		self.processing = True
	
	def stopProcess(self) :
		self.processing = False
	
	def checkProcess(self) -> bool :
		return self.processing
	
	def checking_process(self, *args) :
		print("Processing : " ,self.processing)
			

# ==== Sign Up ModalView
class SignUp(ModalView) :
	pressed = False
	user_id = ""
	sending = False
	
	def __init__(self , **kwargs) :
		super(SignUp , self).__init__(**kwargs)
		Clock.schedule_interval( self.checkNicknameLength , 1 / 60)
		self.ids["join_button"].bind(on_press = self.buttonEffects)
		self.ids["join_button"].bind(on_release = self.registerAccount)
		self.transferData = TransferData()
	
	def setUserId(self, user_id) :
		self.user_id = user_id
	
	def checkNicknameLength(self , *args):
		if len(self.ids["nickname"].text) > 10 :
			self.ids["nickname"].text = self.ids["nickname"].text[:11]
		
	def registerAccount(self , *args) :
		if not self.sending :
			nickname : str = self.ids["nickname"].text
			
			if not nickname.isalnum() :
				self.ids["info"].text = "Invalid Nickname"
				return 
			if not self.ids["addr"].text.isascii() :
				self.ids["info"].text = "Invalid Address"
				return 
			if not self.ids["port"].text.isdigit() :
				self.ids["info"].text = "Invalid Port"
				return 
			
			self.ids["info"].text = "Wait For A Minute"
			Thread(target=self.sendingData, args=(nickname,)).start()
	
	def sendingData(self , nickname : str ) :
		self.sending = True
		if not self.transferData.set_ip( self.ids["addr"].text , int(self.ids["port"].text) ) :
			self.ids["info"].text = "Server Is Down"
			self.sending = False
			return 
		data = { "new" : ( self.user_id , nickname ) }
		if self.transferData.send( data ) :
			confirmation = self.transferData.recieved()
			if confirmation:
				if self.transferData.send(confirmation) :
					self.dismiss()
				
		self.ids["info"].text = "No Internet Connection"
		self.sending = False
		
	def buttonEffects(self , *args) :
		def endColor(*args) :
			self.ids["join_button"].color = ghex("c9ccd1")
			
		self.ids["join_button"].color = (1 , 1 , 1)
		Clock.schedule_once(endColor , 2)


# ===== Main Widget ( Main Holder )
class MainWidget(BoxLayout) :
	app_is_open = False
	
	def __init__(self , **kwargs) :
		super(MainWidget , self).__init__(**kwargs)
		self.signUpPopUp = SignUp()
		self.signUpPopUp.bind( on_dismiss = self.saveData)
		self.appDataManager = ManageAppData()
		Clock.schedule_once(self.registerUser , 1)
		
	def registerUser(self , *args) :
		if not self.appDataManager.data_exist() :
			self.appDataManager.create_path()
			self.appDataManager.create_data()
		else :
			self.appDataManager.load_data()
		self.app_is_open = True
		
		if not self.appDataManager.is_registed():
			self.signUpPopUp.setUserId(self.appDataManager.get_id())
			self.signUpPopUp.open()
	
	def saveData(self , *args) :
		self.appDataManager.register_acc()
		self.appDataManager.save_data()
	
	def checkIfRegister(self):
		conditions = ( self.app_is_open, not self.appDataManager.data_exist() )
		if all(conditions) :
			return False
		return True

# ===== Free Wall App
class FreeWallApp(App) :
	
	def on_start(self) :
		from android.permissions import request_permission , Permission
		needs = ( Permission.INTERNET , Permission.READ_EXTERNAL_STORAGE , Permission.WRITE_EXTERNAL_STORAGE )
		for need in needs :
			print(need)
			#request_permission(permission=need)
		Clock.schedule_interval( self.check_if_data_exist , 1/60)
		
	
	def build(self) :
		Builder.load_file("list_of_screens.kv")
		return MainWidget()
	
	def check_if_data_exist(self , dt : int):
		if not self.root.checkIfRegister() :
			self.stop()
		
	
if __name__ == "__main__" :
	LabelBase.register(name="wall_text" , fn_regular="wall_font.ttf")
	FreeWallApp().run()