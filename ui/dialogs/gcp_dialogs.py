# -*- coding: utf-8 -*-
"""GCP related dialogs."""
import os
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QFormLayout, QLineEdit,
    QDoubleSpinBox, QCheckBox, QDialogButtonBox,
    QRadioButton, QButtonGroup, QScrollArea
)
from qgis.PyQt.QtCore import Qt, QTimer, pyqtSignal
from qgis.PyQt.QtGui import QPixmap, QPainter, QPen, QColor, QCursor
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker

class GCPImagePickerDialog(QDialog):
    point_selected = pyqtSignal(float, float, str)

    def __init__(self, image_path, parent=None, gcp_mode=True):
        super().__init__(parent)
        self.image_path = image_path
        self.gcp_mode = gcp_mode
        self.selected_point = None
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.setWindowTitle(f'Select GCP Point - {os.path.basename(image_path)}')
        self.setMinimumSize(600, 500)
        self.resize(900, 700)
        self._setup_ui()
        QTimer.singleShot(100, self.fit_to_window)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        toolbar = QHBoxLayout()
        zoom_in_btn = QPushButton('+')
        zoom_in_btn.setFixedWidth(30)
        zoom_in_btn.setToolTip('Zoom In')
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton('-')
        zoom_out_btn.setFixedWidth(30)
        zoom_out_btn.setToolTip('Zoom Out')
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar.addWidget(zoom_out_btn)

        fit_btn = QPushButton('Fit')
        fit_btn.setToolTip('Fit to Window')
        fit_btn.clicked.connect(self.fit_to_window)
        toolbar.addWidget(fit_btn)

        actual_btn = QPushButton('100%')
        actual_btn.setToolTip('Actual Size')
        actual_btn.clicked.connect(self.actual_size)
        toolbar.addWidget(actual_btn)
        toolbar.addStretch()

        self.info_label = QLabel('Click on the image to mark GCP point')
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        toolbar.addWidget(self.info_label)
        layout.addLayout(toolbar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setStyleSheet("QScrollArea { background-color: #1a1a1a; }")

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("QLabel { background-color: #1a1a1a; }")
        self.image_label.setMouseTracking(True)

        self.original_pixmap = QPixmap(self.image_path)
        if self.original_pixmap.isNull():
            self.image_label.setText(f'Failed to load: {os.path.basename(self.image_path)}')
        else:
            self.image_label.setPixmap(self.original_pixmap)
            self.original_size = self.original_pixmap.size()

        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        point_layout = QHBoxLayout()
        self.point_label = QLabel('Pixel: --')
        self.point_label.setStyleSheet("font-weight: bold; color: #007bff;")
        point_layout.addWidget(self.point_label)
        point_layout.addStretch()
        layout.addLayout(point_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.confirm_btn = QPushButton('Confirm Point')
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setStyleSheet("QPushButton:enabled { background-color: #28a745; color: white; font-weight: bold; }")
        self.confirm_btn.clicked.connect(self.confirm_point)
        button_layout.addWidget(self.confirm_btn)
        layout.addLayout(button_layout)

        self.image_label.mousePressEvent = self.on_mouse_press
        self.image_label.wheelEvent = self.on_wheel

    def on_mouse_press(self, event):
        if event.button() == Qt.LeftButton and not self.original_pixmap.isNull():
            label_pos = self.image_label.mapFrom(self, event.pos())
            current_pixmap = self.image_label.pixmap()
            if current_pixmap:
                offset_x = (self.image_label.width() - current_pixmap.width()) / 2
                offset_y = (self.image_label.height() - current_pixmap.height()) / 2
                img_x = label_pos.x() - offset_x
                img_y = label_pos.y() - offset_y
                if 0 <= img_x <= current_pixmap.width() and 0 <= img_y <= current_pixmap.height():
                    scale_x = self.original_pixmap.width() / current_pixmap.width()
                    scale_y = self.original_pixmap.height() / current_pixmap.height()
                    self.selected_point = (img_x * scale_x, img_y * scale_y)
                    self.point_label.setText(f'Pixel: ({self.selected_point[0]:.1f}, {self.selected_point[1]:.1f})')
                    self.confirm_btn.setEnabled(True)
                    self.draw_marker()

    def on_wheel(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()

    def draw_marker(self):
        if not self.selected_point or self.original_pixmap.isNull():
            return
        marker_pixmap = QPixmap(self.original_pixmap)
        painter = QPainter(marker_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(255, 0, 0), 3)
        painter.setPen(pen)
        x, y = int(self.selected_point[0]), int(self.selected_point[1])
        size = 20
        painter.drawLine(x - size, y, x + size, y)
        painter.drawLine(x, y - size, x, y + size)
        painter.drawEllipse(x - size//2, y - size//2, size, size)
        painter.end()
        scaled = marker_pixmap.scaled(
            int(self.original_size.width() * self.zoom_factor),
            int(self.original_size.height() * self.zoom_factor),
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        self.image_label.resize(scaled.size())

    def zoom_in(self):
        self.zoom_factor = min(self.max_zoom, self.zoom_factor * 1.25)
        self.update_image()

    def zoom_out(self):
        self.zoom_factor = max(self.min_zoom, self.zoom_factor / 1.25)
        self.update_image()

    def fit_to_window(self):
        if self.original_pixmap.isNull():
            return
        viewport = self.scroll_area.viewport()
        max_width = viewport.width() - 20
        max_height = viewport.height() - 20
        scale_w = max_width / self.original_pixmap.width()
        scale_h = max_height / self.original_pixmap.height()
        self.zoom_factor = min(scale_w, scale_h)
        self.update_image()

    def actual_size(self):
        self.zoom_factor = 1.0
        self.update_image()

    def update_image(self):
        if self.original_pixmap.isNull():
            return
        new_width = int(self.original_pixmap.width() * self.zoom_factor)
        new_height = int(self.original_pixmap.height() * self.zoom_factor)
        scaled = self.original_pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        self.image_label.resize(scaled.size())
        if self.selected_point:
            self.draw_marker()

    def confirm_point(self):
        if self.selected_point:
            self.point_selected.emit(self.selected_point[0], self.selected_point[1], self.image_path)
            self.accept()

class GCPMapTool(QgsMapToolEmitPoint):
    point_picked = pyqtSignal(float, float)

    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.setCursor(QCursor(Qt.CrossCursor))

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            point = self.toMapCoordinates(event.pos())
            self.point_picked.emit(point.x(), point.y())
            marker = QgsVertexMarker(self.canvas)
            marker.setCenter(point)
            marker.setIconType(QgsVertexMarker.ICON_CROSS)
            marker.setColor(QColor(255, 0, 0))
            marker.setIconSize(15)
            marker.setPenWidth(2)
            QTimer.singleShot(2000, lambda: self.canvas.scene().removeItem(marker))

class GCPSelectorDialog(QDialog):
    def __init__(self, pixel_x, pixel_y, filename, gcp_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add to GCP')
        self.setMinimumWidth(350)
        self.setModal(True)
        self.selected_gcp_id = None
        self.create_new = False
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info_group = QGroupBox('Image Point')
        info_layout = QVBoxLayout(info_group)
        info_layout.addWidget(QLabel(f'File: {filename}'))
        info_layout.addWidget(QLabel(f'Pixel: ({pixel_x:.1f}, {pixel_y:.1f})'))
        layout.addWidget(info_group)

        select_group = QGroupBox('Select GCP')
        select_layout = QVBoxLayout(select_group)
        self.button_group = QButtonGroup(self)

        new_radio = QRadioButton('+ Create New GCP')
        new_radio.setStyleSheet("font-weight: bold; color: #28a745;")
        new_radio.setChecked(True)
        self.button_group.addButton(new_radio, -1)
        select_layout.addWidget(new_radio)

        for gcp in gcp_list:
            gcp_name = gcp.get('gcp_name', f"GCP {gcp['id']}")
            img_count = len(gcp.get('image_points', []))
            world_coords = f"({gcp['world_x']:.2f}, {gcp['world_y']:.2f})"
            radio = QRadioButton(f"{gcp_name} - World: {world_coords}")
            radio.setToolTip(f"{img_count} image point(s)")
            self.button_group.addButton(radio, gcp['id'])
            select_layout.addWidget(radio)

        layout.addWidget(select_group)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        add_btn = QPushButton('Add to GCP')
        add_btn.setStyleSheet("QPushButton { background-color: #007bff; color: white; font-weight: bold; }")
        add_btn.clicked.connect(self.accept)
        button_layout.addWidget(add_btn)
        layout.addLayout(button_layout)

    def get_selection(self):
        checked_id = self.button_group.checkedId()
        if checked_id == -1:
            return (None, True)
        else:
            return (checked_id, False)

class GCPPropertiesDialog(QDialog):
    def __init__(self, pixel_x, pixel_y, filename, default_x=0, default_y=0, parent=None, iface=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle('New GCP')
        self.setMinimumWidth(400)
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        img_group = QGroupBox('Image Point')
        img_layout = QFormLayout(img_group)
        img_layout.addRow('File:', QLabel(filename))
        img_layout.addRow('Pixel:', QLabel(f'({pixel_x:.1f}, {pixel_y:.1f})'))
        layout.addWidget(img_group)

        world_group = QGroupBox('World Coordinates')
        world_layout = QFormLayout(world_group)

        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-999999999, 999999999)
        self.x_spin.setDecimals(6)
        self.x_spin.setValue(default_x)
        self.x_spin.setMinimumWidth(150)
        world_layout.addRow('X (Easting/Longitude):', self.x_spin)

        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-999999999, 999999999)
        self.y_spin.setDecimals(6)
        self.y_spin.setValue(default_y)
        self.y_spin.setMinimumWidth(150)
        world_layout.addRow('Y (Northing/Latitude):', self.y_spin)

        z_layout = QHBoxLayout()
        self.z_spin = QDoubleSpinBox()
        self.z_spin.setRange(-99999, 99999)
        self.z_spin.setDecimals(3)
        self.z_spin.setValue(0)

        from_dem_btn = QPushButton('From DEM')
        from_dem_btn.setToolTip('Extract elevation from loaded DEM layer')
        from_dem_btn.clicked.connect(self.extract_z_from_dem)
        z_layout.addWidget(self.z_spin)
        z_layout.addWidget(from_dem_btn)
        z_layout.addStretch()
        world_layout.addRow('Z (Elevation):', z_layout)
        layout.addWidget(world_group)

        prop_group = QGroupBox('GCP Properties')
        prop_layout = QFormLayout(prop_group)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('e.g., GCP01')
        prop_layout.addRow('GCP Name:', self.name_edit)

        self.checkpoint_check = QCheckBox('Mark as Checkpoint')
        self.checkpoint_check.setToolTip('Checkpoints are used for accuracy verification')
        prop_layout.addRow('', self.checkpoint_check)
        layout.addWidget(prop_group)

        hint = QLabel('Tip: Click on the map to set world coordinates')
        hint.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(hint)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        create_btn = QPushButton('Create GCP')
        create_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; font-weight: bold; }")
        create_btn.clicked.connect(self.accept)
        button_layout.addWidget(create_btn)
        layout.addLayout(button_layout)

    def extract_z_from_dem(self):
        if not self.iface:
            QMessageBox.warning(self, 'Error', 'Cannot access DEM layers')
            return
        from qgis.core import QgsProject, QgsPointXY
        layers = QgsProject.instance().mapLayers().values()
        dem_layers = [l for l in layers if l.type() == 1 and l.bandCount() == 1]
        if not dem_layers:
            QMessageBox.warning(self, 'No DEM', 'Load a DEM first.')
            return
        if len(dem_layers) == 1:
            dem = dem_layers[0]
        else:
            names = [l.name() for l in dem_layers]
            from qgis.PyQt.QtWidgets import QInputDialog
            name, ok = QInputDialog.getItem(self, 'Select DEM', 'Choose DEM layer:', names, 0, False)
            if not ok or not name:
                return
            dem = next(l for l in dem_layers if l.name() == name)
        try:
            x = self.x_spin.value()
            y = self.y_spin.value()
            point = QgsPointXY(x, y)
            results = dem.dataProvider().identify(point, 1)
            if results.isValid():
                z = results.results()[1]
                self.z_spin.setValue(float(z))
                QMessageBox.information(self, 'Success', f'Extracted elevation: {z:.3f}')
            else:
                QMessageBox.warning(self, 'Error', 'Could not sample DEM')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed: {str(e)}')

    def get_gcp_data(self):
        return {
            'world_x': self.x_spin.value(),
            'world_y': self.y_spin.value(),
            'world_z': self.z_spin.value(),
            'gcp_name': self.name_edit.text().strip() or None,
            'is_checkpoint': self.checkpoint_check.isChecked()
        }
