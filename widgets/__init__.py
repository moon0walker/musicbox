from . import widgets
from . import control_panel
from . import values
from tools.lang import _

data = [
	widgets.ControlPanelRowNumerical(name='order',         label=_('Order cost'), step=0.5, minimum=1, maximum=100),
	widgets.ControlPanelRowList     (name='karaoke_order', label=_('Karaoke order cost'), values=[ (_('Disable'),'0'), ('x1','1'), ('x2','2'), ('x3','3'), ('x4','4') ]),
	widgets.ControlPanelRowList     (name='currency',      label=_('Choose currency'), values=[ ('USD', 'USD'), ('EUR', 'EUR'), ('ZLT', 'ZLT'), ('RUB', 'RUB'), ('UAH', 'UAH') ] ),
	widgets.ControlPanelRowList     (name='language',      label=_('Choose your language'), values=[ ('English', 'en_US'), ('Українська', 'uk_UA'), ('Русский', 'ru_RU'), ('Polska', 'pl_PL') ]),
	widgets.ControlPanelRowList     (name='demo_folders',  label=_('Folder of the demonstration mode'), values=[ (_('Disable'), 'disable'), (_('Select Path'), ''), (_('All library'), 'all_library') ] ),
	widgets.ControlPanelRowNumerical(name='volumediff',    label=_('The volume difference between demo and ordered compositions'), step=1, minimum=0, maximum=100),
	widgets.ControlPanelRowList     (name='theme',         label=_('The color scheme of the interface'), values=[ (_('Red'), 'Red'), (_('Blue'), 'Blue'), (_('Green'), 'Green'), (_('Silver'), 'Silver')] ),
	widgets.ControlPanelRowList     (name='equalizer',     label=_('Equalizer'), values=[]),
	widgets.ControlPanelRowList     (name='banner',        label=_('Add / remove banner'), values=[ (_('Remove'), ''), (_('Select Path'), '') ] ),
	widgets.ControlPanelRowList     (name='media_files',   label=_('Add / delete media files'), values=[ (_('Add'), 0), (_('Remove'), 1) ]),
	widgets.ControlPanelRowList     (name='statistics',    label=_('Statistics'), values=[ (_('Show'), 0), (_('Clear'), 1) ]),
	widgets.ControlPanelRowList     (name='update',        label=_('Update program'), values=[]),
	widgets.ControlPanelRowList     (name='exit',          label=_('Exit'), values=[ (_('With saving'), 1), (_('Without saving'), 0) ] )
]

def create_frames(parent, settings):
	widgets.ValuesFrame       = values.ValuesFrame             (parent, data, settings)
	widgets.ControlPanelFrame = control_panel.ControlPanelFrame(parent, data, settings)
	# widgets.ControlPanelRowList     (name='theme',         label=_('The color scheme of the interface'), values=[ (_('Red'), 'Red'), (_('Blue'), 'Blue'), (_('Green'), 'Green'), (_('Silver'), 'Silver'), (_('Set picture'), '') ] ),
