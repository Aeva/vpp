
import sys
import os.path
import json
from gi.repository import Gtk
from dbus.mainloop.glib import DBusGMainLoop
from switchprint.switch_board import SwitchBoard
from switchprint.printer_interface import PrinterInterface
from .slicing import pdq_print_job


class PrinterWrapper(PrinterInterface):
    def __init__(self, *args, **kwargs):
        self.heater_bar = None
        self.progress_bar = None
        PrinterInterface.__init__(self, *args, **kwargs)

    def on_report(self, blob):
        data = json.loads(blob)
        tool = data["thermistors"]["tools"][0]
        bed = data["thermistors"]["bed"]

        def get_percent(pair):
            value, target = pair
            if target == None:
                return 0
            if value >= target:
                return 100
            else:
                return 100/target*value
        percent = sum(map(get_percent, [tool, bed]))/2.0
        if self.heater_bar:
            self.heater_bar.set_fraction(percent/100.0)
            self.heater_bar.set_text(
                "Nozzle: {0}, Bed: {1}".format(
                    tool[0], bed[0]))

    def connect(self, heater_bar, progress_bar):
        self.heater_bar = heater_bar
        self.progress_bar = progress_bar


class DemoHandler(SwitchBoard):
    def __init__(self, builder):
        self.builder = builder
        self.printer = None
        self.print_started = False
        SwitchBoard.__init__(self, PrinterWrapper)

    def warm_up(self):
        self.printer.home()
        self.printer.motors_off()
        self.printer.set_tool_temp(0, 190)
        self.printer.set_bed_temp(45)

    def cool_down(self):
        self.printer.home(True, False, False)
        self.printer.motors_off()
        self.printer.set_tool_temp(0, 0)
        self.printer.set_bed_temp(0)

    def on_new_printer(self, printer):
        if not self.printer:
            print "Connected printer: %s" % printer.uuid
            heater_bar = self.builder.get_object("heater_progress")
            progress_bar = self.builder.get_object("print_progress")
            self.printer = printer
            self.printer.connect(heater_bar, progress_bar)
            self.printer.motors_off()
            if self.print_started:
                self.warm_up()
                
    def onDeleteWindow(self, *args):
        #Gtk.main_quit(*args)
        pass

    def onCancel(self, *args):
        Gtk.main_quit(*args)

    def onPrint(self, *args):
        self.print_started = True
        print "Init print demo! :D"

        settings = self.builder.get_object("smoke_and_mirrors")
        progress = self.builder.get_object("print_progress")
        status_bar = self.builder.get_object("slice_progress")
        settings.destroy()
        progress.show_all()

        print_args = [status_bar]
        if len(sys.argv) == 2:
            print_args.append(sys.argv[1])

        # start slicing job
        pdq_print_job(*print_args)

        # warm up printer
        self.warm_up()


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
    DBusGMainLoop(set_as_default=True)
    builder = Gtk.Builder()
    glade_path = os.path.abspath(
        os.path.join(__file__, "..", "print_dialog.glade"))
    builder.add_from_file(glade_path)
    builder.connect_signals(DemoHandler(builder))

    window = builder.get_object("smoke_and_mirrors")
    window.show_all()

    populate_printer_list(builder)
    
    Gtk.main()
