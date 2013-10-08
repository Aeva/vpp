from gi.repository import Gtk


class DemoHandler:
    def onDeleteWindow(self, *args):
        #Gtk.main_quit(*args)
        pass

    def onCancel(self, *args):
        Gtk.main_quit(*args)

    def onPrint(self, *args):
        print "Init print demo! :D"

        settings = builder.get_object("smoke_and_mirrors")
        progress = builder.get_object("print_progress")
        settings.destroy()
        progress.show_all()

    def onStopJob(self, *args):
        Gtk.main_quit(*args)


def populate_printer_list(builder):
    columns = ["Printer", "Location", "Status"]
    data = [
        ["Print to file", "", ""],
        ["Lulzbot TAZ", "", "Ready!"],
        ["Lulzbot AO-101", "", "Offline"],
        ["Generic Reprap", "", "Offline"],
    ]

    store = Gtk.ListStore(str, str, str)
    for row in data:
        store.append(row)

    tree = builder.get_object("printer_treeview")
    tree.set_model(store)
    renderer = Gtk.CellRendererText()

    for column in columns:
        tree.append_column(Gtk.TreeViewColumn(column, renderer))

    # ok... this doesn't quite work, but whatever.


def gui_main(*args):
    builder = Gtk.Builder()
    builder.add_from_file("printdialog.glade")
    builder.connect_signals(DemoHandler())

    window = builder.get_object("smoke_and_mirrors")
    window.show_all()

    populate_printer_list(builder)
    
    Gtk.main()
