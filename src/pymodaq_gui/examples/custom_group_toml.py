from pathlib import Path
import datetime

import toml

from pymodaq_utils import config as config_mod
from pymodaq_gui.utils.widgets.tree_toml import TreeFromToml
from pymodaq_gui.parameter.pymodaq_ptypes import registerParameterType, GroupParameter

from pyqt_checkbox_list_widget.checkBoxListWidget import CheckBoxListWidget
# from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
from qtpy.QtWidgets import QDialog, QVBoxLayout, QPushButton, QCheckBox


config_path = Path('./custom_toml_group.toml')


class CustomConfig(config_mod.BaseConfig):
    """Main class to deal with configuration values for this plugin"""
    config_template_path = config_path
    config_name = f"custom_settings"


type_list = ['tc', 'volt']

child_template = [
    {'title': 'Do it?:', 'name': 'do_it', 'type': 'bool', 'value': True},
    {'title': 'Type:', 'name': 'type', 'type': 'list', 'value': 'K', 'limits': ['', 'K', '23']},
    {'title': 'Resolution:', 'name': 'resolution', 'type': 'int', 'value': 6},
    {'title': 'transducer', 'name': 'choice', 'type': 'list', 'value': type_list[0],
     'limits': type_list},
]


channel_list = [f"Instrument1/Module2/Channel{number}" for number in range(10)]


class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        # The answer we've all been looking for
        self.channellist = []

        self.setWindowTitle("Select Channels")
        self.setLayout(QVBoxLayout())

        self.allCheckBox = QCheckBox('Check all')
        self.cblist = CheckBoxListWidget()
        self.cblist.addItems(channel_list)
        self.layout().addWidget(self.allCheckBox)
        self.layout().addWidget(self.cblist)

        # label = QLabel("Enter your name:")
        # self.layout().addWidget(label)

        # self.nameEdit = QLineEdit()
        # self.layout().addWidget(self.nameEdit)

        button = QPushButton("Submit")
        button.clicked.connect(self.submit_name)
        self.layout().addWidget(button)

    def submit_name(self):
        self.channellist = self.checkedlist(self.cblist)
        self.accept()

    def checkedlist(self, widget: CheckBoxListWidget):
        """
        Return the value select from a Checkbox list
        Parameters
        ----------
        widget that is a CheckBoxListWidget

        Returns
        -------
        list of value
        """
        if isinstance(widget, CheckBoxListWidget):
            return [item.text()
                    for item in [widget.item(counter) for counter in range(widget.count())]
                    if item.checkState() == 2]
        else:
            return self.checkedlist(self.cblist)


class ScalableCustomGroup(GroupParameter):
    """
        |

        ================ =============
        **Attributes**    **Type**
        *opts*            dictionnary
        ================ =============

        See Also
        --------
        hardware.DAQ_Move_Stage_type
    """

    def __init__(self, **opts):
        opts['type'] = 'mycustomgroupparameter'
        opts['addText'] = "Add"
        opts['addList'] = type_list
        super().__init__(**opts)

    def addNew(self, optlist):
        """
            Add a child.

            =============== ===========
            **Parameters**   **Type**
            *typ*            string
            =============== ===========
        """
        name_prefix = 'template'

        dialog = CustomDialog()
        dialog.exec_()

        children = []
        for parameter in child_template:
            if parameter['name'] == "choice":
                parameter['value'] = optlist

        for channel in dialog.channellist:
            children.append({'title': f'{channel}',
                             'name': f'{channel}',
                             'type': 'group',
                             'removable': True, 'children': child_template})

        self.addChildren(children)


registerParameterType('mycustomgroupparameter', ScalableCustomGroup, override=True)


if __name__ == '__main__':
    from pymodaq_gui.utils.utils import mkQApp

    app = mkQApp('Dashboard')

    config = CustomConfig()

    tree_toml = TreeFromToml(config)
    tree_toml.show_dialog()

    app.exec()

