import code
import os
import sys
import contextlib
import io

from PyQt4 import QtGui, QtCore

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

import time
import logging;logging.basicConfig(filename='interp.out',level=logging.INFO)

class QtInterpreter(QtGui.QPlainTextEdit):
    ps1 = '>>> '
    ps2 = '... '
    linesep = '\n'
    rich_text = False   # ND TODO: implement rich text option (i.e. html)
    single_threaded = True   # ND TODO: implement non-blocking runsource call

    variable_update = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None, variables={}):
        super().__init__(parent)
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
        # TODO: write out history

    def preprocess(self, command):
        # hook for macros, shortcuts, etc
        return command

    def run_command(self, command):
        command = self.preprocess(command)

        out = io.StringIO()   # string buffers to capture output
        err = io.StringIO()

        output = ''

        with stdout_as(out), stderr_as(err):
            try:
                ret = self.interp.runsource(command)
                
                logging.info(out.getvalue())
                logging.info(err.getvalue())

                outval = out.getvalue()
                errval = err.getvalue()

                if not outval and not errval:
                    #self.insertHtml('<br>')
                    output += self.linesep
                    logging.info('1' + out.getvalue() + err.getvalue())
                else:
                    #self.insertHtml('<br>')
                    output += self.linesep
                    if outval:
                        output += outval
                    if errval:
                        output += errval
                    logging.info('2' + out.getvalue() + err.getvalue())

                if ret:
                    output += self.ps2
                else:
                    output += self.ps1

                self.output(output)

                # set scroll bar to the bottom
                self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

                # update history
                self.variable_update.emit(self.locals)   # for variable inspector
                if command:
                    self.history.insert(0, command)
                self.history_idx = 0
            
            except Exception as e:
                print(e)

        print('out:', out.getvalue())
        print('err:', err.getvalue())
        print('history', self.history_idx, self.history)

    def output(self, text, color='black'):
        self.insertPlainText(text)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        # self.insertHtml('<p style="color:{color}">{text}</p>'.format(color=color, text=text))

    def rewrite_line(self, new_line):
        # rewrite the line for history update / corrected statements
        text = self.toPlainText()
        text_lines = text.split(self.linesep)[:-1]   # get all but last line
        self.setPlainText('\n'.join(text_lines + [self.ps1 + new_line]))
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        self.moveCursor(QtGui.QTextCursor.End)  # move to the end of the document

    # disable clicking and selecting
    # def mouseReleaseEvent(self, e): pass
    # def mousePressEvent(self, e): pass
    # def mouseDoubleClickEvent(self, e): pass

    # TODO disallow deleting / backspacing the prompt

    def keyPressEvent(self, e):
        # TODO make it non clickable
        # TODO fix history

        if e.key() == QtCore.Qt.Key_Up:

            if self.history:
                self.history_idx += 1
                self.history_idx = min(len(self.history) - 1, self.history_idx)
                self.history_idx = max(0, self.history_idx)
                print('up', self.history_idx)
                self.rewrite_line(self.history[self.history_idx])

        elif e.key() == QtCore.Qt.Key_Down:
            if self.history:
                self.history_idx -= 1
                self.history_idx = min(len(self.history) - 1, self.history_idx)
                self.history_idx = max(0, self.history_idx)
                print('down', self.history_idx)

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


class Variables(QtGui.QTreeWidget):
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
    app = QtGui.QApplication(sys.argv)

    # set up main display window

    display = Interpreter(variables={'app':app})
    display.show()

    sys.exit(app.exec_())
