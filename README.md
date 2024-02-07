
# serialem-remontage
Reassemble montaged atlases from SerialEM

![image](https://github.com/tribell4310/serialem-remontage/assets/67428134/77ce6934-b07f-41ef-9e39-d3d07e26f121)


## Approach

This script takes in the `*.st` (image stack) and `*.st.mdoc` (metadata) files produced by SerialEM during a grid montaging event.  Place these two files in a working directory along with the `remontage.py` script.


## Dependencies

Image processing requires [mrc2tif](https://bio3d.colorado.edu/imod/doc/man/mrc2tif.html) from the [IMOD software suite](https://bio3d.colorado.edu/imod/).  The data processing scripts require python 3.10 or higher, preferably installed in a dedicated virtual environment. Package dependencies are:
 - numpy
 - pillow

## Protocol

 - Navigate to your working directory.
 - Run the mrc2tif script:
`mrc2tif your_stack_file.st file_prefix` 
 - Run the re-montaging script:
`python remontage.py file_prefix`
 - Your finished montage is now saved as a jpg image in the working directory as `final_montage.jpg`.

## Questions

If you run into issues with these scripts, please feel free to open an Issue in GitHub, and I'll get back to you as quickly as I can.  Thanks for your interest!

> Written with [StackEdit](https://stackedit.io/).
