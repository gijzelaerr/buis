"""
Helper functions for using Kliko in combinaton with Django
"""
from django import forms
from cwl_utils.parser_v1_0 import InputParameter
from typing import List
from cwl_utils.parser_v1_0 import InputArraySchema

mapping = {
    'null': forms.BooleanField,
    'boolean': forms.BooleanField,
    'int': forms.IntegerField,
    'long': forms.IntegerField,
    'float': forms.FloatField,
    'double': forms.FloatField,
    'string': forms.CharField,
    'File': forms.FileField,
    'Directory': forms.FileField,
    'array': forms.CharField,  # todo
}


class CwlForm(forms.Form):
    def __init__(self, inputs: List[InputParameter], *args, **kwargs):
        super().__init__(*args, **kwargs)

        for input in inputs:
            # other fields: format, inputBinding, secondaryFiles, streamable
            if type(input.type) is str:
                type_ = mapping[input.type]
            elif type(input.type) is list:
                type_ = forms.CharField  # todo
            else:
                type_ = mapping[input.type.type]
            id = input.id.split('#')[-1]

            params = {
                'help_text': input.doc,
            }

            if type_ != forms.FileField:
                pass
                # params['default'] = input.default
                # params['description'] = input.label

            self.fields[id] = type_(**params)
