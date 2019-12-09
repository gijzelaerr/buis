import subprocess
from pathlib import Path
from typing import List, Optional

from cwl_utils.parser_v1_0 import InputParameter, InputArraySchema
from django import forms
from django.conf import settings

from scheduler.util import list_files2

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
    'array': forms.CharField,
}


class CwlForm(forms.Form):
    types = {}

    def add_fields(self, inputs: List[InputParameter], default_values: dict, prefix: Path):
        for input in inputs:
            params = {}

            # unused cwl fields: format, inputBinding, secondaryFiles, streamable

            if input.type == 'boolean':
                params['required'] = False
                type_ = input.type
            elif type(input.type) is str:
                type_ = input.type
            elif type(input.type) is list:
                if len(input.type) != 2 or 'null' not in input.type:
                    raise Exception("We don't support io with multiple types (yet)")
                type_ = input.type[1]
                params['required'] = False
            elif type(input.type) is InputArraySchema:
                type_ = 'array'
            elif input.type.type == 'enum':
                type_ = input.type.type
                choices = [s[len(input.type.name) + 1:] for s in input.type.symbols]
                params['choices'] = zip(choices, choices)
            else:
                type_ = input.type.type

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

            self.types[id] = type_
            self.fields[id] = mapping[type_](**params)

    def __init__(self, inputs: List[InputParameter], prefix: Path,
                 default_values: Optional[dict] = None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        if not default_values:
            default_values = {}

        self.inputs = inputs
        self.prefix = prefix
        self.add_fields(inputs=inputs, default_values=default_values, prefix=prefix)

    def back_to_cwl_job(self, prefix: Path = None):
        """
        Prepares the cleaned form data for serialisation to a job file.
        """
        formatted = {}
        for k, v in self.cleaned_data.items():
            type_ = self.types[k]
            # Files and directories are a bit more needy so require special formatting
            if type_ in ('Directory', 'File'):
                if prefix:
                    v = str(prefix / v)
                formatted[k] = {'class': type_, 'path': v}
            else:
                formatted[k] = v
        return formatted


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
