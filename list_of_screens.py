
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex as ghex
from kivy.metrics import sp

from backend import TransferData , app_information
from threading import Thread
from time import sleep

# ==== Likes And Dislikes Button
class LikesDislikesButton(Button) :
	
	def otherIsClicked(self , color : str) -> bool :
		if self.color == color :
			return True
		return False	

# ==== Wall Cantainer
class WallContainer(BoxLayout) :
	wall_id = ""
	my_id = ""
	likes : list[str] = []
	dislikes : list[str] = []
	
	def __init__(self , **kwargs) :
		super(WallContainer, self).__init__(**kwargs)
		self.client = TransferData()
		
	def configuringIds(self , *args) :
		try : 
			self.my_id = self.parent.parent.parent.parent.user_id
		except Exception :
			pass
		else :
			self.ids["likes_button"].bind( on_release = self.userLikeIt )
			self.ids["dislikes_button"].bind( on_release = self.userDislikeIt )
			if self.my_id in self.likes :
				self.ids["likes_button"].color = ( 1 , 1 , 1)
			if self.my_id in self.dislikes :
				self.ids["dislikes_button"].color = ( 1 , 1 , 1)
			
	def configure(self , wall : dict ) :
		#data : { id : [ nickname , post  , { 'likes' : [] , 'dislikes' : [] } ] }
		self.wall_id = tuple(wall.keys())[0]
		self.likes = wall[self.wall_id][2]['likes']
		self.dislikes = wall[self.wall_id][2]['dislikes']
		self.ids["post"].text = wall[self.wall_id][1]
		self.ids["nickname"].text = f"- {wall[self.wall_id][0]}"
		self.ids["likes_button"].text = f"likes {len(self.likes)}"
		self.ids["dislikes_button"].text = f"dislikes {len(self.dislikes)}"
		Clock.schedule_once(self.configuringIds , 1 / 3 )
		
		
	# Method If User Like The Post
	def userLikeIt(self , *args ) :
		if self.parent.parent.parent.parent.parent.checkProcess() :
			return 
		if self.ids["nickname"].text == "- developers" :
			return 
		self.parent.parent.parent.parent.parent.processNow()
		Thread(target = self.sendLiking).start()
		
	def sendLiking(self) :
		addr = self.parent.parent.parent.parent.addr
		port = self.parent.parent.parent.parent.port
		if not self.client.set_ip(addr , port) :
			self.parent.parent.parent.parent.parent.stopProcess()
			return 
		data = { "like" : ( self.my_id  , self.wall_id) }
		if not self.client.send(data) :
			self.parent.parent.parent.parent.parent.stopProcess()
			return 
	
		if self.my_id not in self.likes :
			self.likes.append(self.my_id)
		if self.my_id in self.dislikes :
			self.dislikes.remove(self.my_id)
		
		self.ids["likes_button"].color = (1 , 1 , 1)
		self.ids["likes_button"].text = f"likes { len(self.likes) }"
		self.ids["dislikes_button"].color = "gray"
		self.ids["dislikes_button"].text = f"dislikes { len(self.dislikes) }"
		self.parent.parent.parent.parent.parent.stopProcess()
	
	# Method If User Dislike The Post
	def userDislikeIt(self , *args ) :
		if self.parent.parent.parent.parent.parent.checkProcess() :
			return 
		if self.ids["nickname"].text == "- developers" :
			return 
		self.parent.parent.parent.parent.parent.processNow()
		Thread(target=self.sendDisliking).start()
		
	def sendDisliking(self) :
		addr = self.parent.parent.parent.parent.addr
		port = self.parent.parent.parent.parent.port
		if not self.client.set_ip(addr , port) :
			self.parent.parent.parent.parent.parent.stopProcess()
			return 
		data = { "dislike" : ( self.my_id  , self.wall_id) }
		if not self.client.send(data) :
			self.parent.parent.parent.parent.parent.stopProcess()
			return 
		
		if self.my_id in self.likes :
			self.likes.remove(self.my_id)
		if self.my_id not in self.dislikes :
			self.dislikes.append(self.my_id)
			
		self.ids["dislikes_button"].color = (1 , 1 , 1)
		self.ids["dislikes_button"].text = f"dislikes { len(self.dislikes) }"
		self.ids["likes_button"].color = "gray"
		self.ids["likes_button"].text = f"likes { len(self.likes) }"
		self.parent.parent.parent.parent.parent.stopProcess()
	
# ==== Button for ( refresh , search , most likes , most dislikes )
class WallViewerButtons(Button) :
	
	def __init__(self , **kwargs) :
		super(WallViewerButtons , self).__init__(**kwargs)
		self.background_color = ghex("b0828c")
		self.background_down = "" #ghex("4f3139")
		self.font_name = "wall_text"
		self.font_size = sp(14)
		
	
