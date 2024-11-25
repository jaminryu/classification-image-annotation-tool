# PyQt Image Annotation Tool
## Forked from robertbrada/PyQt-image-annotation-tool. 
Due to some specific requirements in the project, I have modified the code. I hope these changes can help others with similar needs.

## New features
- [2024/11/25] add a file navigation bar with color-coded labels.
- [2024/11/25] only applicable for one-shot image labeling.
- [2024/11/25] change the default mode to "move".
- [2024/11/25] Increase the GUI and image sizes.

This app is used to label images in a given directory.
Labeled images can be moved or copied into sub-directories, which are named as assigned labels.
The app is just a single Python script with GUI.


## What can this app do
For example you have folder ./data/images/ with a lot of images and you need to assign some
label(s) to these images.

- it can assign multiple labels to one image
- it allows you to choose number and names of your labels
- it can move/copy images to folders that are named as desired labels.
- it can generate .csv file with assigned labels.
- it can generate .xlsx file with assigned labels.
- all settings are handled via GUI

## Installation and usage

1. Clone the project:
    ```bash
    git clone https://github.com/jaminryu/classification-image-annotation-tool
    ```

2. Enter the directory and install the dependencies (you might need to use ```pip3``` instead of ```pip```):
    ```bash
    cd PyQt-image-annotation-tool
    pip install -r requirements.txt
    ```
3. Run the app (use ```python3``` for Python 3)
   ```bash
    python main.py
    ```

## Keyboard shortcuts

- Right Arrow : Next image
- Left Arrow : Previous image
- 1-9: Select label

## Contributing

Pull requests are welcomed.
