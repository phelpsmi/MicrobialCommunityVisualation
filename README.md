# The Many Faces of Microbial Communities

Our client requested that we create a tool to visualize microbial population data, which would help her in her research. To that end, we've created a tool that can load QIIME OTU files containing population data, represent the relationships in the data via a 3d model of a human, and display the model on the screen in such a way that the user can compare it with those of other samples. The ultimate goal is for this comparison to help the user find patterns that he or she would normally miss. Over the course of the project, we've gained technical skills, such as working with the Qt UI toolkit and the MakeHuman project, as well as non-technical skill such as reading code and working with a client.

## Installation

`git clone git@github.com:phelpsmi/MicrobialCommunityVisualation.git`

Python 2.7 must be installed. (Python 3 will not work)

## Usage

From the repository run:
`python code/FaceView/main.py`

You will need microbial sample data in the `.otu` file format along with a `.csv` metadata file.
For testing purposes, sample files can be found in the `code/FaceView/` directory.
Further instructions on use can be found in the documentation folder.

## Credits

TODO: Write credits