# ==== Screen 1( Wall Viewer )
class WallViewer(Screen) :
	user_id = ""
	addr = ""
	port = 0
	
	def __init__(self , **kwargs) :
		super(WallViewer , self).__init__(**kwargs)
		self.client = TransferData()
		Clock.schedule_interval(self.checkNicknameLength , 1 /60)
		self.ids["search"].bind( on_release = self.searchNickname)
		self.ids["refresh"].bind( on_release = self.refreshWall)
		self.ids["most_likes"].bind( on_release = self.mostLikedWall)
		self.ids["most_dislikes"].bind( on_release = self.mostDislikedWall)
	
	def on_enter(self, *args) :
		self.parent.stopProcess()
		self.user_id = self.parent.parent.appDataManager.get_id()
		self.addr = self.parent.addr
		self.port = self.parent.port
		
	def displayWall(self , wall : dict) :
		widget = WallContainer()
		widget.configure(wall)
		self.ids["feeds"].add_widget(widget)
		self.ids["feeds"].bind(minimum_height=self.ids["feeds"].setter('height'))
	
	def checkNicknameLength(self , *args):
		if len(self.ids["nickname"].text) > 10 :
			self.ids["nickname"].text = self.ids["nickname"].text[:11]
	
	#  Method For Finding Most Disliked
	def mostDislikedWall(self , *args) :
		# Data Collecting	
		if self.parent.checkProcess() :
			return 
		self.parent.processNow()
		data = { "most disliked" : self.user_id }
		Thread(target=self.findingMostDisliked , args=(data , )).start()
	
	def findingMostDisliked(self , data : dict) :
		if not self.client.set_ip(self.parent.addr , self.parent.port) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		if not self.client.send(data) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		walls = self.client.recieved()
		if not walls :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		self.client.close()
		self.ids["feeds"].clear_widgets()
		
		for wall in walls :
			sleep(1/40)
			self.displayWall(wall)
		try:	self.parent.stopProcess()
		except Exception:	pass
	
	# Method For Finding Most Liked
	def mostLikedWall(self , *args) :
		# Data Collecting	
		if self.parent.checkProcess() :
			return 
		self.parent.processNow()
		data = { "most liked" : self.user_id }
		Thread(target=self.findingMostLiked , args=(data , )).start()
	
	def findingMostLiked(self , data : dict) :
		if not self.client.set_ip(self.parent.addr , self.parent.port) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		if not self.client.send(data) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		walls = self.client.recieved()
		if not walls :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		self.client.close()
		self.ids["feeds"].clear_widgets()
		
		for wall in walls :
			sleep(1/40)
			self.displayWall(wall)
		try:	self.parent.stopProcess()
		except Exception:	pass
	
	# Method For Refreshing Wall
	def refreshWall(self , *args) :
		# Data Collecting	
		if self.parent.checkProcess() :
			return 
		self.parent.processNow()
		data = { "refresh" : self.user_id }
		Thread(target=self.refreshingWall , args=(data , )).start()
	
	def refreshingWall(self , data : dict) :
		if not self.client.set_ip(self.parent.addr , self.parent.port) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		if not self.client.send(data) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		walls = self.client.recieved()
		if not walls :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		
		self.client.close()
		self.ids["feeds"].clear_widgets()
		for wall in walls :
			sleep(1/40)
			self.displayWall(wall)
		try:	self.parent.stopProcess()
		except Exception:	pass
	
	# Method For Searching Nickname
	def searchNickname(self, *args) :
		nickname : str = self.ids["nickname"].text
		
		def returnHintText( *args) :
			self.ids["nickname"].hint_text = "nickname"
		
		# Checking The Nickname
		if not nickname.isascii() :
			self.ids["nickname"].text = ""
			self.ids["nickname"].hint_text = "invalid nickname"
			Clock.schedule_once(returnHintText , 1 )
			return 
		
		# Data Collecting	
		if self.parent.checkProcess() :
			return 
		self.parent.processNow()
		data = { "find" : nickname }
		Thread(target=self.findingNickname , args=(data,)).start()
	
	def findingNickname(self , data : dict) :
		if not self.client.set_ip(self.parent.addr , self.parent.port) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		if not self.client.send(data) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		walls : list[dict] = self.client.recieved()
		if not walls : 
			try:	self.parent.stopProcess()
			except Exception:	pass
			
			def returnHintText( *args) :
				self.ids["nickname"].hint_text = "nickname"
		
			self.ids["nickname"].text = ""
			self.ids["nickname"].hint_text = "Not Found"
			Clock.schedule_once(returnHintText , 1 )
			return 
		
		self.client.close()
		self.ids["feeds"].clear_widgets()
			
		for wall in walls :
			sleep(1/3)
			self.displayWall(wall)
		try:	self.parent.stopProcess()
		except Exception:	pass
		

