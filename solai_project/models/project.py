# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, SUPERUSER_ID, _


class Task(models.Model):
    _inherit = "project.task"

    def action_subtask(self):
        action = self.env.ref('project.project_task_action_sub_task').read()[0]

        # only display subtasks of current task
        action['domain'] = [('id', 'child_of', self.id), ('id', '!=', self.id)]

        # update context, with all default values as 'quick_create' does not contains all field in its view
        if self._context.get('default_project_id'):
            default_project = self.env['project.project'].browse(self.env.context['default_project_id'])
        else:
            default_project = self.project_id.subtask_project_id or self.project_id
        ctx = dict(self.env.context)
        ctx.update({
            # 'default_name': self.env.context.get('name', self.name) + ':',
            'default_parent_id': self.id,  # will give default subtask field in `default_get`
            'default_company_id': default_project.company_id.id if default_project else self.env.company.id,
            'search_default_parent_id': self.id,
        })
        parent_values = self._subtask_values_from_parent(self.id)
        for fname, value in parent_values.items():
            if 'default_' + fname not in ctx:
                ctx['default_' + fname] = value
        action['context'] = ctx

        return action