"""
Helper functions for using Kliko in combinaton with Django
"""
from django import forms
from django.conf import settings
from cwl_utils.parser_v1_0 import InputParameter
from typing import List, Optional
from cwl_utils.parser_v1_0 import InputArraySchema
from toil.utils.toilStats import getStats, processData
from toil.common import Toil
from os import path, walk
from pathlib import Path
import subprocess
from toil.jobStores.abstractJobStore import NoSuchJobStoreException
from ruamel import yaml
import logging


mapping = {
    'null': forms.BooleanField,
    'boolean': forms.BooleanField,
    'int': forms.IntegerField,
    'long': forms.IntegerField,
    'float': forms.FloatField,
    'double': forms.FloatField,
    'string': forms.CharField,
    'File': forms.ChoiceField,
    'Directory': forms.ChoiceField,
    'enum': forms.ChoiceField,
}


def list_files(prefix: Path, extensions=None):
    if not extensions:
        extensions = ['cwl']
    for root, dirs, files in walk(str(prefix)):
        subfolder = root[len(str(prefix)) + 1:]
        for f in files:
            if f.split('.')[-1] in extensions:
                yield path.join(subfolder, f)


# todo: merge this with other list_files
def list_files2(prefix: Path):
    for i in prefix.rglob('*'):
        relative = i.relative_to(prefix)
        if not str(relative).startswith('.git'):
            yield relative


def parse_job(job: Path, repo: Path):
    with open(str(job)) as f:
        loaded = yaml.load(f)

    cleaned = {}
    for key, value in loaded.items():
        if type(value) is dict:
            if value['class'] in ['File', 'Directory']:
                cleaned[key] = str((job.parent / Path(value['path'])).resolve().relative_to(repo))
            else:
                cleaned[key] = value
        else:
            cleaned[key] = value
    return cleaned


class CwlForm(forms.Form):

    def add_fields(self, inputs: List[InputParameter], default_values: dict, prefix: Path):
        for input in inputs:
            params = {}

            # unused cwl fields: format, inputBinding, secondaryFiles, streamable

            if type(input.type) is str:
                type_ = mapping[input.type]
            elif type(input.type) is list:
                if len(input.type) != 2 or 'null' not in input.type:
                    raise Exception("We don't support io with multiple types (yet)")
                type_ = mapping[input.type[1]]
                params['required'] = False
            elif type(input.type) is InputArraySchema:
                # todo, add array type
                type_ = mapping[input.type.items]
            elif input.type.type == 'enum':
                type_ = mapping[input.type.type]
                choices = [s[len(input.type.name) + 1:] for s in input.type.symbols]
                params['choices'] = zip(choices, choices)
            else:
                type_ = mapping[input.type.type]

            params['help_text'] = input.doc

            id = input.id.split('#')[-1]

            if input.type in ['File', 'Directory']:
                files = list(list_files2(prefix))
                params['choices'] = zip(files, files)

            if id in default_values:
                params['initial'] = default_values[id]
            else:
                params['initial'] = input.default
            params['label'] = input.label

            self.fields[id] = type_(**params)

    def __init__(self, inputs: List[InputParameter], prefix: Path,
                 default_values: Optional[dict] = None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        if not default_values:
            default_values = {}

        self.inputs = inputs
        self.prefix = prefix
        self.add_fields(inputs=inputs, default_values=default_values, prefix=prefix)

    def back_to_cwl_job(self):
        return self.cleaned_data


def cwl2dot(workflow_path: str) -> (str, str):
    """
    Parses a CWL definition and return the dot representation
    """
    args = [settings.CWLTOOL_BIN, '--print-dot', '--enable-ext', workflow_path]
    done = subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = done.stdout.decode().replace("\n", " ")
    if done.returncode == 0:
        error = False
    else:
        error = done.stderr.decode().replace("\n", " ")
    return stdout, error


def toil_jobstore_info(jobstore: str) -> dict:
    """parses a toil jobstore folder"""
    try:
        jobStore = Toil.resumeJobStore(jobstore)
    except NoSuchJobStoreException:
        return {}
    else:
        stats = getStats(jobStore)
        return processData(jobStore.config, stats)
