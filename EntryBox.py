from customtkinter import *
from customtkinter import filedialog
from sheetLoader import sheets

possible_sheets = [''] + list(sheets.keys())[:]
entry_value = ''
drop_value = ''
file_name = ''

def click(app, entry, drop=None):
    global entry_value, drop_value
    entry_value = entry.get()
    if drop: drop_value = drop.get()
    app.destroy()

def entry():
    global entry_value, drop_value
    entry_value = ''
    drop_value = ''
    app = CTk()
    set_appearance_mode('dark')
    app.geometry('500x200')
    entry = CTkEntry(master=app)
    drpdwn = CTkComboBox(app, values=possible_sheets)
    btn = CTkButton(master=app, text='Confirm', command=lambda: click(app, entry, drpdwn))
    entry.place(relx=.5, rely=.3, anchor='center')
    drpdwn.place(relx=.5, rely=.5, anchor='center')
    btn.place(relx=.5, rely=.7, anchor='center')
    drpdwn.set('')
    entry.focus()
    app.bind('<Return>', (lambda event: click(app, entry, drpdwn)))
    app.mainloop()

def save():
    global entry_value
    entry_value = ''
    app = CTk()
    set_appearance_mode('dark')
    app.geometry('500x200')
    entry = CTkEntry(master=app)
    btn = CTkButton(master=app, text='Confirm', command=lambda: click(app, entry))
    entry.place(relx=.5, rely=.4, anchor='center')
    btn.place(relx=.5, rely=.6, anchor='center')
    entry.focus()
    app.bind('<Return>', (lambda event: click(app, entry)))
    app.mainloop()

def load():
    global file_name
    file_name = ''
    app = CTk()
    set_appearance_mode('dark')
    app.geometry('500x200')
    file_selection = filedialog.askopenfile(parent=app,mode='rb',title='Choose a file', initialdir="Tilemap Editor\Saves")
    if file_selection: file_name = file_selection.name
    app.destroy()