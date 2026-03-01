# -*- coding: utf-8 -*-
"""Results tab for downloading and importing results."""
import os
import tempfile
import zipfile
import shutil
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QComboBox, QTextEdit,
    QFileDialog, QMessageBox, QCheckBox, QDialog,
    QDialogButtonBox, QScrollArea
)
from qgis.core import QgsProject, QgsRasterLayer, QgsPointCloudLayer
from ...utils.helpers import get_status_text, format_processing_time

class ResultsTab(QWidget):
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

        task_group = QGroupBox('Task Selection')
        task_layout = QVBoxLayout()
        task_layout.setContentsMargins(5, 5, 5, 5)
        task_layout.setSpacing(3)
        self.task_combo = QComboBox()
        self.task_combo.addItem('No task selected', '')
        self.task_combo.currentIndexChanged.connect(self.select_task)
        task_layout.addWidget(self.task_combo)
        task_group.setLayout(task_layout)
        layout.addWidget(task_group)

        actions_group = QGroupBox('Actions')
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(5, 5, 5, 5)
        btn_layout.setSpacing(3)
        self.refresh_btn = QPushButton('Refresh')
        self.refresh_btn.setMaximumWidth(80)
        self.refresh_btn.clicked.connect(self.refresh_status)
        self.download_btn = QPushButton('Download')
        self.download_btn.setMaximumWidth(80)
        self.download_btn.clicked.connect(self.download_results)
        self.import_btn = QPushButton('Import')
        self.import_btn.setMaximumWidth(80)
        self.import_btn.clicked.connect(self.import_to_qgis)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addStretch()
        actions_group.setLayout(btn_layout)
        layout.addWidget(actions_group)

        display_group = QGroupBox('Results')
        display_layout = QVBoxLayout()
        display_layout.setContentsMargins(5, 5, 5, 5)
        display_layout.setSpacing(3)
        self.results_text = QTextEdit()
        self.results_text.setMinimumHeight(60)
        self.results_text.setMaximumHeight(100)
        self.results_text.setReadOnly(True)
        display_layout.addWidget(self.results_text)
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def select_task(self):
        selected_uuid = self.task_combo.currentData()
        if selected_uuid:
            self.parent_dialog.current_project = selected_uuid
            self.results_text.clear()
            self.parent_dialog.update_task_buttons()
            self.parent_dialog.task_manager.start_monitoring(selected_uuid)
        else:
            self.parent_dialog.current_project = None
            self.results_text.clear()
            self.parent_dialog.task_manager.stop_monitoring()

    def refresh_status(self):
        if not self.parent_dialog.current_project:
            return
        task_info = self.parent_dialog.odm.get_task_info(self.parent_dialog.current_project)
        self.results_text.clear()
        if task_info:
            status_field = task_info.get('status', {})
            status_code = status_field.get('code', 0) if isinstance(status_field, dict) else status_field
            progress = task_info.get('progress', 0)
            name = task_info.get('name', 'Unknown')
            proc_time = task_info.get('processingTime', 0)
            status_text = get_status_text(status_code)
            time_str = format_processing_time(proc_time)
            self.results_text.append(f'{name}: {status_text} ({int(progress)}%){time_str}')

    def download_results(self):
        if not self.parent_dialog.current_project:
            return
        output_path, _ = QFileDialog.getSaveFileName(self, 'Save Results', '', 'ZIP files (*.zip)')
        if output_path:
            self.parent_dialog.processing_tab.status_text.append(f'Downloading to {output_path}...')
            if self.parent_dialog.odm.download_results(self.parent_dialog.current_project, output_path):
                self.parent_dialog.processing_tab.status_text.append('✓ Download completed')
            else:
                self.parent_dialog.processing_tab.status_text.append('✗ Download failed')

    def import_to_qgis(self):
        if not self.parent_dialog.current_project:
            QMessageBox.warning(self, 'Warning', 'No task selected.')
            return
        task_info = self.parent_dialog.odm.get_task_info(self.parent_dialog.current_project)
        if not task_info:
            QMessageBox.critical(self, 'Error', 'Could not get task info.')
            return
        status_code = task_info.get('status', {}).get('code', 0)
        if status_code != 40:
            QMessageBox.warning(self, 'Warning', 'Task must be completed first.')
            return
        dialog = ImportOptionsDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return
        options = dialog.get_options()
        try:
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, 'results.zip')
            self.parent_dialog.processing_tab.status_text.append('Downloading results...')
            if not self.parent_dialog.odm.download_results(self.parent_dialog.current_project, zip_path):
                QMessageBox.critical(self, 'Error', 'Failed to download.')
                return
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_dir)
            imported = 0
            if options['orthophoto']:
                ortho = os.path.join(temp_dir, 'odm_orthophoto', 'odm_orthophoto.tif')
                if os.path.exists(ortho):
                    layer = QgsRasterLayer(ortho, 'Orthophoto', 'gdal')
                    if layer.isValid():
                        QgsProject.instance().addMapLayer(layer)
                        imported += 1
                        self.parent_dialog.processing_tab.status_text.append('✓ Orthophoto imported')
            if options['dsm']:
                dsm = os.path.join(temp_dir, 'odm_dem', 'dsm.tif')
                if os.path.exists(dsm):
                    layer = QgsRasterLayer(dsm, 'DSM', 'gdal')
                    if layer.isValid():
                        QgsProject.instance().addMapLayer(layer)
                        imported += 1
                        self.parent_dialog.processing_tab.status_text.append('✓ DSM imported')
            if options['dtm']:
                dtm = os.path.join(temp_dir, 'odm_dem', 'dtm.tif')
                if os.path.exists(dtm):
                    layer = QgsRasterLayer(dtm, 'DTM', 'gdal')
                    if layer.isValid():
                        QgsProject.instance().addMapLayer(layer)
                        imported += 1
                        self.parent_dialog.processing_tab.status_text.append('✓ DTM imported')
            if options['point_cloud']:
                pc_paths = [
                    'odm_georeferencing/odm_georeferenced_model.laz',
                    'odm_georeferencing/odm_georeferenced_model.las',
                ]
                for pc_path in pc_paths:
                    full = os.path.join(temp_dir, pc_path)
                    if os.path.exists(full):
                        layer = QgsPointCloudLayer(full, 'Point Cloud', 'pointcloud')
                        if layer.isValid():
                            QgsProject.instance().addMapLayer(layer)
                            imported += 1
                            self.parent_dialog.processing_tab.status_text.append('✓ Point cloud imported')
                            break
            if imported > 0:
                self.parent_dialog.iface.mapCanvas().refreshAllLayers()
                QMessageBox.information(self, 'Success', f'Imported {imported} layers.')
            else:
                QMessageBox.warning(self, 'Warning', 'No valid files found.')
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Import failed: {str(e)}')

class ImportOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Import Options')
        self.setModal(True)
        layout = QVBoxLayout()
        self.ortho_check = QCheckBox('Import Orthophoto')
        self.ortho_check.setChecked(True)
        self.dsm_check = QCheckBox('Import DSM')
        self.dsm_check.setChecked(True)
        self.dtm_check = QCheckBox('Import DTM')
        self.dtm_check.setChecked(True)
        self.pc_check = QCheckBox('Import Point Cloud')
        self.pc_check.setChecked(True)
        layout.addWidget(QLabel('Select results to import:'))
        layout.addWidget(self.ortho_check)
        layout.addWidget(self.dsm_check)
        layout.addWidget(self.dtm_check)
        layout.addWidget(self.pc_check)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_options(self):
        return {
            'orthophoto': self.ortho_check.isChecked(),
            'dsm': self.dsm_check.isChecked(),
            'dtm': self.dtm_check.isChecked(),
            'point_cloud': self.pc_check.isChecked()
        }
