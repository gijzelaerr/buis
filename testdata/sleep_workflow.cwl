cwlVersion: v1.0
class: Workflow

requirements:
  - class: StepInputExpressionRequirement
  - class: InlineJavascriptRequirement

inputs: {}

outputs: {}

steps:
  sleep1:
    run: sleep.cwl
    in:
      seconds:
        valueFrom: $(1)
    out: []

  sleep10:
    run: sleep.cwl
    in:
      seconds:
        valueFrom: $(10)
    out: []

  sleep100:
    run: sleep.cwl
    in:
      seconds:
        valueFrom: $(100)
    out: []

  sleep1000:
    run: sleep.cwl
    in:
      seconds:
        valueFrom: $(1000)
    out: []

  sleep10000:
    run: sleep.cwl
    in:
      seconds:
        valueFrom: $(10000)
    out: []

