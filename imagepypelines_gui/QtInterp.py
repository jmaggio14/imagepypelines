import code
import os
import sys
import contextlib
import io

from PyQt5 import QtWidgets, QtCore


@contextlib.contextmanager
def stdout_as(new):
    """ context manager to replace stdout with another file-like object. """
    sys.stdout = new
    yield sys.stdout
    sys.stdout = sys.__stdout__

@contextlib.contextmanager
def stderr_as(new):
    """ context manager to replace stderr with another file-like object. """
    sys.stderr = new
    yield sys.stderr
    sys.stderr = sys.__stderr__


class Interpreter(QtWidgets.QTextEdit):
    ps1 = '>>> '
    ps2 = '... '
    linesep = '\n'
    variable_update = QtCore.pyqtSignal(dict)

    def __init__(self, master=None, variables={}):
        super().__init__(master)
        self.locals = {'__builtins__':__builtins__, 'self':self}
        self.locals.update(variables)
        
        self.globals = {}
        
        self.history = []
        self.history_idx = 0

        self.interp = code.InteractiveInterpreter(self.locals)
        self.output(self.ps1)

    def close(self, event):
        pass
        #self.output.close()
        # TODO write out history

    def run_command(self, command):
        out = io.StringIO()   # string buffers to capture output
        err = io.StringIO()

        with stdout_as(out), stderr_as(err):
            try:
                ret = self.interp.runsource(command)

                if out.getvalue() == '' and err.getvalue() == '':
                    self.insertHtml('<br>')
                else:
                    self.insertHtml('<br>')
                    self.output(out.getvalue())
                    self.output(err.getvalue(), color='red')
                    self.insertHtml('<br>')

                if ret:
                    self.output(self.ps2)
                else:
                    self.output(self.ps1)

                # set scroll bar to the bottom
                self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

                self.variable_update.emit(self.locals)
                self.history.append(command)
                self.history_idx = -1
            except Exception as e:
                print(e)

        # print('out:', repr(out.getvalue()))
        # print('err:', repr(err.getvalue()))
        print(self.history_idx, self.history)

    def output(self, text, color='black'):
        self.insertHtml('<p style="color:{color}">{text}</p>'.format(color=color, text=text))

    def rewrite_line(self, data):
        """ rewrite the line so that """

    # disable clicking and selecting
    # def mouseReleaseEvent(self, e): pass
    # def mousePressEvent(self, e): pass
    # def mouseDoubleClickEvent(self, e): pass

    def keyPressEvent(self, e):
        # TODO make it non clickable
        # TODO fix history

        if e.key() == QtCore.Qt.Key_Up:

            if self.history:
                self.history_idx -= 1
                self.history_idx = min(-len(self.history), self.history_idx)
                self.history_idx = max(-1, self.history_idx)
                print(self.history_idx)
                self.rewrite_line(self.history[self.history_idx])

        elif e.key() == QtCore.Qt.Key_Down:
            if self.history:
                self.history_idx += 1
                self.history_idx = min(-len(self.history), self.history_idx)
                self.history_idx = max(-1, self.history_idx)
                print(self.history_idx)

                self.rewrite_line(self.history[self.history_idx])

        elif e.key() == QtCore.Qt.Key_Return:
            text = self.toPlainText()

            # TODO make this robust
            # strip trailing newline and remove sub prompt
            cmd = text.split(self.ps1)[-1].rstrip(self.linesep)
            cmd = cmd.replace(self.ps2, "")

            self.run_command(cmd)

        else:
            super().keyPressEvent(e)


class Variables(QtWidgets.QTreeWidget):
    def __init__(self, master):
        QtWidgets.QTreeWidget.__init__(self, master)
        self.setColumnCount(3)
        self.setHeaderLabels(['Variable', 'Value', 'Type'])

    @QtCore.pyqtSlot(dict)
    def get_items(self, obj):
        items = self.enumerate_items(obj)
        self.clear()
        self.insertTopLevelItems(0, items)
        self.sortItems(0, QtCore.Qt.AscendingOrder)

    def enumerate_items(self, obj, items=[], level=0):
        if level > 3:
            return items

        for key in obj:
            val = obj[key]

            items.append(QtWidgets.QTreeWidgetItem([str(key), self.value(val), str(type(val))]))

            if isinstance(val, dict):
                items[-1].addChildren(self.enumerate_items(val, [], level+1))

        return items

    def value(self, val):
        if isinstance(val, list):
            _str = 'Len: '+str(len(val))
        else:
            _str = str(val)
        return _str

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # set up main display window

    display = Interpreter()
    display.show()

    sys.exit(app.exec_())