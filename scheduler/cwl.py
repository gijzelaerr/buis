import subprocess
from pathlib import Path
from typing import List, Optional

from cwl_utils.parser_v1_0 import InputParameter, InputArraySchema
from django import forms
from django.conf import settings

from scheduler.models import Dataset

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
    'boolean_array': forms.CharField,
    'string_array': forms.CharField,
    'int_array': forms.CharField,
    'float_array': forms.CharField,
    'Directory_array': forms.CharField,
    'File_array': forms.CharField,
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
                type_ = input.type.items + '_array'
            elif input.type.type == 'enum':
                type_ = input.type.type
                choices = [s[len(input.type.name) + 1:] for s in input.type.symbols]
                params['choices'] = zip(choices, choices)
            else:
                type_ = input.type.type

            params['help_text'] = input.doc

            id = input.id.split('#')[-1]

            if input.type in ['File', 'Directory']:

                repo_choices = []
                for i in prefix.rglob('*'):
                    relative = i.relative_to(prefix)
                    if not str(relative).startswith('.git'):
                        if (type_ == "Directory" and relative.is_dir()) or \
                                (type_ == "File" and relative.is_file()):
                            repo_choices.append((i, f"repo: {relative}"))

                dataset_choices = [(d.path, f"dataset: {d.description}") for d in Dataset.objects.all()]
                params['choices'] = dataset_choices + repo_choices

            if id in default_values:
                params['initial'] = default_values[id]
            else:
                params['initial'] = input.default

            if type(input.type) is InputArraySchema:
                params['initial'] = ",".join(str(i) for i in params['initial'])
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
                formatted[k] = {'class': type_, 'path': v}
            elif type_ == 'boolean_array':
                formatted[k] = [bool(x.strip()) for x in v.split(',')]
            elif type_ == 'int_array':
                formatted[k] = [int(x.strip()) for x in v.split(',')]
            elif type_ == 'float_array':
                formatted[k] = [float(x.strip()) for x in v.split(',')]
            elif type_ in ['string_array', 'Directory_array', 'File_array']:
                formatted[k] = [str(x.strip()) for x in v.split(',')]
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
