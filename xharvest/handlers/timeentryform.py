from xharvest.handlers.base import Handler
from xharvest.threads import GtkThread
from xharvest.threads import gtk_thread_cb

class TimeEntryFormHandler(Handler):

    def __init__(self, time_entry_id=None):
        super(TimeEntryFormHandler, self).__init__()
        self.time_entry_id = time_entry_id
        self.hours = 0
        self.notes = ''
        self.proj_id = -1
        self.task_id = -1

    def start_spinner(self):
        spinner = self.builder.get_object('spinnerCreatingNewTimeEntry')
        spinner.show()
        spinner.start()

    def on_closed(self, pop):
        pop.destroy()

    def on_notes_changed(self, b):
        self.notes = b.get_text(b.get_start_iter(), b.get_end_iter(), True)

    def on_hours_changed(self, entry):
        self.hours = entry.get_text()

    def on_combobox_projects_changed(self, cbx):
        cbx_task = self.builder.get_object('comboBoxTextNewTimeEntryTask')
        cbx_task.remove_all()
        self.proj_id = int(cbx.get_active_id())
        for t in self.assignments.get_tasks(self.proj_id):
            cbx_task.append(f"{t['task']['id']}", t['task']['name'])

    def on_combobox_tasks_changed(self, cbx):
        self.task_id = int(cbx.get_active_id() or 0)

    def on_delete_time_entry(self, event_box, event_button):
        self.start_spinner()

        @gtk_thread_cb
        def callback(thread, handler):
            handler.time_entries.emit('time_entry_deleted', self.time_entry_id)
            handler.builder.get_object('popoverNewTimeEntry').popdown()

        GtkThread(
            target=self.time_entries.delete,
            args=(self.time_entry_id,),
            target_cb=callback,
            target_cb_args=(self,),
        ).start()

    def on_saving_time_entry_form(self, btn):
        self.start_spinner()
        btn.hide()

        data = {
            'user_id':self.user.data['id'],
            'notes': self.notes,
            'task_id': int(self.task_id),
            'project_id': int(self.proj_id),
            'hours': self.hours,
        }

        if not self.time_entry_id:
            data['user_id'] = self.user.data['id']
            data['spent_date'] = self.week.get_selected_date()\
                                          .date()\
                                          .isoformat()

        @gtk_thread_cb
        def callback(thread, handler):
            handler.time_entries.emit('time_entry_saved', self.time_entry_id)
            handler.builder.get_object('popoverNewTimeEntry').popdown()

        GtkThread(
            target=self.time_entries.save,
            args=(self.time_entry_id, data),
            target_cb=callback,
            target_cb_args=(self,),
        ).start()
        #self.time_entries.save(self.time_entry_id, data)
        #self.time_entries.emit('time_entry_saved', self.time_entry_id)
        #pop = self.builder.get_object('popoverNewTimeEntry')
        #pop.popdown()

