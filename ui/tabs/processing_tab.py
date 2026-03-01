# -*- coding: utf-8 -*-
"""Processing tab UI and logic."""
import os
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QComboBox, QCheckBox,
    QTextEdit, QFileDialog, QMessageBox, QMenu, QAction,
    QSpinBox, QScrollArea, QGridLayout
)
from qgis.PyQt.QtCore import Qt
from ...utils.presets import get_preset_names, get_preset_config

class ProcessingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_dialog = parent
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        project_group = QGroupBox('Project Settings')
        project_grid = QGridLayout()
        project_grid.setContentsMargins(5, 5, 5, 5)
        project_grid.setSpacing(3)
        project_grid.addWidget(QLabel('Processing Preset:'), 0, 0)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(get_preset_names())
        self.preset_combo.setCurrentText('Default')
        self.preset_combo.currentTextChanged.connect(self._apply_preset)
        self.preset_combo.setToolTip('Choose a processing preset')
        self.preset_combo.setMaximumWidth(180)
        project_grid.addWidget(self.preset_combo, 0, 1)
        project_group.setLayout(project_grid)
        layout.addWidget(project_group)

        output_group = QGroupBox('Output Products')
        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(5, 5, 5, 5)
        output_layout.setSpacing(3)
        desc = QLabel('Select outputs:')
        desc.setStyleSheet("font-size: 11px; color: #666;")
        output_layout.addWidget(desc)
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setSpacing(8)
        self.orthophoto_checkbox = QCheckBox('Orthophoto')
        self.orthophoto_checkbox.setChecked(True)
        self.orthophoto_checkbox.setToolTip('Generate georeferenced orthophoto')
        self.dsm_checkbox = QCheckBox('DSM')
        self.dsm_checkbox.setToolTip('Digital Surface Model')
        self.dtm_checkbox = QCheckBox('DTM')
        self.dtm_checkbox.setToolTip('Digital Terrain Model')
        checkbox_layout.addWidget(self.orthophoto_checkbox)
        checkbox_layout.addWidget(self.dsm_checkbox)
        checkbox_layout.addWidget(self.dtm_checkbox)
        checkbox_layout.addStretch()
        output_layout.addLayout(checkbox_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        images_group = QGroupBox('Input Images')
        images_layout = QVBoxLayout()
        images_layout.setContentsMargins(5, 5, 5, 5)
        images_layout.setSpacing(3)
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel('Images:'))
        self.images_count_label = QLabel('0')
        self.images_count_label.setStyleSheet("font-weight: bold; color: #007bff;")
        info_layout.addWidget(self.images_count_label)
        info_layout.addStretch()
        images_layout.addLayout(info_layout)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(3)
        self.add_images_btn = QPushButton('📁 Add')
        self.add_images_btn.setMaximumWidth(70)
        self.add_menu = QMenu(self)
        add_files_action = QAction('Add Files', self)
        add_files_action.triggered.connect(self._add_from_files)
        add_dir_action = QAction('Add Directory', self)
        add_dir_action.triggered.connect(self._add_from_directory)
        self.add_menu.addAction(add_files_action)
        self.add_menu.addAction(add_dir_action)
        self.add_images_btn.setMenu(self.add_menu)
        clear_btn = QPushButton('🗑️ Clear')
        clear_btn.setMaximumWidth(70)
        clear_btn.clicked.connect(self._clear_images)
        button_layout.addWidget(self.add_images_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        images_layout.addLayout(button_layout)
        images_group.setLayout(images_layout)
        layout.addWidget(images_group)

        control_group = QGroupBox('Processing Control')
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(3)
        button_grid = QHBoxLayout()
        button_grid.setSpacing(5)
        self.start_btn = QPushButton('🚀 Start')
        self.start_btn.clicked.connect(self._start_processing)
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("""
            QPushButton { font-weight: bold; font-size: 11px; padding: 6px 12px;
                background-color: #28a745; color: white;
                border: none; border-radius: 3px; min-width: 80px; }
            QPushButton:hover { background-color: #218838; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.stop_btn = QPushButton('🛑 Stop')
        self.stop_btn.clicked.connect(self._stop_task)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton { font-weight: bold; font-size: 11px; padding: 6px 12px;
                background-color: #dc3545; color: white;
                border: none; border-radius: 3px; min-width: 80px; }
            QPushButton:hover { background-color: #c82333; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        button_grid.addWidget(self.start_btn)
        button_grid.addWidget(self.stop_btn)
        button_grid.addStretch()
        control_layout.addLayout(button_grid)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        status_group = QGroupBox('Processing Status')
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(5, 5, 5, 5)
        status_layout.setSpacing(3)
        self.status_text = QTextEdit()
        self.status_text.setMinimumHeight(50)
        self.status_text.setMaximumHeight(80)
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("""
            QTextEdit { font-family: 'Courier New', monospace; font-size: 8px;
                background-color: #f8f9fa; border: 1px solid #dee2e6; }
        """)
        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def _apply_preset(self, preset_name):
        if preset_name == 'Custom':
            return
        config = get_preset_config(preset_name)
        if not config:
            return
        self.parent_dialog.apply_preset_config(config)
        self.status_text.append(f'✓ Applied {preset_name} preset')

    def _add_from_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 'Select Images', '',
            'Image files (*.jpg *.jpeg *.png *.tif *.tiff)'
        )
        if files:
            self.parent_dialog.image_paths.extend(files)
            self.parent_dialog.update_images_display()

    def _add_from_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            exts = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')
            count = 0
            for f in os.listdir(directory):
                if f.lower().endswith(exts):
                    self.parent_dialog.image_paths.append(os.path.join(directory, f))
                    count += 1
            if count > 0:
                self.parent_dialog.update_images_display()
            else:
                QMessageBox.information(self, 'No Images', 'No images found.')

    def _clear_images(self):
        self.parent_dialog.image_paths.clear()
        if hasattr(self.parent_dialog, 'photos_dock'):
            self.parent_dialog.photos_dock.set_image_paths([])
        self.parent_dialog.update_images_display()

    def _start_processing(self):
        self.parent_dialog.start_task_processing()

    def _stop_task(self):
        self.parent_dialog.stop_task()

    def update_count(self, count):
        self.images_count_label.setText(str(count))
        self.start_btn.setEnabled(count > 0)
