import csv
import os
import shutil
import sys

import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIntValidator, QKeySequence, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QCheckBox, QFileDialog, QDesktopWidget, QLineEdit, \
    QRadioButton, QShortcut, QScrollArea, QVBoxLayout, QGroupBox, QFormLayout, QListWidget, QListWidgetItem
from xlsxwriter.workbook import Workbook


def get_img_paths(dir, extensions=('.jpg', '.png', '.jpeg')):
    '''
    :param dir: folder with files
    :param extensions: tuple with file endings. e.g. ('.jpg', '.png'). Files with these endings will be added to img_paths
    :return: list of all filenames
    '''

    img_paths = []

    for filename in os.listdir(dir):
        if filename.lower().endswith(extensions):
            img_paths.append(os.path.join(dir, filename))

    # sort image names
    img_paths.sort()
    return img_paths


def make_folder(directory):
    """
    Make folder if it doesn't already exist
    :param directory: The folder destination path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


class SetupWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Window variables
        self.width = 1600
        self.height = 900

        # State variables
        self.selected_folder = ''
        self.selected_labels = ''
        self.num_labels = 0
        self.label_inputs = []
        self.label_headlines = []
        self.mode = 'move'  # default option

        # Labels
        self.headline_folder = QLabel('1. Select folder containing images you want to label', self)
        self.headline_num_labels = QLabel('3. Specify labels', self)
        self.labels_file_description = QLabel(
            'a) select file with labels (text file containing one label on each line)', self)
        self.labels_inputs_description = QLabel('b) or specify how many unique labels you want to assign', self)

        self.selected_folder_label = QLabel(self)
        self.error_message = QLabel(self)

        # Buttons
        self.browse_button = QtWidgets.QPushButton("Browse", self)
        self.confirm_num_labels = QtWidgets.QPushButton("Ok", self)
        self.next_button = QtWidgets.QPushButton("Next", self)
        self.browse_labels_button = QtWidgets.QPushButton("Select labels", self)

        # Inputs
        self.numLabelsInput = QLineEdit(self)

        # Validation
        self.onlyInt = QIntValidator()

        # layouts
        self.formLayout = QFormLayout()

        # GroupBoxes
        self.groupBox = QGroupBox()

        # Scrolls
        self.scroll = QScrollArea(self)

        # Init
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('PyQt5 - Annotation tool - Parameters setup')
        self.setGeometry(0, 0, self.width, self.height)
        self.centerOnScreen()

        self.headline_folder.setGeometry(20, 30, 500, 20)
        self.headline_folder.setObjectName("headline")

        self.selected_folder_label.setGeometry(20, 60, 550, 26)
        self.selected_folder_label.setObjectName("selectedFolderLabel")

        self.browse_button.setGeometry(580, 60, 80, 28)
        self.browse_button.clicked.connect(self.pick_new)

        # Input number of labels
        top_margin_num_labels = 260
        self.headline_num_labels.move(20, top_margin_num_labels)
        self.headline_num_labels.setObjectName("headline")

        self.labels_file_description.move(20, top_margin_num_labels + 30)
        self.browse_labels_button.setGeometry(480, top_margin_num_labels + 25, 89, 28)

        self.browse_labels_button.clicked.connect(self.pick_labels_file)

        self.labels_inputs_description.move(20, top_margin_num_labels + 60)
        self.numLabelsInput.setGeometry(35, top_margin_num_labels + 90, 60, 26)

        self.numLabelsInput.setValidator(self.onlyInt)
        self.confirm_num_labels.setGeometry(96, top_margin_num_labels + 89, 80, 28)
        self.confirm_num_labels.clicked.connect(self.generate_label_inputs)

        # Next Button
        self.next_button.move(360, 530)
        self.next_button.clicked.connect(self.continue_app)
        self.next_button.setObjectName("blueButton")

        # Error message
        self.error_message.setGeometry(20, 560, self.width - 20, 20)
        self.error_message.setAlignment(Qt.AlignCenter)
        self.error_message.setStyleSheet('color: red; font-weight: bold')

        self.init_radio_buttons()

        # initiate the ScrollArea
        self.scroll.setGeometry(20, 400, 300, 100)

        # apply custom styles
        try:
            styles_path = "./styles.qss"
            with open(styles_path, "r") as fh:
                self.setStyleSheet(fh.read())
        except:
            print("Can't load custom stylesheet.")

    def init_radio_buttons(self):
        """
        Creates section with mode selection
        """

        top_margin = 115
        radio_label = QLabel('2. Select mode', self)
        radio_label.setObjectName("headline")
        radio_label.move(20, top_margin)

        radiobutton = QRadioButton(
            "csv (Images in selected folder are labeled and then csv file with assigned labels is generated.)", self)
        radiobutton.mode = "csv"
        radiobutton.toggled.connect(self.mode_changed)
        radiobutton.move(20, top_margin + 35)

        radiobutton = QRadioButton(
            "copy (Creates folder for each label. Labeled images are copied to these folders. Csv is also generated)",
            self)
        radiobutton.mode = "copy"
        radiobutton.toggled.connect(self.mode_changed)
        radiobutton.move(20, top_margin + 65)

        radiobutton = QRadioButton(
            "move (Creates folder for each label. Labeled images are moved to these folders. Csv is also generated)",
            self)
        radiobutton.setChecked(True)
        radiobutton.mode = "move"
        radiobutton.toggled.connect(self.mode_changed)
        radiobutton.move(20, top_margin + 95)

    def mode_changed(self):
        """
        Sets new mode (one of: csv, copy, move)
        """
        radioButton = self.sender()
        if radioButton.isChecked():
            self.mode = radioButton.mode

    def pick_new(self):
        """
        shows a dialog to choose folder with images to label
        """
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")

        self.selected_folder_label.setText(folder_path)
        self.selected_folder = folder_path

    def pick_labels_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select labels", "",
                                                  "Text files (*.txt)", options=options)
        if fileName:
            with open(fileName) as f:
                content = f.readlines()

            labels = [line.rstrip('\n') for line in content]

            print(labels)
            self.numLabelsInput.setText(str(len(labels)))
            self.generate_label_inputs()

            # fill the input fields with loaded labels
            for input, label in zip(self.label_inputs, labels):
                input.setText(label)

    def generate_label_inputs(self):
        """
        Generates input fields for labels. The layout depends on the number of labels.
        """

        # check that number of labels is not empty
        if self.numLabelsInput.text().strip() != '':

            # convert string (number of labels) to integer
            self.num_labels = int(self.numLabelsInput.text())

            # delete previously generated widgets
            for input, headline in zip(self.label_inputs, self.label_headlines):
                input.deleteLater()
                headline.deleteLater()

            # initialize values
            self.label_inputs = []
            self.label_headlines = []  # labels to label input fields
            margin_top = 400

            # show headline for this step
            self.groupBox.setTitle('4. Fill in the labels and click "Next"')
            self.groupBox.setStyleSheet('font-weight: bold')

            # display input fields
            for i in range(self.num_labels):
                # append widgets to lists
                self.label_inputs.append(QtWidgets.QLineEdit(self))
                self.label_headlines.append(QLabel(f'label {i + 1}:', self))
                self.formLayout.addRow(self.label_headlines[i], self.label_inputs[i])

            self.groupBox.setLayout(self.formLayout)
            self.scroll.setWidget(self.groupBox)
            self.scroll.setWidgetResizable(True)

    def centerOnScreen(self):
        """
        Centers the window on the screen.
        """
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.width / 2)),
                  int((resolution.height() / 2) - (self.height / 2)) - 40)

    def check_validity(self):
        """
        :return: if all the necessary information is provided for proper run of application. And error message
        """
        if self.selected_folder == '':
            return False, 'Input folder has to be selected (step 1)'

        num_labels_input = self.numLabelsInput.text().strip()
        if num_labels_input == '' or num_labels_input == '0':
            return False, 'Number of labels has to be number greater than 0 (step 3).'

        if len(self.label_inputs) == 0:
            return False, "You didn't provide any labels. Select number of labels and press \"Ok\""

        for label in self.label_inputs:
            if label.text().strip() == '':
                return False, 'All label fields has to be filled (step 4).'

        return True, 'Form ok'

    def continue_app(self):
        """
        If the setup form is valid, the LabelerWindow is opened and all necessary information is passed to it
        """
        form_is_valid, message = self.check_validity()

        if form_is_valid:
            label_values = []
            for label in self.label_inputs:
                label_values.append(label.text().strip())

            self.close()
            # show window in full-screen mode (window is maximized)
            LabelerWindow(label_values, self.selected_folder, self.mode).showMaximized()
        else:
            self.error_message.setText(message)


class LabelerWindow(QWidget):
    def __init__(self, labels, input_folder, mode):
        super().__init__()

        # init UI state
        self.title = 'PyQt5 - Annotation tool for assigning image classes'
        self.left = 200
        self.top = 100
        self.width = 1600
        self.height = 1200
        # img panel size should be square-like to prevent some problems with different aspect ratios
        self.img_panel_width = 1100
        self.img_panel_height = 1100

        # state variables
        self.counter = 0
        self.input_folder = input_folder
        self.img_paths = get_img_paths(input_folder)
        self.labels = labels
        self.num_labels = len(self.labels)
        self.num_images = len(self.img_paths)
        self.assigned_labels = {}  # 映射图像名称到标签（字符串）
        self.mode = mode

        # initialize list to save all label buttons
        self.label_buttons = []

        # Initialize Labels
        self.image_box = QLabel(self)
        self.img_name_label = QLabel(self)
        self.progress_bar = QLabel(self)
        self.curr_image_headline = QLabel('Current image', self)
        self.csv_note = QLabel('(csv will be also generated automatically after closing the app)', self)
        self.csv_generated_message = QLabel(self)
        self.show_next_checkbox = QCheckBox("Automatically show next image when labeled", self)
        self.generate_xlsx_checkbox = QCheckBox("Also generate .xlsx file", self)

        # 创建文件导航栏
        self.file_list_widget = QListWidget(self)
        self.file_list_widget.itemClicked.connect(self.on_file_item_clicked)

        # 设置文件导航栏的背景颜色和默认文字颜色
        self.file_list_widget.setStyleSheet("background-color: #333333; color: white;")

        # 创建标签到颜色的映射
        self.label_colors = self.assign_label_colors()

        # create label folders
        if mode == 'copy' or mode == 'move':
            self.create_label_folders(labels, self.input_folder)

        # init UI
        self.init_ui()

    def init_ui(self):

        self.setWindowTitle(self.title)
        self.setMinimumSize(self.width, self.height)  # minimum size of the window

        # create buttons
        self.init_buttons()

        # create 'show next automatically' checkbox
        self.show_next_checkbox.setChecked(False)
        self.show_next_checkbox.setGeometry(self.img_panel_width + 220, 10, 400, 20)

        # "create xlsx" checkbox
        self.generate_xlsx_checkbox.setChecked(False)
        self.generate_xlsx_checkbox.setGeometry(self.img_panel_width + 340, 606, 300, 20)

        # image headline
        self.curr_image_headline.setGeometry(220, 10, 300, 20)
        self.curr_image_headline.setObjectName('headline')

        # image name label
        self.img_name_label.setGeometry(220, 40, self.img_panel_width, 20)

        # progress bar (how many images have I labeled so far)
        self.progress_bar.setGeometry(220, 65, self.img_panel_width, 20)

        # csv note
        self.csv_note.setGeometry(self.img_panel_width + 220, 640, 400, 20)

        # message that csv was generated
        self.csv_generated_message.setGeometry(self.img_panel_width + 220, 660, 800, 20)
        self.csv_generated_message.setStyleSheet('color: #43A047')

        # show image
        self.set_image(self.img_paths[0])
        self.image_box.setGeometry(220, 100, self.img_panel_width, self.img_panel_height)
        self.image_box.setAlignment(Qt.AlignTop)

        # image name
        self.img_name_label.setText(self.img_paths[self.counter])

        # progress bar
        self.progress_bar.setText(f'image 1 of {self.num_images}')

        # draw line for better UX
        ui_line = QLabel(self)
        ui_line.setGeometry(220, 98, self.img_panel_width, 1)
        ui_line.setStyleSheet('background-color: black')

        # file Navigation Bar
        self.file_list_widget.setGeometry(10, 10, 200, self.height - 20)
        self.populate_file_list()

        # apply custom styles
        try:
            styles_path = "./styles.qss"
            with open(styles_path, "r") as fh:
                self.setStyleSheet(fh.read())
        except:
            print("Can't load custom stylesheet.")

    def init_buttons(self):

        # Add "Prev Image" and "Next Image" buttons
        next_prev_top_margin = 50
        prev_im_btn = QtWidgets.QPushButton("Prev", self)
        prev_im_btn.move(self.img_panel_width + 220, next_prev_top_margin)
        prev_im_btn.clicked.connect(self.show_prev_image)

        next_im_btn = QtWidgets.QPushButton("Next", self)
        next_im_btn.move(self.img_panel_width + 340, next_prev_top_margin)
        next_im_btn.clicked.connect(self.show_next_image)

        # Add "Prev Image" and "Next Image" keyboard shortcuts
        prev_im_kbs = QShortcut(QKeySequence("left"), self)
        prev_im_kbs.activated.connect(self.show_prev_image)

        next_im_kbs = QShortcut(QKeySequence("right"), self)
        next_im_kbs.activated.connect(self.show_next_image)

        # Add "generate csv file" button
        next_im_btn = QtWidgets.QPushButton("Generate csv", self)
        next_im_btn.move(self.img_panel_width + 220, 600)
        next_im_btn.clicked.connect(lambda state, filename='assigned_classes': self.generate_csv(filename))
        next_im_btn.setObjectName("blueButton")

        # Create button for each label
        x_shift = 0  # variable that helps to compute x-coordinate of button in UI
        for i, label in enumerate(self.labels):
            self.label_buttons.append(QtWidgets.QPushButton(label, self))
            button = self.label_buttons[i]

            # create click event (set label)
            button.clicked.connect(lambda state, x=label: self.set_label(x))

            # create keyboard shortcut event (set label)
            label_kbs = QShortcut(QKeySequence(f"{(i + 1) % 10}"), self)
            label_kbs.activated.connect(lambda x=label: self.set_label(x))

            # place button in GUI (create multiple columns if there is more than 10 button)
            y_shift = (30 + 10) * (i % 10)
            if (i != 0 and i % 10 == 0):
                x_shift += 120
                y_shift = 0

            button.move(self.img_panel_width + 220 + x_shift, y_shift + 120)

    def assign_label_colors(self):
        """
        assign colors for labels in file navigation bar
        """
        colors = [
            QColor("#3cb44b"),
            QColor("#ffe119"),
            QColor("#e6194b"),
            QColor("#4363d8"),
            QColor("#f58231"),
            QColor("#911eb4"),
            QColor("#42d4f4"),
            QColor("#f032e6"),
            QColor("#bfef45"),
            QColor("#fabebe"),
            QColor("#469990"),
            QColor("#e6beff"),
            QColor("#9a6324"),
            QColor("#fffac8"),
            QColor("#800000"),
            QColor("#aaffc3"),
            QColor("#808000"),
            QColor("#ffd8b1"),
            QColor("#000075"),
            QColor("#808080"),
        ]
        label_colors = {}
        for i, label in enumerate(self.labels):
            label_colors[label] = colors[i % len(colors)]
        return label_colors

    def set_label(self, label):
        """
        Sets the label for just loaded image
        :param label: selected label
        """

        img_path = self.img_paths[self.counter]
        img_name = os.path.split(img_path)[-1]

        if img_name in self.assigned_labels:
            previous_label = self.assigned_labels[img_name]

            if label == previous_label:
                del self.assigned_labels[img_name]

                if self.mode == 'copy':
                    os.remove(os.path.join(self.input_folder, label, img_name))
                elif self.mode == 'move':
                    shutil.move(os.path.join(self.input_folder, label, img_name), self.input_folder)
            else:
                if self.mode == 'copy':
                    os.remove(os.path.join(self.input_folder, previous_label, img_name))
                    shutil.copy(img_path, os.path.join(self.input_folder, label))
                elif self.mode == 'move':
                    shutil.move(os.path.join(self.input_folder, previous_label, img_name),
                                os.path.join(self.input_folder, label, img_name))
                self.assigned_labels[img_name] = label
        else:
            self.assigned_labels[img_name] = label
            if self.mode == 'copy':
                shutil.copy(img_path, os.path.join(self.input_folder, label))
            elif self.mode == 'move':
                shutil.move(img_path, os.path.join(self.input_folder, label))

        self.update_file_list_item(self.counter)

        if self.show_next_checkbox.isChecked():
            self.show_next_image()
        else:
            self.set_button_color(img_name)

    def show_next_image(self):
        """
        loads and shows next image in dataset
        """
        if self.counter < self.num_images - 1:
            self.counter += 1

            path = self.img_paths[self.counter]
            filename = os.path.split(path)[-1]

            # If we have already assigned label to this image and mode is 'move', change the input path.
            if self.mode == 'move' and filename in self.assigned_labels:
                label = self.assigned_labels[filename]
                path = os.path.join(self.input_folder, label, filename)

            self.set_image(path)
            self.img_name_label.setText(path)
            self.progress_bar.setText(f'image {self.counter + 1} of {self.num_images}')
            self.set_button_color(filename)
            self.csv_generated_message.setText('')

            self.file_list_widget.setCurrentRow(self.counter)

        # change button color if this is last image in dataset
        elif self.counter == self.num_images - 1:
            path = self.img_paths[self.counter]
            self.set_button_color(os.path.split(path)[-1])

    def show_prev_image(self):
        """
        loads and shows previous image in dataset
        """
        if self.counter > 0:
            self.counter -= 1

            if self.counter < self.num_images:
                path = self.img_paths[self.counter]
                filename = os.path.split(path)[-1]

                # If we have already assigned label to this image and mode is 'move', change the input path.
                if self.mode == 'move' and filename in self.assigned_labels:
                    label = self.assigned_labels[filename]
                    path = os.path.join(self.input_folder, label, filename)

                self.set_image(path)
                self.img_name_label.setText(path)
                self.progress_bar.setText(f'image {self.counter + 1} of {self.num_images}')

                self.set_button_color(filename)
                self.csv_generated_message.setText('')

                self.file_list_widget.setCurrentRow(self.counter)

    def set_image(self, path):
        """
        displays the image in GUI
        :param path: relative path to the image that should be show
        """

        pixmap = QPixmap(path)

        # get original image dimensions
        img_width = pixmap.width()
        img_height = pixmap.height()

        # scale the image properly so it fits into the image window ()
        margin = 20
        if img_width >= img_height:
            pixmap = pixmap.scaledToWidth(self.img_panel_width - margin, Qt.SmoothTransformation)

        else:
            pixmap = pixmap.scaledToHeight(self.img_panel_height - margin, Qt.SmoothTransformation)

        self.image_box.setPixmap(pixmap)

    def generate_csv(self, out_filename):
        """
        Generates and saves csv file with assigned labels.
        Assigned label is represented as one-hot vector.
        :param out_filename: name of csv file to be generated
        """
        path_to_save = os.path.join(self.input_folder, 'output')
        make_folder(path_to_save)
        csv_file_path = os.path.join(path_to_save, out_filename) + '.csv'

        with open(csv_file_path, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')

            # write header
            writer.writerow(['img'] + self.labels)

            # write one-hot labels
            for img_name, label in self.assigned_labels.items():
                labels_one_hot = self.labels_to_zero_one(label)
                writer.writerow([img_name] + list(labels_one_hot))

        message = f'csv saved to: {csv_file_path}'
        self.csv_generated_message.setText(message)
        print(message)

        if self.generate_xlsx_checkbox.isChecked():
            try:
                self.csv_to_xlsx(csv_file_path)
            except:
                print('Generating xlsx file failed.')

    def csv_to_xlsx(self, csv_file_path):
        """
        converts csv file to xlsx file
        :param csv_file_path: path to csv file which we want to convert to xlsx
        """
        workbook = Workbook(csv_file_path[:-4] + '.xlsx')
        worksheet = workbook.add_worksheet()

        with open(csv_file_path, 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)

        workbook.close()

    def set_button_color(self, filename):
        """
        update colors
        """

        if filename in self.assigned_labels:
            assigned_label = self.assigned_labels[filename]
        else:
            assigned_label = None

        for button in self.label_buttons:
            if button.text() == assigned_label:
                button.setStyleSheet('border: 1px solid #43A047; background-color: #4CAF50; color: white')
            else:
                button.setStyleSheet('background-color: None')

    def closeEvent(self, event):
        """
        This function is executed when the app is closed.
        It automatically generates csv file in case the user forgot to do that
        """
        print("closing the App..")
        self.generate_csv('assigned_classes_automatically_generated')

    def labels_to_zero_one(self, label):
        """
        change the label to one-hot vector
        """
        label_to_int = dict((c, i) for i, c in enumerate(self.labels))
        zero_one_arr = np.zeros([self.num_labels], dtype=int)
        if label in label_to_int:
            zero_one_arr[label_to_int[label]] = 1
        return zero_one_arr

    @staticmethod
    def create_label_folders(labels, folder):
        for label in labels:
            make_folder(os.path.join(folder, label))

    def populate_file_list(self):
        """
        populate file list
        """
        for idx, img_path in enumerate(self.img_paths):
            img_name = os.path.split(img_path)[-1]
            item = QListWidgetItem(img_name)
            self.file_list_widget.addItem(item)
            self.update_file_list_item(idx)

        self.file_list_widget.setCurrentRow(self.counter)

    def update_file_list_item(self, idx):
        """
        update file list item
        """
        item = self.file_list_widget.item(idx)
        img_path = self.img_paths[idx]
        img_name = os.path.split(img_path)[-1]

        if img_name in self.assigned_labels:
            # labeled
            label = self.assigned_labels[img_name]
            color = self.label_colors.get(label, Qt.white)
            item.setForeground(color)
        else:
            # unlabeled
            item.setForeground(Qt.white)

    def on_file_item_clicked(self, item):
        """
        When clicking on an item in the file list, the corresponding image is displayed
        """
        img_name = item.text()
        img_path = os.path.join(self.input_folder, img_name)
        if not os.path.exists(img_path):
            if img_name in self.assigned_labels:
                label = self.assigned_labels[img_name]
                img_path = os.path.join(self.input_folder, label, img_name)
            else:
                return

        self.counter = self.img_paths.index(os.path.join(self.input_folder, img_name))

        self.set_image(img_path)
        self.img_name_label.setText(img_path)
        self.progress_bar.setText(f'image {self.counter + 1} of {self.num_images}')
        self.set_button_color(img_name)
        self.csv_generated_message.setText('')

    def keyPressEvent(self, event):
        """
        Handle keyboard events and make sure shortcuts are still valid when focus is on a QListWidget
        """
        if event.key() == Qt.Key_Left:
            self.show_prev_image()
        elif event.key() == Qt.Key_Right:
            self.show_next_image()
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    # run the application
    app = QApplication(sys.argv)
    ex = SetupWindow()
    ex.show()
    sys.exit(app.exec_())
