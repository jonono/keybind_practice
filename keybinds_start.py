import sys
import time
import random
import skills
from PyQt4 import QtCore, QtGui

from keybinds import Ui_MainWindow



class StartQT4(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.mouse_buttons = [(QtCore.Qt.LeftButton,'M1'),
							  (QtCore.Qt.RightButton,'M2'),
							  (QtCore.Qt.MidButton,'M3'),
							  (QtCore.Qt.XButton1,'M4'),
							  (QtCore.Qt.XButton2,'M5')]
		self.user_skills = {}
		self.current_time = time.time()
		self.current_input = []
		self.current_player = ''
		self.current_skill = ''
		self.success_hits = 0
		self.total_hits = 0
		self.total_time = None
		self.user_players = {}
		self.started = 0
		self.parsing = 0
		self.restart_timer = None
		
		QtCore.QObject.connect(self.ui.start_button,QtCore.SIGNAL("clicked()"), self.start_counter)
		QtCore.QObject.connect(self.ui.stop_button,QtCore.SIGNAL("clicked()"), self.stop_counter)
		self.ui.success_label.setStyleSheet('QLabel#success_label {background: lightgrey}')
		self.ui.success_label.setText('Stopped.')
		
		self.ui.skills_label.setText('Welcome.')
		self.parse_config()
		
	def start_counter(self):
		self.ui.user_input.setText('')
		self.ui.ratio_label.setText('')
		self.ui.avg_label.setText('')
		self.ui.reaction_label.setText('')
		self.ui.stop_button.setEnabled(True)
		self.ui.start_button.setEnabled(False)
		self.total_hits = 0
		self.total_time = None
		self.success_hits = 0
		self.ui.success_label.setText('Starting...')
		self.produce_timer()
	
	def produce_timer(self):
		self.restart_timer = QtCore.QTimer()
		self.restart_timer.timeout.connect(self.run_challenge)
		self.restart_timer.setSingleShot(True)
		self.restart_timer.start(1000)
	
	def stop_counter(self):
		if self.restart_timer:
			self.restart_timer.stop()
			self.restart_timer.deleteLater()
		self.started = 0
		self.parsing = 146
		self.ui.stop_button.setEnabled(False)
		self.ui.start_button.setEnabled(True)
		self.ui.success_label.setStyleSheet('QLabel#success_label {background: lightgrey}')
		self.ui.success_label.setText('Stopped.')
	
	def keyPressEvent(self, event):
		if((self.started) & (not(self.parsing))):
			self.parse_input(event.key(),0)
		
	
	def mousePressEvent(self, event):
		if(self.started & (not(self.parsing))):
			self.parse_input(event.button(),1)
	
	def run_challenge(self):
		self.parsing = 0
		pair = self.generate_pair()
		self.current_player = pair[0]
		self.current_skill = pair[1]
		sentence = self.generate_sentence(pair[0],pair[1])
		self.ui.skills_label.setText(sentence)
		self.current_time = time.time()
		self.ui.success_label.setStyleSheet('QLabel#success_label {background: lightyellow}')
		self.ui.success_label.setText('Waiting for input...')
		self.ui.user_input.setText('')
		self.started = 1
		
		
	def generate_pair(self):
		pair = [random.choice(list(self.user_players.keys())).lower() , random.choice(list(self.user_skills.keys()))]
		while(((pair[0].lower() == 'self') & (pair[1] in skills.other_target)) | ((pair[0].lower() != 'self') & (pair[1] in skills.no_target))):
			pair = [random.choice(list(self.user_players.keys())).lower() , random.choice(list(self.user_skills.keys()))]
		return pair

	def generate_sentence(self,player,skill):
		if(self.current_skill in skills.no_target):
			sentence = 'Use ' + skill + '!'
		else:
			sentence = 'Target ' + player + ' with ' + skill + '!'
		return sentence
	
	def parse_input(self,key,mouse):
		if(mouse):
			mouse_tuple = [x for x in self.mouse_buttons if x[0] == key]
			self.ui.user_input.setText(self.ui.user_input.text() + mouse_tuple[0][1])
		else:
			self.ui.user_input.setText(self.ui.user_input.text() + QtGui.QKeySequence(key).toString().upper())
		self.current_input.append(key)
			
		if((len(self.current_input) == 2) | (self.current_skill in skills.no_target)):
			self.parse_success()	
	
	def parse_success(self):
		self.parsing = 1
		spent_time = time.time() - self.current_time
		if(self.compare_keys()):
			self.ui.success_label.setStyleSheet('QLabel#success_label {background: lightgreen}')
			self.ui.success_label.setText('Correct!')
			self.success_hits+=1
		else:
			self.ui.success_label.setStyleSheet('QLabel#success_label {background: pink}')
			self.ui.success_label.setText('Wrong! ' + self.user_players.get(self.current_player.lower()) + ' + ' + self.user_skills.get(self.current_skill))
		self.total_hits+=1
		if(self.total_time):
			self.total_time+= spent_time
		else:
			self.total_time = spent_time
		self.ui.ratio_label.setText( "{:.1f}".format(self.success_hits/self.total_hits*100) + '%')
		self.ui.avg_label.setText("{:.1f}".format(self.total_time/self.total_hits) + 's')
		self.ui.reaction_label.setText("{:.1f}".format(spent_time) + 's')
		self.produce_timer()
		self.current_input = []
	
	def compare_keys(self):
		mbuttons = [x[1] for x in self.mouse_buttons]
		
		if(self.current_skill in skills.no_target):
			if(self.user_skills.get(self.current_skill) in mbuttons):
				[correct_button] = [x[0] for x in self.mouse_buttons if x[1] == self.user_skills.get(self.current_skill)]
				return correct_button == self.current_input[0]
			else:
				return self.current_input[0] == QtGui.QKeySequence.fromString(self.user_skills.get(self.current_skill))
		else:
			if(self.user_players.get(self.current_player) in mbuttons):
				[correct_player_button] = [x[0] for x in self.mouse_buttons if x[1] == self.user_players.get(self.current_player)]
			else:
				correct_player_button = QtGui.QKeySequence.fromString(self.user_players.get(self.current_player))
			
			if(self.user_skills.get(self.current_skill) in mbuttons):
				[correct_skill_button] = [x[0] for x in self.mouse_buttons if x[1] == self.user_skills.get(self.current_skill)]
			else:
				correct_skill_button = QtGui.QKeySequence.fromString(self.user_skills.get(self.current_skill))
		return (self.current_input[0] == correct_player_button) & (self.current_input[1] == correct_skill_button)
		#return (self.current_input[0] == QtGui.QKeySequence.fromString(self.user_players.get(self.current_player))) & (self.current_input[1] == QtGui.QKeySequence.fromString(self.user_skills.get(self.current_skill)))

		
	def parse_config(self):
		line_num = 0
		f = open('config.txt','r')
		content = f.read().split('\n')
		f.close()
		clean_content = [x for x in content if not x.startswith('#')]
		for line in clean_content:
			line = line.strip()
			if(line != '[Players]'):
				if '=' in line:
					current_pair = line.split('=')
					current_pair[0] = current_pair[0].strip()
					current_pair[1] = current_pair[1].strip()
					self.user_skills[current_pair[0]]=current_pair[1]
			else:
				for i in range(line_num,len(clean_content)):
					if '=' in clean_content[i]:
						current_pair = clean_content[i].split('=')
						current_pair[0] = current_pair[0].strip()
						current_pair[1] = current_pair[1].strip()
						self.user_players[current_pair[0].lower()]=current_pair[1]
			line_num+=1	
			if(line == '[Players]'):
				break
		
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	current_app = StartQT4()
	current_app.show()
	sys.exit(app.exec_())
