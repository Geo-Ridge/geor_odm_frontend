# -*- coding: utf-8 -*-
"""GCP (Ground Control Points) tab."""
import os
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QListWidget, QLineEdit,
    QFormLayout, QGridLayout, QFileDialog, QMessageBox,
    QScrollArea, QDialog, QDoubleSpinBox, QCheckBox
)
from qgis.PyQt.QtCore import Qt
from ...utils.helpers import is_projection_line
from ...ui.dialogs.gcp_dialogs import GCPImagePickerDialog

class GCPTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_dialog = parent
        self.gcp_points = []
        self.current_gcp_file = None
        self.gcp_projection = None
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        file_group = QGroupBox('GCP File')
        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(5, 5, 5, 5)
        file_layout.setSpacing(3)
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText('GCP file path (.txt or .csv)')
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setMaximumHeight(25)
        file_layout.addWidget(self.file_path_edit)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(3)
        self.load_btn = QPushButton('Load')
        self.load_btn.setMaximumWidth(60)
        self.load_btn.clicked.connect(self.load_gcp_file)
        self.save_btn = QPushButton('Save')
        self.save_btn.setMaximumWidth(60)
        self.save_btn.clicked.connect(self.save_gcp_file)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        file_layout.addLayout(btn_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        crs_group = QGroupBox('Coordinate System')
        crs_layout = QHBoxLayout()
        crs_layout.setContentsMargins(5, 5, 5, 5)
        crs_layout.addWidget(QLabel('CRS:'))
        self.crs_edit = QLineEdit()
        self.crs_edit.setPlaceholderText('EPSG:4326')
        self.crs_edit.setMaximumWidth(100)
        self.crs_edit.setText('EPSG:4326')
        crs_layout.addWidget(self.crs_edit)
        crs_layout.addStretch()
        crs_group.setLayout(crs_layout)
        layout.addWidget(crs_group)

        points_group = QGroupBox('GCP Points')
        points_layout = QVBoxLayout()
        points_layout.setContentsMargins(5, 5, 5, 5)
        points_layout.setSpacing(3)
        self.gcp_list = QListWidget()
        self.gcp_list.setMaximumHeight(80)
        self.gcp_list.setMinimumHeight(50)
        self.gcp_list.itemClicked.connect(self.select_gcp_point)
        points_layout.addWidget(self.gcp_list)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(3)
        self.add_btn = QPushButton('Add')
        self.add_btn.setMaximumWidth(50)
        self.add_btn.clicked.connect(self.add_gcp_point)
        self.edit_btn = QPushButton('Edit')
        self.edit_btn.setMaximumWidth(50)
        self.edit_btn.clicked.connect(self.edit_gcp_point)
        self.edit_btn.setEnabled(False)
        self.remove_btn = QPushButton('Del')
        self.remove_btn.setMaximumWidth(50)
        self.remove_btn.clicked.connect(self.remove_gcp_point)
        self.remove_btn.setEnabled(False)
        controls_layout.addWidget(self.add_btn)
        controls_layout.addWidget(self.edit_btn)
        controls_layout.addWidget(self.remove_btn)
        controls_layout.addStretch()
        points_layout.addLayout(controls_layout)
        points_group.setLayout(points_layout)
        layout.addWidget(points_group)

        images_group = QGroupBox('Image Points')
        images_layout = QVBoxLayout()
        images_layout.setContentsMargins(5, 5, 5, 5)
        images_layout.setSpacing(3)
        self.images_list = QListWidget()
        self.images_list.setMaximumHeight(60)
        self.images_list.setMinimumHeight(40)
        self.images_list.itemDoubleClicked.connect(self.view_image_point)
        images_layout.addWidget(self.images_list)
        img_btn_layout = QHBoxLayout()
        self.add_img_point_btn = QPushButton('+ Add')
        self.add_img_point_btn.setMaximumWidth(60)
        self.add_img_point_btn.setToolTip('Add image point from Photos panel')
        self.add_img_point_btn.clicked.connect(self.add_image_point)
        self.add_img_point_btn.setEnabled(False)
        self.remove_img_point_btn = QPushButton('Remove')
        self.remove_img_point_btn.setMaximumWidth(60)
        self.remove_img_point_btn.clicked.connect(self.remove_image_point)
        self.remove_img_point_btn.setEnabled(False)
        img_btn_layout.addWidget(self.add_img_point_btn)
        img_btn_layout.addWidget(self.remove_img_point_btn)
        img_btn_layout.addStretch()
        images_layout.addLayout(img_btn_layout)
        images_group.setLayout(images_layout)
        layout.addWidget(images_group)

        info_group = QGroupBox('Point Info')
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(2)
        info_grid = QGridLayout()
        info_grid.setSpacing(2)
        info_grid.addWidget(QLabel('ID:'), 0, 0)
        self.id_label = QLabel('-')
        info_grid.addWidget(self.id_label, 0, 1)
        info_grid.addWidget(QLabel('World:'), 1, 0)
        self.world_label = QLabel('-, -, -')
        info_grid.addWidget(self.world_label, 1, 1)
        info_grid.addWidget(QLabel('Name:'), 2, 0)
        self.name_label = QLabel('-')
        info_grid.addWidget(self.name_label, 2, 1)
        info_grid.addWidget(QLabel('Checkpoint:'), 3, 0)
        self.checkpoint_label = QLabel('No')
        info_grid.addWidget(self.checkpoint_label, 3, 1)
        info_layout.addLayout(info_grid)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def load_gcp_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Load GCP File', '', 'GCP Files (*.txt);;All Files (*.*)'
        )
        if not file_path:
            return
        try:
            gcp_dict = {}
            self.gcp_projection = None
            with open(file_path, 'r') as f:
                lines = f.readlines()
            if not lines:
                QMessageBox.warning(self, 'Empty File', 'File is empty.')
                return
            first_line = lines[0].strip()
            if is_projection_line(first_line):
                self.gcp_projection = first_line
                self.crs_edit.setText(first_line)
                data_lines = lines[1:]
            else:
                self.gcp_projection = 'EPSG:4326'
                self.crs_edit.setText('EPSG:4326')
                data_lines = lines
            for line_num, line in enumerate(data_lines, start=2):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        world_x = float(parts[0])
                        world_y = float(parts[1])
                        world_z = float(parts[2])
                        image_x = float(parts[3])
                        image_y = float(parts[4])
                        filename = parts[5]
                        gcp_name = parts[6] if len(parts) > 6 else f"GCP_{len(gcp_dict) + 1}"
                        if gcp_name not in gcp_dict:
                            gcp_dict[gcp_name] = {
                                'id': len(gcp_dict) + 1,
                                'world_x': world_x,
                                'world_y': world_y,
                                'world_z': world_z,
                                'gcp_name': gcp_name,
                                'is_checkpoint': False,
                                'image_points': []
                            }
                        gcp_dict[gcp_name]['image_points'].append({
                            'filename': filename,
                            'x': image_x,
                            'y': image_y
                        })
                    except ValueError as e:
                        print(f"Error parsing line {line_num}: {e}")
            self.gcp_points = list(gcp_dict.values())
            if self.gcp_points:
                self.current_gcp_file = file_path
                self.file_path_edit.setText(file_path)
                self.update_gcp_list()
                total = sum(len(g['image_points']) for g in self.gcp_points)
                QMessageBox.information(self, 'Success', f'Loaded {len(self.gcp_points)} GCPs with {total} image points')
            else:
                QMessageBox.warning(self, 'No GCPs', 'No valid GCP points found.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load GCP file: {str(e)}')

    def save_gcp_file(self):
        if not self.gcp_points:
            QMessageBox.warning(self, 'Warning', 'No GCP points to save.')
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Save GCP File', '', 'GCP Files (*.txt);;All Files (*.*)'
        )
        if not file_path:
            return
        try:
            crs_text = self.crs_edit.text().strip() or 'EPSG:4326'
            with open(file_path, 'w') as f:
                f.write(f"{crs_text}\n")
                f.write('# GCP file generated by ODM Frontend\n')
                f.write('# Format: geo_x geo_y geo_z im_x im_y filename gcp_name\n')
                for gcp in self.gcp_points:
                    for img_pt in gcp.get('image_points', []):
                        fields = [
                            f"{gcp['world_x']}",
                            f"{gcp['world_y']}",
                            f"{gcp['world_z']}",
                            f"{img_pt['x']}",
                            f"{img_pt['y']}",
                            img_pt['filename'],
                            gcp.get('gcp_name', f"GCP{gcp['id']}")
                        ]
                        f.write('\t'.join(fields) + '\n')
            self.current_gcp_file = file_path
            self.file_path_edit.setText(file_path)
            total = sum(len(g.get('image_points', [])) for g in self.gcp_points)
            QMessageBox.information(self, 'Success', f'Saved {len(self.gcp_points)} GCPs with {total} image points')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save GCP file: {str(e)}')

    def update_gcp_list(self):
        self.gcp_list.clear()
        for gcp in self.gcp_points:
            name = gcp.get('gcp_name', f"GCP{gcp['id']}")
            count = len(gcp.get('image_points', []))
            checkpoint = " [Checkpoint]" if gcp.get('is_checkpoint') else ""
            self.gcp_list.addItem(f"{name} ({count} images){checkpoint}")

    def select_gcp_point(self, item):
        row = self.gcp_list.row(item)
        if 0 <= row < len(self.gcp_points):
            gcp = self.gcp_points[row]
            name = gcp.get('gcp_name', f"GCP{gcp['id']}")
            self.id_label.setText(f"ID: {gcp['id']}")
            self.world_label.setText(f"{gcp['world_x']:.2f}, {gcp['world_y']:.2f}, {gcp['world_z']:.2f}")
            self.name_label.setText(name)
            self.checkpoint_label.setText("Yes" if gcp.get('is_checkpoint') else "No")
            self.edit_btn.setEnabled(True)
            self.remove_btn.setEnabled(True)
            self.add_img_point_btn.setEnabled(True)
            self.update_images_list(gcp)

    def update_images_list(self, gcp):
        self.images_list.clear()
        for img_pt in gcp.get('image_points', []):
            text = f"{img_pt['filename']}: ({img_pt['x']:.1f}, {img_pt['y']:.1f})"
            self.images_list.addItem(text)
        has_images = len(gcp.get('image_points', [])) > 0
        self.remove_img_point_btn.setEnabled(has_images)

    def add_gcp_point(self):
        if not self.parent_dialog.image_paths:
            QMessageBox.warning(self, 'No Images', 'Add images first.')
            return
        QMessageBox.information(self, 'Add GCP', 'Double-click an image in Photos panel to mark a GCP point.')

    def add_image_point(self):
        if not self.gcp_list.currentItem():
            return
        QMessageBox.information(self, 'Add Image Point', 'Double-click an image in Photos panel to mark another point.')

    def edit_gcp_point(self):
        current = self.gcp_list.currentItem()
        if not current:
            return
        row = self.gcp_list.row(current)
        if 0 <= row < len(self.gcp_points):
            gcp = self.gcp_points[row]
            dialog = QDialog(self)
            dialog.setWindowTitle(f'Edit {gcp.get("gcp_name", "GCP")}')
            dialog.setModal(True)
            layout = QFormLayout(dialog)
            from qgis.PyQt.QtWidgets import QLineEdit, QDialogButtonBox
            name_edit = QLineEdit(gcp.get('gcp_name', ''))
            layout.addRow('Name:', name_edit)
            x_spin = QDoubleSpinBox()
            x_spin.setRange(-999999999, 999999999)
            x_spin.setDecimals(6)
            x_spin.setValue(gcp['world_x'])
            layout.addRow('X:', x_spin)
            y_spin = QDoubleSpinBox()
            y_spin.setRange(-999999999, 999999999)
            y_spin.setDecimals(6)
            y_spin.setValue(gcp['world_y'])
            layout.addRow('Y:', y_spin)
            z_spin = QDoubleSpinBox()
            z_spin.setRange(-99999, 99999)
            z_spin.setDecimals(3)
            z_spin.setValue(gcp['world_z'])
            layout.addRow('Z:', z_spin)
            checkpoint = QCheckBox()
            checkpoint.setChecked(gcp.get('is_checkpoint', False))
            layout.addRow('Checkpoint:', checkpoint)
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)
            if dialog.exec_() == QDialog.Accepted:
                gcp['gcp_name'] = name_edit.text().strip() or gcp.get('gcp_name', f"GCP{gcp['id']}")
                gcp['world_x'] = x_spin.value()
                gcp['world_y'] = y_spin.value()
                gcp['world_z'] = z_spin.value()
                gcp['is_checkpoint'] = checkpoint.isChecked()
                self.update_gcp_list()
                self.select_gcp_point(self.gcp_list.item(row))

    def remove_gcp_point(self):
        current = self.gcp_list.currentItem()
        if not current:
            return
        row = self.gcp_list.row(current)
        if 0 <= row < len(self.gcp_points):
            gcp = self.gcp_points[row]
            name = gcp.get('gcp_name', f"GCP{gcp['id']}")
            reply = QMessageBox.question(self, 'Confirm Delete', f'Delete {name} and all its image points?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.gcp_points.pop(row)
                for i, g in enumerate(self.gcp_points, 1):
                    g['id'] = i
                self.update_gcp_list()
                self._clear_info()

    def remove_image_point(self):
        gcp_item = self.gcp_list.currentItem()
        img_item = self.images_list.currentItem()
        if not gcp_item or not img_item:
            return
        gcp_row = self.gcp_list.row(gcp_item)
        img_row = self.images_list.row(img_item)
        if 0 <= gcp_row < len(self.gcp_points):
            gcp = self.gcp_points[gcp_row]
            if 0 <= img_row < len(gcp.get('image_points', [])):
                gcp['image_points'].pop(img_row)
                self.update_gcp_list()
                self.update_images_list(gcp)

    def view_image_point(self, item):
        gcp_item = self.gcp_list.currentItem()
        if not gcp_item:
            return
        gcp_row = self.gcp_list.row(gcp_item)
        img_row = self.images_list.row(item)
        if 0 <= gcp_row < len(self.gcp_points):
            gcp = self.gcp_points[gcp_row]
            img_points = gcp.get('image_points', [])
            if 0 <= img_row < len(img_points):
                img_pt = img_points[img_row]
                filename = img_pt['filename']
                for path in self.parent_dialog.image_paths:
                    if os.path.basename(path) == filename:
                        viewer = GCPImagePickerDialog(path, self)
                        viewer.selected_point = (img_pt['x'], img_pt['y'])
                        viewer.point_label.setText(f"Pixel: ({img_pt['x']:.1f}, {img_pt['y']:.1f})")
                        viewer.confirm_btn.setEnabled(True)
                        viewer.draw_marker()
                        viewer.exec_()
                        break

    def _clear_info(self):
        self.id_label.setText('ID: -')
        self.world_label.setText('-, -, -')
        self.name_label.setText('-')
        self.checkpoint_label.setText('No')
        self.images_list.clear()
        self.edit_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.add_img_point_btn.setEnabled(False)
        self.remove_img_point_btn.setEnabled(False)
