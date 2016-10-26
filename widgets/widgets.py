
class ControlPanelRowList(object):
	def __init__(self, label, values=None, name=None):
		self.name   = name
		self.label  = label
		self.values = values

	def get_value(self, value):
		valueitem = list(filter(lambda x: x[0] == value, self.values))
		if len(valueitem) > 0:
			return valueitem[0][1]
		return None

	def get_label(self, value):
		valueitem = list(filter(lambda x: x[1] == value, self.values))
		if len(valueitem) > 0:
			return valueitem[0][0]
		return None

class ControlPanelRowNumerical(object):
	def __init__(self, label, step, minimum=0, maximum=1000, name=None):
		self.name   = name
		self.label  = label
		self.step   = step
		self.minimum = minimum
		self.maximum = maximum


BANNER_WINDOW = 0
DEMO_WINDOW   = 1
MEDIA_WINDOW  = 2
UPDATE_WINDOW = 3
STATISTICS_WINDOW = 4

ValuesFrame = None
ControlPanelFrame = None
