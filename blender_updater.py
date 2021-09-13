import threading
import subprocess
import signal
import os
import sys
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QComboBox, QVBoxLayout, QWidget)
from PySide6.QtCore import Slot, Qt

class BlenderUpdater(QWidget):
	def __init__(self):
		QWidget.__init__(self)

		self.title = "Blender Updater"
		self.base_path = ""
		self.branches_dir = ""
		with open("blender_updater.conf", "r") as f:
			'''
			This would have been easier with configparser but I'd like to leave the file sourceable if need be.
			'''
			fulltext = f.read()
			lines = fulltext.split("\n")
			for line in lines: # LIFO: parity with sourcing file in a shell script
				split = line.split("=")
				if split[0] == "BASE_PATH":
					self.base_path=split[1]
				elif split[0] == "BRANCHES_DIR":
					self.branches_dir=split[1]

		self.initUI()

		self.comboChanged()

	def initUI(self):
		self.setWindowTitle(self.title)

		git_command = subprocess.run(["git", "-C", self.base_path, "branch", "-a", "--sort=-committerdate"], stdout = subprocess.PIPE)

		raw_data = str(git_command).split("->")[1].split()

		filtered_data = []

		self.branches_combo = QComboBox(self)

		for data in raw_data:
			branch_name = data.split("/")[-1].split("\\n")[0]
			if branch_name not in filtered_data:
				filtered_data.append(branch_name)
				self.branches_combo.addItem(branch_name)

		self.branches_combo.currentTextChanged.connect(self.comboChanged)

		self.submit_button = QPushButton("Build selected branch")
		self.submit_button.clicked.connect(self.startThread)

		self.progress_label = QLabel("")

		self.abort_button = QPushButton("Abort current build")
		self.abort_button.clicked.connect(self.abortBuild)
		self.abort_button.setEnabled(False)

		self.start_branch_button = QPushButton("Start selected build")
		self.start_branch_button.clicked.connect(self.startBuild)
		self.start_branch_button.setEnabled(False)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.branches_combo)
		self.layout.addWidget(self.submit_button)
		self.layout.addWidget(self.progress_label)
		self.layout.addWidget(self.abort_button)
		self.layout.addWidget(self.start_branch_button)
		self.setLayout(self.layout)


	def buildBlender(self, stop_event):
		self.submit_button.setEnabled(False)
		self.start_branch_button.setEnabled(False)
		self.abort_button.setEnabled(True)
		parameters = ["sh", "./blender_updater.sh", self.getBranchName(), self.base_path, self.branches_dir]
		with subprocess.Popen(parameters, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid) as proc:
			self.shell_process = proc
			text = ""
			loop = 0
			while proc.poll() is None:
				for output in proc.stdout:
					output_string = output.strip().decode("utf-8")
					if output_string == "CHECKOUT":
						text = "(1/4) - Checkout"
						# self.progress_label.setText("(1/4) - Checkout")
						self.title = "(1/4) - Blender Updater"
					elif output_string == "UPDATE":
						text = "(2/4) - Update"
						# self.progress_label.setText("(2/4) - Update")
						self.title = "(2/4) - Blender Updater"
					elif output_string == "BUILD":
						text = "(3/4) - Build"
						# self.progress_label.setText("(3/4) - Build")
						self.title = "(3/4) - Blender Updater"
					elif output_string == "Error during build": #TODO: Does this Linux?
						progress = False
						text = "Error during build"
						# self.progress_label.setText("Error during build")
						self.title = "Blender Updater"

					dots = int(loop % 4)
					dots_text = ""
					for i in range(dots):
						dots_text += "."

					self.progress_label.setText(text + dots_text)

					self.setWindowTitle(self.title)

					print(output_string)

					loop += 1

		self.progress_label.setText("(4/4) - Done")
		self.title = "Blender Updater"
		self.abort_button.setEnabled(False)
		self.start_branch_button.setEnabled(True)
		self.submit_button.setEnabled(True)

		self.setWindowTitle(self.title)

		#for i in range(5): # Not sure of *nix equivalent
		#	ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)

		self.cancelThread()


	def abortBuild(self):
		if self.shell_process:
			os.killpg(os.getpgid(self.shell_process.pid), signal.SIGTERM) # shhhh it works
			self.shell_process.wait()
			self.stop_event.set()
			self.abort_button.setEnabled(False)
			self.start_branch_button.setEnabled(True)
			self.submit_button.setEnabled(True)
			self.progress_label.setText("Aborted")
			self.title = "Blender Updater"
			self.setWindowTitle(self.title)

	def getBranchName(self):
		selectedBranch = self.branches_combo.currentText()
		return selectedBranch if len(selectedBranch)>0 else "master"

	def startThread(self):
		self.stop_event = threading.Event()
		self.c_thread = threading.Thread(target = self.buildBlender, args = (self.stop_event, ))
		self.c_thread.start()


	def comboChanged(self):
		path = os.path.join(self.base_path, self.branches_dir, self.getBranchName(), "bin/blender")

		if os.path.exists(path):
			self.start_branch_button.setEnabled(True)
		else:
			self.start_branch_button.setEnabled(False)


	def startBuild(self):
		path = os.path.join(self.base_path, self.branches_dir, self.getBranchName(), "bin/blender")
		print("START : " + path)
		subprocess.Popen([path])


	def cancelThread(self):
		self.stop_event.set()


def main():
	app = QApplication(sys.argv)

	widget = BlenderUpdater()
	widget.resize(400, 200)
	widget.show()

	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
