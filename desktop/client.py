"""
Deprecated PySimpleGUI client (stub)

The project migrated to a Tkinter + ttkbootstrap tray client implemented in
`desktop/tray_app.py`. This file is kept only as a marker to avoid accidental
execution of the old GUI.

Run the new client with:

    python desktop\tray_app.py

"""
import sys

def main() -> None:
    print('This client is deprecated. Use desktop/tray_app.py')


if __name__ == '__main__':
    main()
