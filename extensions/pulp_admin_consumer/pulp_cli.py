# -*- coding: utf-8 -*-
#
# Copyright © 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import time
from gettext import gettext as _
from pulp.gc_client.framework.extensions import PulpCliSection, PulpCliCommand, \
    PulpCliOption, PulpCliFlag, UnknownArgsParser
from pulp.gc_client.api.exceptions import NotFoundException

# -- framework hook -----------------------------------------------------------

def initialize(context):
    consumer_section = AdminConsumerSection(context)
    consumer_section.add_subsection(ContentSection(context))
    context.cli.add_section(consumer_section)
    
# -- common exceptions --------------------------------------------------------

class InvalidConfig(Exception):
    """
    During parsing of the user supplied arguments, this will indicate a
    malformed set of values. The message in the exception (e[0]) is formatted
    and i18n'ed to be displayed directly to the user.
    """
    pass

# -- sections -----------------------------------------------------------------

class AdminConsumerSection(PulpCliSection):

    def __init__(self, context):
        PulpCliSection.__init__(self, 'consumer', 'consumer lifecycle (list, update, etc.) commands')

        self.context = context
        self.prompt = context.prompt # for easier access

        # Common Options
        id_option = PulpCliOption('--id', 'uniquely identifies the consumer; only alphanumeric, -, and _ allowed', required=True)
        name_option = PulpCliOption('--display_name', '(optional) user-readable display name for the consumer', required=False)
        description_option = PulpCliOption('--description', '(optional) user-readable description for the consumer', required=False)

        # Update Command
        update_command = PulpCliCommand('update', 'changes metadata on an existing consumer', self.update)
        update_command.add_option(id_option)
        update_command.add_option(name_option)
        update_command.add_option(description_option)
        d =  '(optional) adds/updates/deletes notes to programmtically identify the consumer; '
        d += 'key-value pairs must be separated by an equal sign (e.g. key=value); multiple notes can '
        d += 'be changed by specifying this option multiple times; notes are deleted by '
        d += 'specifying "" as the value'
        update_command.add_option(PulpCliOption('--note', d, required=False, allow_multiple=True))
        self.add_command(update_command)

        # Delete Command
        unregister_command = PulpCliCommand('unregister', 'unregisters a consumer', self.unregister)
        unregister_command.add_option(PulpCliOption('--id', 'identifies the consumer to be unregistered', required=True))
        self.add_command(unregister_command)

        # List Command
        list_command = PulpCliCommand('list', 'lists summary of consumers registered to the Pulp server', self.list)
        list_command.add_option(PulpCliFlag('--details', 'if specified, all the consumer information is displayed'))
        list_command.add_option(PulpCliOption('--fields', 'comma-separated list of consumer fields; if specified, only the given fields will displayed', required=False))
        self.add_command(list_command)

    def update(self, **kwargs):

        # Assemble the delta for all options that were passed in
        delta = dict([(k, v) for k, v in kwargs.items() if v is not None])
        delta.pop('id') # not needed in the delta
        if 'note' in kwargs.keys():
            if kwargs['note']:
                delta['notes'] = self._parse_notes(kwargs['note'])
            delta.pop('note')

        try:
            self.context.server.consumer.update(kwargs['id'], delta)
            self.prompt.render_success_message('Consumer [%s] successfully updated' % kwargs['id'])
        except NotFoundException:
            self.prompt.write('Consumer [%s] does not exist on the server' % kwargs['id'], tag='not-found')

    def unregister(self, **kwargs):
        id = kwargs['id']

        try:
            self.context.server.consumer.unregister(id)
            self.prompt.render_success_message('Consumer [%s] successfully unregistered' % id)
        except NotFoundException:
            self.prompt.write('Consumer [%s] does not exist on the server' % id, tag='not-found')

    def list(self, **kwargs):

        self.prompt.render_title('Consumers')

        consumer_list = self.context.server.consumer.consumers().response_body

        # Default flags to render_document_list
        filters = ['id', 'display_name', 'description', 'bindings', 'notes']
        order = filters

        if kwargs['details'] is True:
            filters = None
            order = ['id', 'display_name']
        elif kwargs['fields'] is not None:
            filters = kwargs['fields'].split(',')
            if 'id' not in filters:
                filters.append('id')
            order = ['id']

        # Manually loop over the repositories so we can interject the plugins
        # manually based on the CLI flags.
        for c in consumer_list:
            self.prompt.render_document(c, filters=filters, order=order)


    def install(self, **kwargs):
        id = kwargs['id']
        units = []
        for name in kwargs['name']:
            unit_key = dict(name=name)
            unit = dict(type_id='rpm', unit_key=unit_key)
            units.append(unit)
        try:
            task = self.context.server.consumer_content.install(id, units=units)
            self.prompt.render_success_message('Install task created with id [%s]' % task.task_id)
            # Wait for task to finish
            self.prompt.render_success_message('Content units [%s] successfully installed on consumer [%s]' % (kwargs['name'], id))
        except NotFoundException:
            self.prompt.write('Consumer [%s] does not exist on the server' % id, tag='not-found')



    def _parse_notes(self, notes_list):
        """
        Extracts notes information from the user-specified options and puts them in a dictionary

        @return: dict of notes

        @raises InvalidConfig: if one or more of the notes is malformed
        """

        notes_dict = {}
        for note in notes_list:
            pieces = note.split('=', 1)

            if len(pieces) < 2:
                raise InvalidConfig(_('Notes must be specified in the format key=value'))

            key = pieces[0]
            value = pieces[1]

            if value in (None, '', '""'):
                value = None

            if key in notes_dict.keys():
                self.prompt.write('Multiple values entered for a note with key [%s]. All except first value will be ignored.' % key)
                continue

            notes_dict[key] = value

        return notes_dict



