# Copyright 2015 - StackStorm, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse
import json
import logging

from cliff import command
from cliff import show
import yaml

from mistralclient.commands.v2 import base
from mistralclient import utils

LOG = logging.getLogger(__name__)


def format_list(environment=None):
    columns = (
        'Name',
        'Description',
        'Scope',
        'Created at',
        'Updated at'
    )

    if environment:
        data = (
            environment.name,
            environment.description,
            environment.scope,
            environment.created_at,
        )

        if hasattr(environment, 'updated_at'):
            data += (environment.updated_at or '<none>',)
        else:
            data += (None,)

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


def format(environment=None):
    columns = (
        'Name',
        'Description',
        'Variables',
        'Scope',
        'Created at',
        'Updated at'
    )

    if environment:
        data = (environment.name,)

        if hasattr(environment, 'description'):
            data += (environment.description or '<none>',)
        else:
            data += (None,)

        data += (
            json.dumps(environment.variables, indent=4),
            environment.scope,
            environment.created_at,
        )

        if hasattr(environment, 'updated_at'):
            data += (environment.updated_at or '<none>',)
        else:
            data += (None,)

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


def load_file_content(f):
    content = f.read()

    try:
        data = yaml.safe_load(content)
    except Exception:
        data = json.loads(content)

    return data


class List(base.MistralLister):
    """List all environments."""

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        return mistral_client.environments.list()


class Get(show.ShowOne):
    """Show specific environment."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument(
            'name',
            help='Environment name'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        environment = mistral_client.environments.get(parsed_args.name)

        return format(environment)


class Create(show.ShowOne):
    """Create new environment."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'file',
            type=argparse.FileType('r'),
            help='Environment configuration file in JSON or YAML'
        )

        return parser

    def take_action(self, parsed_args):
        data = load_file_content(parsed_args.file)

        mistral_client = self.app.client_manager.workflow_engine
        environment = mistral_client.environments.create(**data)

        return format(environment)


class Delete(command.Command):
    """Delete environment."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument('name', nargs='+', help='Name of environment(s).')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        utils.do_action_on_many(
            lambda s: mistral_client.environments.delete(s),
            parsed_args.name,
            "Request to delete environment %s has been accepted.",
            "Unable to delete the specified environment(s)."
        )


class Update(show.ShowOne):
    """Update environment."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'file',
            type=argparse.FileType('r'),
            help='Environment configuration file in JSON or YAML'
        )

        return parser

    def take_action(self, parsed_args):
        data = load_file_content(parsed_args.file)

        mistral_client = self.app.client_manager.workflow_engine
        environment = mistral_client.environments.update(**data)

        return format(environment)
