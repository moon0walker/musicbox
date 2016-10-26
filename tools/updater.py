import os
import sys
import shutil
import tarfile
# import subprocess
from glob import glob


class Updater():
	def __init__(self, path):
		self.filepatern = 'musicbox_update'
		self.update_tmp_path = '/home/user/musicbox/update_tmp'
		self.update_file_path = os.path.join(self.update_tmp_path, 'update.py')
		self.path = path

		# if self.check_usb():
		# 	if self.find_file():
		# 		self.unpack_update()
		# 		self.start_update()

	def check_usb(self):
		if len(os.listdir(self.path)) > 0:
			return True
		else:
			return False

	def find_file(self):
		result = [y for x in os.walk(self.path) for y in glob(os.path.join(x[0], '*.tgz'))]
		for item in result:
			fn = item.split('/')
			filename = fn[len(fn)-1]
			if self.filepatern in filename:
				if self.check_valid_archive(item):
					self.filename = item
					return True
		return False

	def check_valid_archive(self, file):
		return True if tarfile.is_tarfile(file) else False

	def unpack_update(self):
		update = tarfile.open(self.filename)
		update.extractall(path=self.update_tmp_path)
		update.close()

	def clear_update_tmp(self):
		for item in os.listdir(self.update_tmp_path):
			file_path = os.path.join(self.update_tmp_path, item)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path):
					shutil.rmtree(file_path)
			except:
				pass

	def start_update(self):
		python = sys.executable
		# subprocess.Popen( '{0} {1}'.format(python, self.update_file_path), shell=True )
		# os.system( '{0} {1}'.format(python, self.update_file_path) )
		os.execl(python, python, self.update_file_path)

