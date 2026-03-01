# -*- coding: utf-8 -*-
"""Project file management."""

import json
import os


class ProjectManager:
    """Handles project save/load operations."""

    def __init__(self, dialog):
        self.dialog = dialog

    def save_project(self, file_path):
        """Save current project to file."""
        d = self.dialog

        project_data = {
            'name': getattr(d, 'project_name', 'Untitled Project'),
            'preset': d.preset_combo.currentText(),
            'images': d.image_paths,
            'options': {
                'feature_extraction': d.feature_extraction_combo.currentText(),
                'camera_lens': d.camera_lens_combo.currentText(),
                'quality': d.quality_spin.value(),
                'dsm': d.dsm_checkbox.isChecked(),
                'dtm': d.dtm_checkbox.isChecked(),
                'orthophoto': d.orthophoto_checkbox.isChecked(),
                'reconstruction': d.recon_combo.currentText(),
                'fov': d.fov_spin.value(),
                'pointcloud_density': d.pc_density_combo.currentText(),
                'outlier_removal': d.outlier_checkbox.isChecked(),
                'deviation': d.deviation_spin.value(),
                'resolution': d.resolution_spin.value(),
                'tile_size': d.tile_combo.currentText(),
                'texture_mesh': d.texture_checkbox.isChecked(),
                'generate_video': d.video_checkbox.isChecked(),
                'generate_report': d.report_checkbox.isChecked(),
                'threads': d.threads_spin.value(),
                'memory_limit': d.memory_spin.value()
            },
            'odm_settings': {
                'base_url': d.odm.base_url,
                'token': d.odm.token
            }
        }

        with open(file_path, 'w') as f:
            json.dump(project_data, f, indent=2)

    def load_project(self, file_path):
        """Load project from file."""
        with open(file_path, 'r') as f:
            return json.load(f)

    def apply_to_dialog(self, project_data):
        """Apply loaded project data to dialog."""
        d = self.dialog

        # Load images
        d.image_paths = project_data.get('images', [])

        # Load preset
        preset = project_data.get('preset', 'Custom')
        d.preset_combo.setCurrentText(preset)

        # If custom, load manual options
        if preset == 'Custom':
            opts = project_data.get('options', {})
            d.feature_extraction_combo.setCurrentText(opts.get('feature_extraction', 'auto'))
            d.camera_lens_combo.setCurrentText(opts.get('camera_lens', 'auto'))
            d.quality_spin.setValue(opts.get('quality', 50))
            d.dsm_checkbox.setChecked(opts.get('dsm', False))
            d.dtm_checkbox.setChecked(opts.get('dtm', False))
            d.orthophoto_checkbox.setChecked(opts.get('orthophoto', True))
            d.recon_combo.setCurrentText(opts.get('reconstruction', 'high'))
            d.fov_spin.setValue(opts.get('fov', 60))
            d.pc_density_combo.setCurrentText(opts.get('pointcloud_density', 'medium'))
            d.outlier_checkbox.setChecked(opts.get('outlier_removal', False))
            d.deviation_spin.setValue(opts.get('deviation', 5))
            d.resolution_spin.setValue(opts.get('resolution', 24))
            d.tile_combo.setCurrentText(opts.get('tile_size', '2048'))
            d.texture_checkbox.setChecked(opts.get('texture_mesh', True))
            d.video_checkbox.setChecked(opts.get('generate_video', False))
            d.report_checkbox.setChecked(opts.get('generate_report', True))
            d.threads_spin.setValue(opts.get('threads', 0))
            d.memory_spin.setValue(opts.get('memory_limit', 8))

        # Load ODM settings
        odm_settings = project_data.get('odm_settings', {})
        if odm_settings.get('base_url'):
            d.odm.set_credentials(
                odm_settings['base_url'],
                odm_settings.get('token', '')
            )

        # Store project name
        d.project_name = project_data.get('name', 'Loaded Project')

        return True