class ContentSection(PulpCliSection):

    def __init__(self, context):
        PulpCliSection.__init__(
            self,
            'content',
            _('content unit installation management'))
        for Command in (InstallContent, UpdateContent, UninstallContent):
            command = Command(context)
            command.create_option(
                '--id',
                _('identifies the consumer'),
                required=True)
            command.create_option(
                '--type',
                _('content unit type ID'),
                required=True)
            command.create_option(
                '--name',
                _('content unit key (name)'),
                required=True,
                allow_multiple=True,
                aliases=['-n'])
            self.add_command(command)


class InstallContent(PulpCliCommand):

    def __init__(self, context, **options):
        PulpCliCommand.__init__(
            self,
            'install',
            _('install content units'),
            self.run,
            **options)
        self.context = context

    def run(self, **kwargs):
        id = kwargs['id']
        type_id = kwargs['type']
        units = []
        for name in kwargs['name']:
            unit_key = dict(name=name)
            unit = dict(type_id=type_id, unit_key=unit_key)
            units.append(unit)
        self.install(id, units, {})

    def install(self, id, units, options):
        prompt = self.context.prompt
        server = self.context.server
        try:
            task = server.consumer_content.install(id, units=units, options=options)
            msg = _('Install task created with id [%s]') % task.task_id
            prompt.render_success_message(msg)
            response = server.tasks.get_task(task.task_id)
            if self.rejected(response):
                return
            if self.postponed(response):
                return
            self.process(id, response)
        except NotFoundException:
            msg = _('Consumer [%s] not found') % id
            prompt.write(msg, tag='not-found')

    def rejected(self, response):
        rejected = response.is_rejected()
        if rejected:
            prompt = self.context.prompt
            msg = 'The request was rejected by the server'
            prompt.render_failure_message(_(msg))
            msg = 'This is likely due to an impending delete request for the consumer.'
            prompt.render_failure_message(_(msg))
        return rejected

    def postponed(self, response):
        postponed = response.is_postponed()
        if postponed:
            prompt = self.context.prompt
            msg  = \
                'The request to install content was accepted but postponed ' \
                'due to one or more previous requests against the consumer.' \
                ' The install will take place at the earliest possible time.'
            self.context.prompt.render_paragraph(_(msg))
        return postponed

    def process(self, id, response):
        prompt = self.context.prompt
        server = self.context.server
        cfg = self.context.client_config
        m = 'This command may be exited via CTRL+C without affecting the install.'
        prompt.render_paragraph(_(m))
        try:
            response = self.poll(response)
            if response.was_successful():
                self.succeeded(id, response)
            if response.was_failure():
                self.failed(id, response)
            if response.was_cancelled():
                self.cancelled(id, response)
        except KeyboardInterrupt:
            # graceful interrupt
            pass

    def poll(self, response):
        server = self.context.server
        cfg = self.context.client_config
        spinner = self.context.prompt.create_spinner()
        interval = cfg.getfloat('output', 'poll_frequency_in_seconds')
        while not response.is_completed():
            if response.is_waiting():
                spinner.next(_('Waiting to begin'))
            else:
                spinner.next()
            time.sleep(interval)
            response = server.tasks.get_task(response.task_id)
        return response

    def succeeded(self, id, response):
        prompt = self.context.prompt
        # overall status
        if response.result['status']:
            msg = 'Install Succeeded'
            prompt.render_success_message(_(msg))
        else:
            msg = 'Install Failed'
            prompt.render_failure_message(_(msg))
        # detailed status
        prompt.render_title('Report Details')
        details = response.result['details']
        for type_id, report in details.items():
            status = report['status']
            if status:
                d = dict(
                    status=status,
                    details=report['details'])
                order = ['status', 'details']
                prompt.render_document(d, order=order)
            else:
                d = dict(
                    status=status,
                    message=report['details']['message'])
                order = ['status', 'message']
                prompt.render_document(d, order=order)

    def failed(self, id, response):
        prompt = self.context.prompt
        msg = 'Install failed'
        prompt.render_failure_message(_(msg))
        prompt.render_failure_message(response.exception)

    def cancelled(self, id, response):
        prompt = self.context.prompt
        prompt.render_failure_message('Request Cancelled')


