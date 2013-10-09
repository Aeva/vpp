
import sys
import os.path
from gi.repository import Gtk
from .slicing import pdq_print_job


class DemoHandler:
    def __init__(self, builder):
        self.builder = builder

    def onDeleteWindow(self, *args):
        #Gtk.main_quit(*args)
        pass

    def onCancel(self, *args):
        Gtk.main_quit(*args)

    def onPrint(self, *args):
        print "Init print demo! :D"

        settings = self.builder.get_object("smoke_and_mirrors")
        progress = self.builder.get_object("print_progress")
        status_bar = self.builder.get_object("slice_progress")
        settings.destroy()
        progress.show_all()

        print_args = [status_bar]
        if len(sys.argv) == 2:
            print_args.append(sys.argv[1])
        pdq_print_job(*print_args)

    def onStopJob(self, *args):
        Gtk.main_quit(*args)

    def onSliceUpdate(self, update):
        print "UPDATE:", update


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
    glade_path = os.path.abspath(
        os.path.join(__file__, "..", "print_dialog.glade"))
    builder.add_from_file(glade_path)
    builder.connect_signals(DemoHandler(builder))

    window = builder.get_object("smoke_and_mirrors")
    window.show_all()

    populate_printer_list(builder)
    
    Gtk.main()
