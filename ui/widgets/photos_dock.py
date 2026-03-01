# -*- coding: utf-8 -*-
"""Photos dock widget."""
import os
from qgis.PyQt.QtWidgets import (
    QDockWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWidget, QScrollArea, QGridLayout,
    QSizePolicy, QMenu, QAction, QMessageBox, QMainWindow
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QPixmap, QImage, QTransform
from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsMapCanvas, QgsMapToolZoom, QgsMapToolPan

class ImageMapWindow(QMainWindow):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle(f'Image Viewer - {os.path.basename(image_path)}')
        self.setMinimumSize(400, 300)
        self.resize(800, 600)

        self.canvas = QgsMapCanvas(self)
        self.canvas.setCanvasColor(Qt.black)
        self.canvas.enableAntiAliasing(True)
        self.setCentralWidget(self.canvas)

        self.pan_tool = QgsMapToolPan(self.canvas)
        self.zoom_in_tool = QgsMapToolZoom(self.canvas, False)
        self.zoom_out_tool = QgsMapToolZoom(self.canvas, True)

        toolbar = self.addToolBar('Map Tools')
        toolbar.setStyleSheet("QToolBar { spacing: 5px; padding: 5px; }")

        pan_btn = QPushButton('Pan')
        pan_btn.setToolTip('Pan the view')
        pan_btn.clicked.connect(self.activate_pan)
        toolbar.addWidget(pan_btn)

        zoom_in_btn = QPushButton('Zoom In')
        zoom_in_btn.setToolTip('Zoom in')
        zoom_in_btn.clicked.connect(self.activate_zoom_in)
        toolbar.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton('Zoom Out')
        zoom_out_btn.setToolTip('Zoom out')
        zoom_out_btn.clicked.connect(self.activate_zoom_out)
        toolbar.addWidget(zoom_out_btn)

        toolbar.addSeparator()

        zoom_full_btn = QPushButton('Full Extent')
        zoom_full_btn.setToolTip('Zoom to full extent')
        zoom_full_btn.clicked.connect(self.zoom_full)
        toolbar.addWidget(zoom_full_btn)

        self._load_image()
        self.canvas.setMapTool(self.pan_tool)

    def activate_pan(self):
        self.canvas.setMapTool(self.pan_tool)

    def activate_zoom_in(self):
        self.canvas.setMapTool(self.zoom_in_tool)

    def activate_zoom_out(self):
        self.canvas.setMapTool(self.zoom_out_tool)

    def zoom_full(self):
        if self.layer:
            self.canvas.setExtent(self.layer.extent())
            self.canvas.refresh()

    def _load_image(self):
        from qgis.core import QgsRasterLayer
        self.layer = QgsRasterLayer(self.image_path, os.path.basename(self.image_path))
        if not self.layer.isValid():
            QMessageBox.warning(self, 'Error', f'Failed to load: {os.path.basename(self.image_path)}')
            return
        crs = QgsCoordinateReferenceSystem('EPSG:3857')
        self.layer.setCrs(crs)
        self.canvas.setLayers([self.layer])
        self.canvas.setExtent(self.layer.extent())
        self.canvas.refresh()

    def closeEvent(self, event):
        if self.layer:
            del self.layer
        event.accept()

class PhotosDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_dialog = parent
        self.image_paths = []
        self.current_image_index = -1
        self.thumbnail_size = 120
        self.loaded_thumbnails = 0
        self.batch_size = 20
        self.images_first_loaded = False

        self.setObjectName('odm_photos_dock')
        self.setWindowTitle('ODM Photos')
        self.setMinimumWidth(300)
        self.setMinimumHeight(250)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSizeConstraint(QVBoxLayout.SetNoConstraint)

        # Header with menu
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel('Photos'))
        header_layout.addStretch()

        self.menu_btn = QPushButton('☰')
        self.menu_btn.setFixedWidth(30)
        self.menu_btn.setFixedHeight(25)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #007bff;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #0056b3;
                background-color: #f0f0f0;
            }
        """)
        self.menu_btn.setToolTip('Photo options')
        self._create_menu()
        header_layout.addWidget(self.menu_btn)

        layout.addLayout(header_layout)

        # Scroll area for images
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.image_container = QWidget()
        self.image_layout = QGridLayout(self.image_container)
        self.image_layout.setAlignment(Qt.AlignTop)
        self.image_layout.setSpacing(8)
        self.image_layout.setContentsMargins(8, 8, 8, 8)

        self.image_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setWidget(self.image_container)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)

        layout.addWidget(self.scroll_area)

    def _create_menu(self):
        self.photo_menu = QMenu(self)

        gcp_action = QAction('📍 Add GCP Point', self)
        gcp_action.triggered.connect(self.open_gcp_picker_for_selected)
        self.photo_menu.addAction(gcp_action)

        self.photo_menu.addSeparator()

        rotate_left_action = QAction('↺ Rotate Left', self)
        rotate_left_action.triggered.connect(self.rotate_left)
        self.photo_menu.addAction(rotate_left_action)

        rotate_right_action = QAction('↻ Rotate Right', self)
        rotate_right_action.triggered.connect(self.rotate_right)
        self.photo_menu.addAction(rotate_right_action)

        self.photo_menu.addSeparator()

        remove_action = QAction('🗑️ Remove Selected', self)
        remove_action.triggered.connect(self.remove_image)
        self.photo_menu.addAction(remove_action)

        self.photo_menu.addSeparator()

        fit_action = QAction('🔍 Fit to Window', self)
        fit_action.triggered.connect(self.fit_to_window)
        self.photo_menu.addAction(fit_action)

        self.menu_btn.setMenu(self.photo_menu)
        self._enable_menu_actions(False)

    def _enable_menu_actions(self, enabled):
        for action in self.photo_menu.actions():
            text = action.text()
            if any(x in text for x in ['Rotate', 'Remove', 'GCP']):
                action.setEnabled(enabled)

    def open_gcp_picker_for_selected(self):
        if 0 <= self.current_image_index < len(self.image_paths):
            self.open_gcp_picker(self.current_image_index)

    def open_gcp_picker(self, index):
        if 0 <= index < len(self.image_paths):
            from ..dialogs.gcp_dialogs import GCPImagePickerDialog
            picker = GCPImagePickerDialog(self.image_paths[index], self, gcp_mode=True)
            picker.point_selected.connect(self.on_gcp_point_selected)
            picker.exec_()

    def on_gcp_point_selected(self, pixel_x, pixel_y, filename):
        if self.parent_dialog:
            self.parent_dialog.add_image_point_to_gcp_workflow(pixel_x, pixel_y, filename)

    def set_image_paths(self, image_paths):
        images_changed = self.image_paths != image_paths
        self.image_paths = image_paths.copy()

        if len(self.image_paths) > 20 and not self.images_first_loaded:
            self.images_first_loaded = True

        if images_changed or self.loaded_thumbnails == 0:
            self.refresh_image_display()

        if self.image_paths:
            self.current_image_index = -1
            self._enable_menu_actions(False)

    def refresh_image_display(self):
        for i in reversed(range(self.image_layout.count())):
            widget = self.image_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.loaded_thumbnails = 0

        if not self.image_paths:
            self.images_first_loaded = False
            return

        dock_width = self.width()
        margin_space = 60
        available_width = max(200, dock_width - margin_space)
        self.cols = max(2, available_width // (self.thumbnail_size + 20))

        self.load_next_batch()

    def load_next_batch(self):
        if self.loaded_thumbnails >= len(self.image_paths):
            return

        start_idx = self.loaded_thumbnails
        end_idx = len(self.image_paths)

        for i in range(start_idx, end_idx):
            try:
                thumbnail_widget = self._create_thumbnail(self.image_paths[i], i)
                row = i // self.cols
                col = i % self.cols
                self.image_layout.addWidget(thumbnail_widget, row, col)
            except Exception as e:
                print(f"Error loading image {self.image_paths[i]}: {e}")

        self.loaded_thumbnails = end_idx

    def _create_thumbnail(self, image_path, index):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            image_label = QLabel("Error")
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("color: red; font-size: 10px;")
        else:
            scaled = pixmap.scaled(
                self.thumbnail_size, self.thumbnail_size,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            image_label = QLabel()
            image_label.setPixmap(scaled)
            image_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(image_label)

        filename_label = QLabel(os.path.basename(image_path))
        filename_label.setAlignment(Qt.AlignCenter)
        filename_label.setStyleSheet("font-size: 8px; color: #666;")
        filename_label.setWordWrap(True)
        layout.addWidget(filename_label)

        widget.mousePressEvent = lambda event, idx=index: self.select_image(idx)
        widget.mouseDoubleClickEvent = lambda event, idx=index: self.open_image_viewer(idx)
        widget.setStyleSheet("""
            QWidget {
                border: 1px solid transparent;
                background-color: transparent;
                margin: 3px;
            }
            QWidget:hover {
                border: 1px solid #0078d4;
                background-color: rgba(0, 120, 212, 0.05);
            }
        """)

        return widget

    def open_image_viewer(self, index):
        if 0 <= index < len(self.image_paths):
            viewer = ImageMapWindow(self.image_paths[index], self)
            viewer.show()

    def select_image(self, index):
        self.current_image_index = index
        self._enable_menu_actions(index >= 0)

        for i in range(self.image_layout.count()):
            widget = self.image_layout.itemAt(i).widget()
            if i == index:
                widget.setStyleSheet("""
                    QWidget {
                        border: 2px solid #0078d4;
                        background-color: rgba(0, 120, 212, 0.1);
                        margin: 3px;
                    }
                """)
            else:
                widget.setStyleSheet("""
                    QWidget {
                        border: 1px solid transparent;
                        background-color: transparent;
                        margin: 3px;
                    }
                    QWidget:hover {
                        border: 1px solid #0078d4;
                        background-color: rgba(0, 120, 212, 0.05);
                    }
                """)

    def rotate_left(self):
        if 0 <= self.current_image_index < len(self.image_paths):
            self._rotate_image(-90)

    def rotate_right(self):
        if 0 <= self.current_image_index < len(self.image_paths):
            self._rotate_image(90)

    def _rotate_image(self, angle):
        image_path = self.image_paths[self.current_image_index]
        try:
            image = QImage(image_path)
            if image.isNull():
                QMessageBox.warning(self, 'Error', f'Failed to load: {os.path.basename(image_path)}')
                return

            transform = QTransform()
            transform.rotate(angle)
            rotated = image.transformed(transform, Qt.SmoothTransformation)

            if rotated.save(image_path):
                self.refresh_image_display()
                if self.current_image_index < self.image_layout.count():
                    self.select_image(self.current_image_index)
            else:
                QMessageBox.warning(self, 'Error', f'Failed to save: {os.path.basename(image_path)}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to rotate: {str(e)}')

    def remove_image(self):
        if 0 <= self.current_image_index < len(self.image_paths):
            image_path = self.image_paths[self.current_image_index]
            reply = QMessageBox.question(
                self, 'Remove Image',
                f'Remove "{os.path.basename(image_path)}"?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.image_paths.pop(self.current_image_index)
                if self.parent_dialog:
                    self.parent_dialog.image_paths = self.image_paths.copy()
                    self.parent_dialog.update_images_display()
                self.refresh_image_display()

                if self.image_paths:
                    if self.current_image_index >= len(self.image_paths):
                        self.current_image_index = len(self.image_paths) - 1
                    self.select_image(self.current_image_index)
                else:
                    self.current_image_index = -1

    def fit_to_window(self):
        QMessageBox.information(self, 'Fit', 'Fit to window would be implemented here')

    def on_scroll(self, value):
        scrollbar = self.scroll_area.verticalScrollBar()
        if scrollbar.maximum() - value < 100:
            if self.loaded_thumbnails < len(self.image_paths):
                self.load_next_batch()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_paths:
            dock_width = self.width()
            margin_space = 80
            available_width = max(250, dock_width - margin_space)

            min_thumb = 70
            max_thumb = 160

            best_cols = 1
            best_size = min_thumb
            best_score = float('inf')

            for cols in range(1, 9):
                thumb_size = (available_width // cols) - 8
                thumb_size = max(min_thumb, min(max_thumb, thumb_size))
                total_width = cols * (thumb_size + 8)
                score = abs(available_width - total_width)

                if score < best_score:
                    best_score = score
                    best_cols = cols
                    best_size = thumb_size

            if abs(best_size - self.thumbnail_size) > 10:
                self.thumbnail_size = best_size
                self.cols = best_cols
                self.refresh_image_display()