class UpdateContent(PulpCliCommand):

    def __init__(self, context, **options):
        PulpCliCommand.__init__(
            self,
            'update',
            _('update (installed) content units'),
            self.run,
            **options)
        self.context = context

    def run(self, **kwargs):
        id = kwargs['id']
        type_id = kwargs['type']
        units = []
        for name in kwargs['name']:
            unit_key = dict(name=name)
            unit = dict(type_id=type_id, unit_key=unit_key)
            units.append(unit)
        self.update(id, units, {})

    def update(self, id, units, options):
        prompt = self.context.prompt
        server = self.context.server
        try:
            task = server.consumer_content.update(id, units=units, options=options)
            msg = _('Install task created with id [%s]') % task.task_id
            prompt.render_success_message(msg)
            response = server.tasks.get_task(task.task_id)
            if self.rejected(response):
                return
            if self.postponed(response):
                return
            self.process(id, response)
        except NotFoundException:
            msg = _('Consumer [%s] not found') % id
            prompt.write(msg, tag='not-found')

    def rejected(self, response):
        rejected = response.is_rejected()
        if rejected:
            prompt = self.context.prompt
            msg = 'The request was rejected by the server'
            prompt.render_failure_message(_(msg))
            msg = 'This is likely due to an impending delete request for the consumer.'
            prompt.render_failure_message(_(msg))
        return rejected

    def postponed(self, response):
        postponed = response.is_postponed()
        if postponed:
            prompt = self.context.prompt
            msg  = \
                'The request to update content was accepted but postponed ' \
                'due to one or more previous requests against the consumer.' \
                ' The install will take place at the earliest possible time.'
            self.context.prompt.render_paragraph(_(msg))
        return postponed

    def process(self, id, response):
        prompt = self.context.prompt
        server = self.context.server
        cfg = self.context.client_config
        m = 'This command may be exited via CTRL+C without affecting the install.'
        prompt.render_paragraph(_(m))
        try:
            response = self.poll(response)
            if response.was_successful():
                self.succeeded(id, response)
            if response.was_failure():
                self.failed(id, response)
            if response.was_cancelled():
                self.cancelled(id, response)
        except KeyboardInterrupt:
            # graceful interrupt
            pass

    def poll(self, response):
        server = self.context.server
        cfg = self.context.client_config
        spinner = self.context.prompt.create_spinner()
        interval = cfg.getfloat('output', 'poll_frequency_in_seconds')
        while not response.is_completed():
            if response.is_waiting():
                spinner.next(_('Waiting to begin'))
            else:
                spinner.next()
            time.sleep(interval)
            response = server.tasks.get_task(response.task_id)
        return response

    def succeeded(self, id, response):
        prompt = self.context.prompt
        # overall status
        if response.result['status']:
            msg = 'Update Succeeded'
            prompt.render_success_message(_(msg))
        else:
            msg = 'Update Failed'
            prompt.render_failure_message(_(msg))
        # detailed status
        prompt.render_title('Report Details')
        details = response.result['details']
        for type_id, report in details.items():
            status = report['status']
            if status:
                d = dict(
                    status=status,
                    details=report['details'])
                order = ['status', 'details']
                prompt.render_document(d, order=order)
            else:
                d = dict(
                    status=status,
                    message=report['details']['message'])
                order = ['status', 'message']
                prompt.render_document(d, order=order)

    def failed(self, id, response):
        prompt = self.context.prompt
        msg = 'Update failed'
        prompt.render_failure_message(_(msg))
        prompt.render_failure_message(response.exception)

    def cancelled(self, id, response):
        prompt = self.context.prompt
        prompt.render_failure_message('Request Cancelled')


