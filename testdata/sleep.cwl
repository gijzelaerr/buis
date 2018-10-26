#!/usr/bin/env cwl-runner

class: CommandLineTool
id: sleep
label: sleep all night long
cwlVersion: v1.0

inputs: []

outputs: []

baseCommand: [sleep, 50]

