# -*- coding: utf-8 -*-
"""Main ODM dialog container."""
import os
from qgis.PyQt.QtWidgets import (
    QDockWidget, QVBoxLayout, QWidget, QTabWidget,
    QPushButton, QMenu, QAction, QMessageBox, QInputDialog
)
from qgis.PyQt.QtCore import Qt

from ..core.connection import ODMConnection
from ..core.task_manager import TaskManager
from ..core.project_manager import ProjectManager
from ..utils.presets import get_preset_config

from .tabs.processing_tab import ProcessingTab
from .tabs.options_tab import OptionsTab
from .tabs.gcp_tab import GCPTab
from .tabs.tasks_tab import TasksTab
from .tabs.results_tab import ResultsTab
from .dialogs.connection_dialog import ConnectionDialog
from .widgets.photos_dock import PhotosDock

class ODMMainDialog(QDockWidget):
    """Main ODM Frontend dock widget."""

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.odm = ODMConnection()
        self.task_manager = TaskManager(self.odm, iface)
        self.project_manager = ProjectManager(self)

        self.current_project = None
        self.image_paths = []
        self.project_name = 'Untitled Project'
        self.pending_project_load_success = False

        self.photos_dock = None

        self._setup_ui()
        self._connect_signals()
        self._load_initial_data()

    def _setup_ui(self):
        self.setWindowTitle('ODM Frontend')
        self.setMinimumWidth(350)
        self.setMaximumWidth(450)
        self.setAttribute(Qt.WA_DeleteOnClose, False)

        central = QWidget()
        self.setWidget(central)
        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(1)

        # Tab widget
        self.tabs = QTabWidget()

        # Menu button
        self.menu_btn = QPushButton('☰')
        self.menu_btn.setFixedWidth(30)
        self.menu_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #007bff; border: none; font-size: 16px; }
            QPushButton:hover { color: #0056b3; background-color: #f0f0f0; }
        """)
        self.menu_btn.setToolTip('Project Menu')

        self.project_menu = QMenu(self)
        conn_action = QAction('🔗 Connection', self)
        conn_action.triggered.connect(self.show_connection_dialog)
        open_action = QAction('📂 Open Project', self)
        open_action.triggered.connect(self.open_project)
        save_action = QAction('💾 Save Project', self)
        save_action.triggered.connect(self.save_project)
        self.project_menu.addAction(conn_action)
        self.project_menu.addSeparator()
        self.project_menu.addAction(open_action)
        self.project_menu.addAction(save_action)
        self.menu_btn.setMenu(self.project_menu)
        self.tabs.setCornerWidget(self.menu_btn)

        # Create tabs
        self.processing_tab = ProcessingTab(self)
        self.options_tab = OptionsTab(self)
        self.gcp_tab = GCPTab(self)
        self.tasks_tab = TasksTab(self)
        self.results_tab = ResultsTab(self)

        self.tabs.addTab(self.processing_tab, 'Processing')
        self.tabs.addTab(self.options_tab, 'Options')
        self.tabs.addTab(self.gcp_tab, 'GCPs')
        self.tabs.addTab(self.tasks_tab, 'Tasks')
        self.tabs.addTab(self.results_tab, 'Results')

        layout.addWidget(self.tabs)
        central.setLayout(layout)

    def _connect_signals(self):
        # Task manager signals
        self.task_manager.status_changed.connect(self._on_status_changed)
        self.task_manager.task_completed.connect(self._on_task_completed)
        self.task_manager.task_failed.connect(self._on_task_failed)

    def _load_initial_data(self):
        self.tasks_tab.load_tasks()
        self.apply_preset_config(get_preset_config('Default'))

    def _on_status_changed(self, task_info):
        self.results_tab.refresh_status()

    def _on_task_completed(self, task_id):
        self.processing_tab.status_text.append('✓ Processing completed!')
        self.processing_tab.start_btn.setEnabled(True)
        self.processing_tab.stop_btn.setEnabled(False)
        self.tasks_tab.load_tasks()

    def _on_task_failed(self, task_id):
        self.processing_tab.status_text.append('✗ Processing failed!')
        self.processing_tab.start_btn.setEnabled(True)
        self.processing_tab.stop_btn.setEnabled(False)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        if self.photos_dock:
            self.photos_dock.hide()

    def show_connection_dialog(self):
        dialog = ConnectionDialog(self.odm, self)
        dialog.exec_()

    def apply_preset_config(self, config):
        """Apply preset configuration to UI."""
        if not config:
            return

        # Processing tab
        self.processing_tab.orthophoto_checkbox.setChecked(config.get('orthophoto', True))
        self.processing_tab.dsm_checkbox.setChecked(config.get('dsm', False))
        self.processing_tab.dtm_checkbox.setChecked(config.get('dtm', False))

        # Options tab
        self.options_tab.set_options(config)

    def update_images_display(self):
        """Update images count and photos dock."""
        count = len(self.image_paths)
        self.processing_tab.update_count(count)

        if count > 0:
            if not self.photos_dock:
                existing = self.iface.mainWindow().findChild(PhotosDock, 'odm_photos_dock')
                if existing:
                    self.photos_dock = existing
                else:
                    self.photos_dock = PhotosDock(self)
                    self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.photos_dock)
            self.photos_dock.show()
            self.photos_dock.set_image_paths(self.image_paths)

            if self.pending_project_load_success:
                QMessageBox.information(self, 'Success', f'Project "{self.project_name}" loaded!')
                self.pending_project_load_success = False
        else:
            if self.photos_dock:
                self.photos_dock.hide()

    def start_task_processing(self):
        """Start new processing task."""
        if not self.image_paths:
            QMessageBox.warning(self, 'Warning', 'Please add images first.')
            return

        name, ok = QInputDialog.getText(self, 'New Task', 'Enter task name:')
        if not ok or not name:
            return

        # Build options
        options = {}
        if self.processing_tab.dsm_checkbox.isChecked():
            options['dsm'] = True
        if self.processing_tab.dtm_checkbox.isChecked():
            options['dtm'] = True
            options['pc-classify'] = True
        if self.processing_tab.orthophoto_checkbox.isChecked():
            options['orthophoto-resolution'] = str(self.options_tab.resolution_spin.value())

        # Add options tab settings
        opts = self.options_tab.get_options()
        options['reconstruction-quality'] = opts['reconstruction']
        options['camera-lens'] = opts['camera_lens']
        options['point-cloud-quality'] = opts['pointcloud_density']
        options['camera-fov'] = str(opts['fov'])

        if opts['outlier_removal']:
            options['use-3dmesh'] = True
            options['pc-cleanup'] = True
            options['pc-classify'] = True
            options['pc-filter'] = str(opts['deviation'])

        if opts['texture_mesh']:
            options['textured-mesh'] = True
        if opts['generate_report']:
            options['build-overviews'] = True

        if opts['threads'] > 0:
            options['threads'] = str(opts['threads'])
        if opts['memory_limit'] > 0:
            options['max-memory'] = str(opts['memory_limit'])

        quality_map = {'auto': 'high', 'high': 'high', 'medium': 'medium', 'low': 'low'}
        options['feature-quality'] = quality_map.get(opts['feature_extraction'], 'medium')

        self.processing_tab.status_text.append(f'Creating task "{name}" with {len(self.image_paths)} images...')

        from qgis.core import Qgis
        msg = self.iface.messageBar().createMessage('ODM: Creating task...')
        self.iface.messageBar().pushWidget(msg, Qgis.Info)

        task = self.odm.create_task(self.image_paths, options, name)
        if task:
            uuid = task.get('uuid')
            QMessageBox.information(self, 'Success', f'Task "{name}" created!\n\nID: {uuid}')
            self.current_project = uuid
            self.tasks_tab.load_tasks()
            self.task_manager.start_monitoring(uuid)
            self.tabs.setCurrentIndex(3)  # Tasks tab
            self.processing_tab.start_btn.setEnabled(False)
            self.processing_tab.stop_btn.setEnabled(True)
        else:
            QMessageBox.critical(self, 'Error', 'Failed to create task.\n\nCheck that:\n1. NodeODM server is running\n2. Images are valid\n3. Server has resources')

    def stop_task(self):
        """Stop current task."""
        if not self.current_project:
            QMessageBox.warning(self, 'Warning', 'No task selected.')
            return

        reply = QMessageBox.question(self, 'Confirm Stop',
            f'Stop task {self.current_project}?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.odm.cancel_task(self.current_project):
                self.processing_tab.status_text.append(f'✓ Task stopped')
                self.processing_tab.stop_btn.setEnabled(False)
                self.processing_tab.start_btn.setEnabled(True)
                self.task_manager.stop_monitoring()
            else:
                self.processing_tab.status_text.append(f'✗ Failed to stop task')

    def update_task_buttons(self):
        """Update button states based on task status."""
        if not self.current_project:
            self.processing_tab.start_btn.setEnabled(len(self.image_paths) > 0)
            self.processing_tab.stop_btn.setEnabled(False)
            return

        task_info = self.odm.get_task_info(self.current_project)
        if task_info:
            status_code = task_info.get('status', {}).get('code', 0)
            if status_code == 20:  # RUNNING
                self.processing_tab.start_btn.setEnabled(False)
                self.processing_tab.stop_btn.setEnabled(True)
            else:
                self.processing_tab.start_btn.setEnabled(len(self.image_paths) > 0)
                self.processing_tab.stop_btn.setEnabled(False)

    def save_project(self):
        """Save project to file."""
        if not self.image_paths:
            QMessageBox.warning(self, 'Warning', 'No images to save.')
            return

        from qgis.PyQt.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Project', '',
            'ODM Project Files (*.odm);;All Files (*.*)')
        if not file_path:
            return

        try:
            self.project_manager.save_project(file_path)
            QMessageBox.information(self, 'Success', f'Project saved to {os.path.basename(file_path)}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save: {str(e)}')

    def open_project(self):
        """Load project from file."""
        from qgis.PyQt.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Project', '',
            'ODM Project Files (*.odm);;All Files (*.*)')
        if not file_path:
            return

        try:
            project_data = self.project_manager.load_project(file_path)
            self.project_manager.apply_to_dialog(project_data)
            self.update_images_display()
            self.pending_project_load_success = True
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load: {str(e)}')

    def add_image_point_to_gcp_workflow(self, pixel_x, pixel_y, filename):
        """Handle GCP image point from photos dock."""
        from .dialogs.gcp_dialogs import GCPSelectorDialog, GCPMapTool, GCPPropertiesDialog
        from qgis.PyQt.QtWidgets import QDialog

        selector = GCPSelectorDialog(pixel_x, pixel_y, filename, self.gcp_tab.gcp_points, self)
        if selector.exec_() == QDialog.Accepted:
            gcp_id, create_new = selector.get_selection()

            if create_new:
                # Activate map tool for world coordinate selection
                canvas = self.iface.mapCanvas()
                self.gcp_map_tool = GCPMapTool(canvas)

                def on_point_picked(world_x, world_y):
                    props = GCPPropertiesDialog(pixel_x, pixel_y, filename, world_x, world_y, self, self.iface)
                    if props.exec_() == QDialog.Accepted:
                        data = props.get_gcp_data()
                        new_gcp = {
                            'id': len(self.gcp_tab.gcp_points) + 1,
                            'world_x': data['world_x'],
                            'world_y': data['world_y'],
                            'world_z': data['world_z'],
                            'gcp_name': data['gcp_name'] or f"GCP{len(self.gcp_tab.gcp_points) + 1}",
                            'is_checkpoint': data['is_checkpoint'],
                            'image_points': [{'filename': filename, 'x': pixel_x, 'y': pixel_y}]
                        }
                        self.gcp_tab.gcp_points.append(new_gcp)
                        self.gcp_tab.update_gcp_list()
                        QMessageBox.information(self, 'Success', f'Created {new_gcp["gcp_name"]}')
                    canvas.unsetMapTool(self.gcp_map_tool)

                self.gcp_map_tool.point_picked.connect(on_point_picked)
                canvas.setMapTool(self.gcp_map_tool)
                self.iface.messageBar().pushMessage('GCP', 'Click on map to set world coordinates', level=0)
            else:
                # Add to existing GCP
                gcp = next((g for g in self.gcp_tab.gcp_points if g['id'] == gcp_id), None)
                if gcp:
                    if 'image_points' not in gcp:
                        gcp['image_points'] = []
                    gcp['image_points'].append({'filename': filename, 'x': pixel_x, 'y': pixel_y})
                    self.gcp_tab.update_gcp_list()
                    QMessageBox.information(self, 'Success', f'Added to {gcp.get("gcp_name", f"GCP{gcp_id}")}')
