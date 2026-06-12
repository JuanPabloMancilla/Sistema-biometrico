import sys
import tkinter


def apply_customtkinter_compatibility():
    """Apply small compatibility fixes required by CustomTkinter on Tcl/Tk 9."""
    if tkinter.TclVersion < 9:
        return

    from customtkinter.windows.widgets.core_widget_classes.dropdown_menu import (
        DropdownMenu,
    )

    if getattr(DropdownMenu, "_securework_tcl9_patch", False):
        return

    original_trace_remove = tkinter.Variable.trace_remove

    def safe_trace_remove(self, mode, callback_name):
        if not callback_name:
            return
        try:
            original_trace_remove(self, mode, callback_name)
        except tkinter.TclError as error:
            if "wrong # args" not in str(error):
                raise

    def safe_add_menu_commands(self):
        try:
            end_index = self.index("end")
            if end_index not in (None, ""):
                self.delete(0, "end")
        except tkinter.TclError:
            pass

        for value in self._values or []:
            label = value
            if sys.platform.startswith("linux"):
                label = "  " + value.ljust(self._min_character_width) + "  "
            else:
                label = value.ljust(self._min_character_width)
            self.add_command(
                label=label,
                command=lambda selected=value: self._button_callback(selected),
                compound="left",
            )

    tkinter.Variable.trace_remove = safe_trace_remove
    DropdownMenu._add_menu_commands = safe_add_menu_commands
    DropdownMenu._securework_tcl9_patch = True