# ==== Screen 2( Profile )
class MyProfile(Screen) :
	user_id = ""
	
	def __init__(self , **kwargs) :
		super(MyProfile , self).__init__(**kwargs)
		self.client = TransferData()
		
	def on_enter(self , *args) :
		self.parent.stopProcess()
		self.user_id = self.parent.parent.appDataManager.get_id()
		self.ids["refresh"].bind(on_release = self.updateProfile)
		
	def updateProfile(self , * args) :
		if self.parent.checkProcess() :
			return 
		self.parent.processNow()
		Thread(target=self.updatingProfile).start()
	
	def returnOriginalText(self , *args) :
		self.ids["refresh"].text = "refresh"
	
	def updatingProfile(self) :
		data =  { "check" : self.user_id }
		if not self.client.set_ip(self.parent.addr , self.parent.port) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		if not self.client.send(data) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		wall = self.client.recieved()
		if not wall :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		self.client.close()
		Clock.schedule_once(self.returnOriginalText, 1)
		self.ids["refresh"].text = "done"
		self.ids["nickname"].text =wall[0]
		self.ids["post"].text = wall[1]
		self.ids["likes"].text = f"likes {len(wall[2]['likes'])}"
		self.ids["dislikes"].text = f"dislikes {len(wall[2]['dislikes'])}"
		try:	self.parent.stopProcess()
		except Exception:	pass
		
# ==== EditorButtons ( Update , Post )
class EditorButtons(Button) :
	
	def endColor(self , *args) :
		self.color = ( 1 , 1 ,1)
	
	def on_press(self , *args) :
		self.color = ghex("b0828c")
		Clock.schedule_once(self.endColor , 2)
	
# ==== Screen 3( Editor )
class ProfileEditor(Screen) :
	user_id = ""
	
	def __init__(self , **kwargs) :
		super(ProfileEditor , self).__init__(**kwargs)
		self.client = TransferData()
		self.ids["info"].text = app_information()
		Clock.schedule_once(self.configuringIds , 1.5)
		Clock.schedule_interval(self.saveTheIP , 1 / 30 )
		Clock.schedule_interval(self.reformatPost , 1 / 60)
	
	def configuringIds(self , *args) :
		self.ids["post"].bind(on_release = self.updatePost)
		self.user_id = self.parent.parent.appDataManager.get_id()
	
	def on_enter(self) :
		self.parent.stopProcess()
		
	def saveTheIP(self , *args) :
		# If  Active Screen , Save IP
		if not self.parent or self.ids["post"].text == "D O N E" :
			return 
		
		if self.ids["addr"].text.isalnum() :
			self.parent.addr = self.ids["addr"].text
		if self.ids["port"].text.isdigit() :
			self.parent.port = int(self.ids["port"].text)
	
	def reformatPost(self , *args) :
		for n , letter in enumerate(self.ids["post_text"].text[:]) :
			if letter == "\n" :
				format_text = list(self.ids["post_text"].text)
				format_text[n] = " "
				self.ids["post_text"].text = "".join(format_text)
			if not letter.isascii() :
				format_text = list(self.ids["post_text"].text)
				format_text[n] = " "
				self.ids["post_text"].text = "".join(format_text)
			
		if len(self.ids["post_text"].text) >= 130 :
			self.ids["post_text"].text = self.ids["post_text"].text[:130]
	
	# Method For Updating Post
	def updatePost(self , *args) :
		if self.parent.checkProcess() :
			return 
		self.parent.processNow()
		Thread(target=self.updatingPost).start()
	
	def changePostButtonText(self ) :
		self.ids["post"].text = "D O N E"
		def backToNormal(dt) :
			self.ids["post"].text = "P O S T"
		Clock.schedule_once(backToNormal , 1)
	
	def updatingPost(self) :
		if not self.ids["addr"].text.isalnum() and not self.ids["port"].text.isdigit() :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		if not self.client.set_ip(self.parent.addr , self.parent.port) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		data = { "post" : (self.user_id , self.ids["post_text"].text) }
		if not self.client.send(data) :
			try:	self.parent.stopProcess()
			except Exception:	pass
			return 
		self.client.close()
		# Do something If Succesfully Post
		self.changePostButtonText()
		try:	self.parent.stopProcess()
		except Exception:	pass
		
		