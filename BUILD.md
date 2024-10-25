pyinstaller:
```
python -m PyInstaller --onefile ./source/gui.py --noconsole
```

nuitka:
```
python -m nuitka --standalone --onefile --enable-plugin=pyside6 --windows-console-mode=disable `
        --windows-icon-from-ico=./images/icon.ico --output-dir=./dist ./source/gui.py
```