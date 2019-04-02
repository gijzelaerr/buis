cwlVersion: v1.0
class: CommandLineTool

baseCommand: python3

hints:
  DockerRequirement:
      dockerImageId: random_fits

inputs:
  size:
    type: int
    default: 1024

outputs:
  fits:
    type: File
    outputBinding:
      glob: random.fits

requirements:
  - class: InlineJavascriptRequirement

arguments:
  - prefix: -c
    valueFrom: |
      from numpy import random
      from astropy.io import fits

      size = $(inputs.size)
      data = random.random((size, size))

      hdu = fits.PrimaryHDU(data)
      hdul = fits.HDUList([hdu])
      hdul.writeto('random.fits')