class UninstallContent(PulpCliCommand):

    def __init__(self, context, **options):
        PulpCliCommand.__init__(
            self,
            'uninstall',
            _('uninstall content units'),
            self.run,
            **options)
        self.context = context

    def run(self, **kwargs):
        id = kwargs['id']
        type_id = kwargs['type']
        units = []
        for name in kwargs['name']:
            unit_key = dict(name=name)
            unit = dict(type_id=type_id, unit_key=unit_key)
            units.append(unit)
        self.uninstall(id, units, {})

    def uninstall(self, id, units, options):
        prompt = self.context.prompt
        server = self.context.server
        try:
            task = server.consumer_content.uninstall(id, units=units, options=options)
            msg = _('Install task created with id [%s]') % task.task_id
            prompt.render_success_message(msg)
            response = server.tasks.get_task(task.task_id)
            if self.rejected(response):
                return
            if self.postponed(response):
                return
            self.process(id, response)
        except NotFoundException:
            msg = _('Consumer [%s] not found') % id
            prompt.write(msg, tag='not-found')

    def rejected(self, response):
        rejected = response.is_rejected()
        if rejected:
            prompt = self.context.prompt
            msg = 'The request was rejected by the server'
            prompt.render_failure_message(_(msg))
            msg = 'This is likely due to an impending delete request for the consumer.'
            prompt.render_failure_message(_(msg))
        return rejected

    def postponed(self, response):
        postponed = response.is_postponed()
        if postponed:
            prompt = self.context.prompt
            msg  = \
                'The request to uninstall content was accepted but postponed ' \
                'due to one or more previous requests against the consumer.' \
                ' The install will take place at the earliest possible time.'
            self.context.prompt.render_paragraph(_(msg))
        return postponed

    def process(self, id, response):
        prompt = self.context.prompt
        server = self.context.server
        cfg = self.context.client_config
        m = 'This command may be exited via CTRL+C without affecting the install.'
        prompt.render_paragraph(_(m))
        try:
            response = self.poll(response)
            if response.was_successful():
                self.succeeded(id, response)
            if response.was_failure():
                self.failed(id, response)
            if response.was_cancelled():
                self.cancelled(id, response)
        except KeyboardInterrupt:
            # graceful interrupt
            pass

    def poll(self, response):
        server = self.context.server
        cfg = self.context.client_config
        spinner = self.context.prompt.create_spinner()
        interval = cfg.getfloat('output', 'poll_frequency_in_seconds')
        while not response.is_completed():
            if response.is_waiting():
                spinner.next(_('Waiting to begin'))
            else:
                spinner.next()
            time.sleep(interval)
            response = server.tasks.get_task(response.task_id)
        return response

    def succeeded(self, id, response):
        prompt = self.context.prompt
        # overall status
        if response.result['status']:
            msg = 'Uninstall Succeeded'
            prompt.render_success_message(_(msg))
        else:
            msg = 'Uninstall Failed'
            prompt.render_failure_message(_(msg))
        # detailed status
        prompt.render_title('Report Details')
        details = response.result['details']
        for type_id, report in details.items():
            status = report['status']
            if status:
                d = dict(
                    status=status,
                    details=report['details'])
                order = ['status', 'details']
                prompt.render_document(d, order=order)
            else:
                d = dict(
                    status=status,
                    message=report['details']['message'])
                order = ['status', 'message']
                prompt.render_document(d, order=order)

    def failed(self, id, response):
        prompt = self.context.prompt
        msg = 'Uninstall failed'
        prompt.render_failure_message(_(msg))
        prompt.render_failure_message(response.exception)

    def cancelled(self, id, response):
        prompt = self.context.prompt
        prompt.render_failure_message('Request Cancelled')