from xharvest.threads import GtkThread
from xharvest.threads import gtk_thread_method_cb
from xharvest.handlers.base import Handler


class TimeEntryFormHandler(Handler):

    template = "time_entry_form"

    def __init__(self, time_entry_id=None):
        self.time_entry_id = time_entry_id
        # TODO Replace with a proper GObject [bgn]
        self.time_entry = None
        if time_entry_id:
            self.time_entry = self.time_entries.get_by_id(time_entry_id)
        self.hours = 0
        self.notes = ""
        self.proj_id = -1
        self.task_id = -1
        # Replace with a proper GObject [end]
        super(TimeEntryFormHandler, self).__init__()

    def bind_data(self):
        self.cbx_proj = self.builder.get_object(
            "comboBoxTextNewTimeEntryProject")
        self.cbx_task = self.builder.get_object("comboBoxTextNewTimeEntryTask")
        self.render_comboboxes()
        txt_notes = self.builder.get_object("textViewNewTimeEntryNotes")
        ent_hours = self.builder.get_object("entryNewTimeEntryHours")
        if self.time_entry:
            self.cbx_proj.set_active_id(str(self.time_entry["project"]["id"]))
            self.cbx_task.set_active_id(str(self.time_entry["task"]["id"]))
            bf = txt_notes.get_buffer()
            bf.set_text(self.time_entry["notes"])
            ent_hours.set_text(str(self.time_entry["hours"]))
            self.builder.get_object("labelDeleteTimeEntry").show()
            if self.time_entry['is_running']:
                ent_hours.set_editable(False)
                ent_hours.set_can_focus(False)
        else:
            self.builder.get_object("labelDeleteTimeEntry").hide()
            self.get_widget("buttonCreateOrUpateNewTimeEntry").show()
            self.cbx_proj.set_active(-1)
            self.cbx_task.set_active(-1)

    def bind_signals(self):
        self.assignments.connect(
            "data_update_end", lambda g: self.render_comboboxes())

    # ----------------------------------------------------------------[Helpers]

    def render_comboboxes(self):
        for a in self.assignments.data:
            self.cbx_proj.append(str(a["project"]["id"]), a["project"]["name"])
            if self.time_entry:
                if self.time_entry["project"]["id"] == int(a["project"]["id"]):
                    for t in a["task_assignments"]:
                        self.cbx_task.append(
                            f"{t['task']['id']}", t["task"]["name"])

    def start_spinner(self):
        spinner = self.builder.get_object("spinnerCreatingNewTimeEntry")
        spinner.show()
        spinner.start()

    # ---------------------------------------------------------[Models Signals]

    # -----------------------------------------------------------[Core Signals]

    def on_root_closed(self, pop):
        pop.destroy()

    def on_notes_changed(self, b):
        self.notes = b.get_text(b.get_start_iter(), b.get_end_iter(), True)

    def on_hours_changed(self, entry):
        self.hours = entry.get_text()

    def on_combobox_projects_changed(self, cbx):
        self.cbx_task.remove_all()
        self.proj_id = int(cbx.get_active_id())
        for t in self.assignments.get_tasks(self.proj_id):
            self.cbx_task.append(f"{t['task']['id']}", t["task"]["name"])

    def on_combobox_tasks_changed(self, cbx):
        self.task_id = int(cbx.get_active_id() or 0)

    def on_delete_time_entry(self, ev_box, gdk_ev_btn):
        self.start_spinner()
        self.get_widget('buttonCreateOrUpateNewTimeEntry').hide()
        ev_box.hide()
        GtkThread(
            target=self.time_entries.delete,
            args=(self.time_entry_id,),
            target_cb=self.on_saving_time_entry_cb,
        ).start()

    def on_saving_time_entry_form(self, btn):
        self.start_spinner()
        btn.hide()
        # TODO Hide Delete Button As Well
        data = {
            "user_id": self.user.data["id"],
            "notes": self.notes,
            "task_id": int(self.task_id),
            "project_id": int(self.proj_id),
            "hours": self.hours,
        }
        if not self.time_entry_id:
            data["user_id"] = self.user.data["id"]
            data["spent_date"] = self.week.get_selected_date()\
                                          .date()\
                                          .isoformat()
        else:
            if self.time_entry["is_running"]:
                del data["hours"]

        GtkThread(
            target=self.on_saving_time_entry,
            args=(self.time_entry_id, data),
            target_cb=self.on_saving_time_entry_cb,
        ).start()

    # -------------------------------------------------------[Thread Callbacks]

    def on_saving_time_entry(self, time_entry_id, data):
        self.time_entries.save(time_entry_id, data)
        self.time_entries.sync_data()

    @gtk_thread_method_cb
    def on_saving_time_entry_cb(self, thread=None):
        self.get_root_widget().popdown()
        # self.time_entries.emit(TimeEntries.SIGNAL_DATA_SET_CHANGED)
        self.time_entries.emit('data_update_end')
