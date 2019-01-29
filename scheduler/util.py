"""
Helper functions for using Kliko in combinaton with Django
"""
from django import forms
from cwl_utils.parser_v1_0 import InputParameter
from typing import List, Optional
from cwl_utils.parser_v1_0 import InputArraySchema
from pathlib import Path
import json

mapping = {
    'null': forms.BooleanField,
    'boolean': forms.BooleanField,
    'int': forms.IntegerField,
    'long': forms.IntegerField,
    'float': forms.FloatField,
    'double': forms.FloatField,
    'string': forms.CharField,
    'File': forms.FilePathField,
    'Directory': forms.FilePathField,
}


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
            else:
                type_ = mapping[input.type.type]

            params['help_text'] = input.doc

            id = input.id.split('#')[-1]

            if type_ is forms.FilePathField:
                params['path'] = str(prefix)
                params['recursive'] = True
                params['match'] = "^(?!\.git|\\.).*"

            if id in default_values:
                params['initial'] = default_values[id]
            else:
                params['initial'] = input.default
            params['label'] = input.label

            self.fields[id] = type_(**params)

    def __init__(self, inputs: List[InputParameter], prefix: Path, default_values: Optional[dict]=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not default_values:
            default_values = {}

        self.inputs = inputs
        self.prefix = prefix
        self.add_fields(inputs=inputs, default_values=default_values, prefix=prefix)

    def back_to_cwl_job(self):
        return self.cleaned_data




