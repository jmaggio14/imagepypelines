rem regenerate the ui and rc files

call D:\Python36\Lib\site-packages\PyQt4\pyuic4.bat -x .\main.ui -o mainWindowUI.py
D:\Python36\Lib\site-packages\PyQt4\pyrcc4.exe -py3 .\diagramscene.qrc -o .\diagramscene_rc3.py
D:\Python36\Lib\site-packages\PyQt4\pyrcc4.exe -py2 .\diagramscene.qrc -o .\diagramscene_rc2.py
