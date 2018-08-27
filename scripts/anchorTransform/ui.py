import os
from maya import cmds
from . import utils, commands

# ----------------------------------------------------------------------------


ICON_PATH = utils.getIconPath("AT_icon.png")


# ----------------------------------------------------------------------------


class TimeInput(utils.QWidget):
    def __init__(self, parent, label, default):
        utils.QWidget.__init__(self, parent)
        
        # create layout
        layout = utils.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        # create label
        l = utils.QLabel(self)
        l.setText(label)
        l.setFont(utils.FONT)
        l.setFixedWidth(100)
        layout.addWidget(l)
        
        # create time
        self.time = utils.QSpinBox(self)
        self.time.setMinimum(0)
        self.time.setMaximum(9999)
        self.time.setValue(default)
        self.time.setFont(utils.FONT)
        layout.addWidget(self.time)
        
    # ------------------------------------------------------------------------

    @property
    def value(self):
        return self.time.value()


class DriverInput(utils.QWidget):
    def __init__(self, parent):
        utils.QWidget.__init__(self, parent)
        
        # create layout
        layout = utils.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        # create label
        l = utils.QLabel(self)
        l.setText("Driver")
        l.setFont(utils.FONT)
        l.setFixedWidth(100)
        layout.addWidget(l)
                
        # create edit
        self.edit = utils.QLineEdit(self)
        self.edit.setPlaceholderText("World")
        self.edit.setFont(utils.FONT)
        self.edit.setEnabled(False)
        layout.addWidget(self.edit)
        
        # create button
        button = utils.QPushButton(self)
        button.setText("Selected")
        button.setFont(utils.FONT)
        button.setFixedWidth(75)
        button.released.connect(self.setTransform)
        layout.addWidget(button)
        
    # ------------------------------------------------------------------------

    @property
    def transform(self):
        transform = self.edit.text()
        return transform if cmds.objExists(transform) else None
        
    # ------------------------------------------------------------------------

    def setTransform(self):
        selection = cmds.ls(sl=True) or [""]
        self.edit.setText(selection[0])


# ----------------------------------------------------------------------------


class AnchorTransformWidget(utils.QWidget):
    def __init__(self, parent):
        utils.QWidget.__init__(self, parent)
        
        # set ui
        self.setParent(parent)        
        self.setWindowFlags(utils.Qt.Window)  

        self.setWindowTitle("Anchor Transform")      
        self.setWindowIcon(utils.QIcon(ICON_PATH))
        
        self.resize(300, 100)
        
        # create layout
        layout = utils.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # create transform input
        self.driver = DriverInput(self)
        layout.addWidget(self.driver)
        
        # divider
        layout.addWidget(utils.divider(self))
        
        # time input
        self.start = TimeInput(self, "Start Frame", 1001)
        self.start.setEnabled(False)
        layout.addWidget(self.start)
        
        self.end = TimeInput(self, "End Frame", 1010)
        self.end.setEnabled(False)
        layout.addWidget(self.end)
        
        # divider
        layout.addWidget(utils.divider(self))
        
        # create time control checkbox
        self.timeline = utils.QCheckBox(self)
        self.timeline.setChecked(True)
        self.timeline.setText("From Time Control Selection")
        self.timeline.setFont(utils.FONT)
        self.timeline.stateChanged.connect(self.setManualInputField)
        layout.addWidget(self.timeline)
        
        # divider
        layout.addWidget(utils.divider(self))
                
        # create button
        button = utils.QPushButton(self)
        button.pressed.connect(self.doAnchor)
        button.setText("Anchor Selected Transforms")
        button.setFont(utils.FONT)
        button.setFocus()
        layout.addWidget(button)
        
    # ------------------------------------------------------------------------
    
    def setManualInputField(self, state):
        self.start.setEnabled(not state)
        self.end.setEnabled(not state)
        
    # ------------------------------------------------------------------------
    
    def getFrameRangeFromTimeControl(self):
        """
        Get frame range from time control.
        
        :return: Frame range
        :rtype: list/None
        """
        rangeVisible = cmds.timeControl(
            utils.getMayaTimeline(), 
            q=True, 
            rangeVisible=True
        )
    
        if not rangeVisible:
            return
        
        r = cmds.timeControl(
            utils.getMayaTimeline(), 
            query=True, 
            ra=True
        )
        return [int(r[0]), int(r[-1])]
        
    def getFrameRangeFromUI(self):
        """
        Get frame range from IO.
        
        :return: Frame range
        :rtype: list/None
        """
        if self.start.value >= self.end.value:
            return
            
        return [self.start.value, self.end.value]

    def getFrameRange(self):
        """
        :return: Frame range
        :rtype: list/None
        """
        if self.timeline.isChecked():
            return self.getFrameRangeFromTimeControl()
        else:
            return self.getFrameRangeFromUI()
            
    # ------------------------------------------------------------------------
  
    def doAnchor(self):
        """
        Anchor selected transforms. Will raise a value error of not valid 
        frame range can be read from the UI settings.
        
        :raise ValueError: When no valid frame range is found
        """
        frameRange = self.getFrameRange()
        if not frameRange:
            raise ValueError("No valid frame range could be found!")

        commands.anchorSelection(self.driver.transform, *frameRange)


# ----------------------------------------------------------------------------


def show():
    dialog = AnchorTransformWidget(utils.mayaWindow())
    dialog.show()
