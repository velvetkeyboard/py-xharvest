from xharvest.factories.base import Factory


class TimeEntryFormFactory(Factory):
    widget_ids = ('popoverNewTimeEntry', 'textbufferTimeEntryNotes')
    root_widget_name = 'popoverNewTimeEntry'

    def bind(self):
        cbx_proj = self.builder.get_object('comboBoxTextNewTimeEntryProject')
        cbx_task = self.builder.get_object('comboBoxTextNewTimeEntryTask')
        txt_notes = self.builder.get_object('textViewNewTimeEntryNotes')
        ent_hours = self.builder.get_object('entryNewTimeEntryHours')

        for a in self.data['assignments']:
            cbx_proj.append(str(a['project']['id']), a['project']['name'])
            if self.data['time_entry']:
                if self.data['time_entry']['project']['id'] == int(a['project']['id']):
                    for t in a['task_assignments']: 
                        cbx_task.append(f"{t['task']['id']}", t['task']['name'])

        if self.data['time_entry']:
            cbx_proj.set_active_id(str(self.data['time_entry']['project']['id']))
            cbx_task.set_active_id(str(self.data['time_entry']['task']['id']))
            bf = txt_notes.get_buffer()
            bf.set_text(self.data['time_entry']['notes'])
            ent_hours.set_text(str(self.data['time_entry']['hours']))
            self.builder.get_object('labelDeleteTimeEntry').show()
        else:
            self.builder.get_object('labelDeleteTimeEntry').hide()
            cbx_proj.set_active(-1)
            cbx_task.set_active(-1)
        #self.builder.get_object('popoverNewTimeEntry')\
        #            .set_relative_to(self.data['relative_widget'])

