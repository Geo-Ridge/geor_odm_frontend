# -*- coding: utf-8 -*-
"""Options tab with advanced processing settings."""
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QComboBox, QSpinBox, QCheckBox,
    QScrollArea, QGridLayout
)

class OptionsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        cam_group = QGroupBox('Camera & Reconstruction')
        cam_grid = QGridLayout()
        cam_grid.setContentsMargins(5, 5, 5, 5)
        cam_grid.setSpacing(3)
        cam_grid.addWidget(QLabel('Feature:'), 0, 0)
        self.feature_combo = QComboBox()
        self.feature_combo.addItems(['auto', 'high', 'medium', 'low'])
        self.feature_combo.setMaximumWidth(80)
        cam_grid.addWidget(self.feature_combo, 0, 1)
        cam_grid.addWidget(QLabel('Lens:'), 0, 2)
        self.lens_combo = QComboBox()
        self.lens_combo.addItems(['auto', 'perspective', 'fisheye', 'spherical'])
        self.lens_combo.setMaximumWidth(90)
        cam_grid.addWidget(self.lens_combo, 0, 3)
        cam_grid.addWidget(QLabel('Quality:'), 1, 0)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(50)
        self.quality_spin.setMaximumWidth(70)
        cam_grid.addWidget(self.quality_spin, 1, 1)
        cam_grid.addWidget(QLabel('Recon:'), 1, 2)
        self.recon_combo = QComboBox()
        self.recon_combo.addItems(['high', 'medium', 'low'])
        self.recon_combo.setCurrentText('high')
        self.recon_combo.setMaximumWidth(80)
        cam_grid.addWidget(self.recon_combo, 1, 3)
        cam_grid.addWidget(QLabel('FOV:'), 2, 0)
        self.fov_spin = QSpinBox()
        self.fov_spin.setRange(1, 180)
        self.fov_spin.setValue(60)
        self.fov_spin.setMaximumWidth(70)
        cam_grid.addWidget(self.fov_spin, 2, 1)
        cam_group.setLayout(cam_grid)
        layout.addWidget(cam_group)

        pc_group = QGroupBox('Point Cloud')
        pc_grid = QGridLayout()
        pc_grid.setContentsMargins(5, 5, 5, 5)
        pc_grid.setSpacing(3)
        pc_grid.addWidget(QLabel('Density:'), 0, 0)
        self.density_combo = QComboBox()
        self.density_combo.addItems(['high', 'medium', 'low'])
        self.density_combo.setCurrentText('medium')
        self.density_combo.setMaximumWidth(80)
        pc_grid.addWidget(self.density_combo, 0, 1)
        pc_grid.addWidget(QLabel('Outlier:'), 1, 0)
        filter_box = QHBoxLayout()
        filter_box.setSpacing(3)
        self.outlier_check = QCheckBox('Enable')
        filter_box.addWidget(self.outlier_check)
        filter_box.addWidget(QLabel('Dev:'))
        self.deviation_spin = QSpinBox()
        self.deviation_spin.setRange(1, 50)
        self.deviation_spin.setValue(5)
        self.deviation_spin.setMaximumWidth(60)
        filter_box.addWidget(self.deviation_spin)
        pc_grid.addLayout(filter_box, 1, 1)
        pc_group.setLayout(pc_grid)
        layout.addWidget(pc_group)

        output_group = QGroupBox('Outputs')
        output_grid = QGridLayout()
        output_grid.setContentsMargins(5, 5, 5, 5)
        output_grid.setSpacing(3)
        output_grid.addWidget(QLabel('Resolution:'), 0, 0)
        self.resolution_spin = QSpinBox()
        self.resolution_spin.setRange(1, 100)
        self.resolution_spin.setValue(5)
        self.resolution_spin.setMaximumWidth(70)
        output_grid.addWidget(self.resolution_spin, 0, 1)
        output_grid.addWidget(QLabel('Tile Size:'), 0, 2)
        self.tile_combo = QComboBox()
        self.tile_combo.addItems(['2048', '4096', '8192'])
        self.tile_combo.setCurrentText('2048')
        self.tile_combo.setMaximumWidth(80)
        output_grid.addWidget(self.tile_combo, 0, 3)
        extra_layout = QHBoxLayout()
        extra_layout.setSpacing(6)
        self.mesh_check = QCheckBox('Mesh')
        self.mesh_check.setChecked(True)
        self.video_check = QCheckBox('Video')
        self.report_check = QCheckBox('Report')
        self.report_check.setChecked(True)
        extra_layout.addWidget(self.mesh_check)
        extra_layout.addWidget(self.video_check)
        extra_layout.addWidget(self.report_check)
        output_grid.addLayout(extra_layout, 1, 0, 1, 4)
        output_group.setLayout(output_grid)
        layout.addWidget(output_group)

        perf_group = QGroupBox('Performance')
        perf_layout = QHBoxLayout()
        perf_layout.setContentsMargins(5, 5, 5, 5)
        perf_layout.setSpacing(3)
        perf_layout.addWidget(QLabel('Threads:'))
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(0, 32)
        self.threads_spin.setValue(0)
        self.threads_spin.setMaximumWidth(60)
        perf_layout.addWidget(self.threads_spin)
        perf_layout.addWidget(QLabel('Memory:'))
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(1, 64)
        self.memory_spin.setValue(8)
        self.memory_spin.setMaximumWidth(60)
        perf_layout.addWidget(self.memory_spin)
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)

        layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def get_options(self):
        return {
            'feature_extraction': self.feature_combo.currentText(),
            'camera_lens': self.lens_combo.currentText(),
            'quality': self.quality_spin.value(),
            'reconstruction': self.recon_combo.currentText(),
            'fov': self.fov_spin.value(),
            'pointcloud_density': self.density_combo.currentText(),
            'outlier_removal': self.outlier_check.isChecked(),
            'deviation': self.deviation_spin.value(),
            'resolution': self.resolution_spin.value(),
            'tile_size': self.tile_combo.currentText(),
            'texture_mesh': self.mesh_check.isChecked(),
            'generate_video': self.video_check.isChecked(),
            'generate_report': self.report_check.isChecked(),
            'threads': self.threads_spin.value(),
            'memory_limit': self.memory_spin.value()
        }

    def set_options(self, options):
        self.feature_combo.setCurrentText(options.get('feature_extraction', 'auto'))
        self.lens_combo.setCurrentText(options.get('camera_lens', 'auto'))
        self.quality_spin.setValue(options.get('quality', 50))
        self.recon_combo.setCurrentText(options.get('reconstruction', 'high'))
        self.fov_spin.setValue(options.get('fov', 60))
        self.density_combo.setCurrentText(options.get('pointcloud_density', 'medium'))
        self.outlier_check.setChecked(options.get('outlier_removal', False))
        self.deviation_spin.setValue(options.get('deviation', 5))
        self.resolution_spin.setValue(options.get('resolution', 5))
        self.tile_combo.setCurrentText(options.get('tile_size', '2048'))
        self.mesh_check.setChecked(options.get('texture_mesh', True))
        self.video_check.setChecked(options.get('generate_video', False))
        self.report_check.setChecked(options.get('generate_report', True))
        self.threads_spin.setValue(options.get('threads', 0))
        self.memory_spin.setValue(options.get('memory_limit', 8))
