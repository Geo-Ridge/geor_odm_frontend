# -*- coding: utf-8 -*-
"""Processing presets for ODM tasks."""

WEBODM_PRESETS = {
    'Default': {
        'feature_extraction': 'high',
        'camera_lens': 'auto',
        'quality': 50,
        'dsm': True,
        'dtm': False,
        'orthophoto': True,
        'reconstruction': 'high',
        'fov': 60,
        'pointcloud_density': 'medium',
        'outlier_removal': False,
        'deviation': 5,
        'resolution': 5,
        'tile_size': '2048',
        'texture_mesh': True,
        'generate_video': False,
        'generate_report': True,
        'threads': 0,
        'memory_limit': 8
    },
    'High Resolution': {
        'feature_extraction': 'high',
        'camera_lens': 'auto',
        'quality': 25,
        'dsm': True,
        'dtm': True,
        'orthophoto': True,
        'reconstruction': 'high',
        'fov': 60,
        'pointcloud_density': 'high',
        'outlier_removal': False,
        'deviation': 5,
        'resolution': 2,
        'tile_size': '2048',
        'texture_mesh': True,
        'generate_video': False,
        'generate_report': True,
        'threads': 0,
        'memory_limit': 8
    },
    'Fast Orthophoto': {
        'feature_extraction': 'low',
        'camera_lens': 'auto',
        'quality': 75,
        'dsm': False,
        'dtm': False,
        'orthophoto': True,
        'reconstruction': 'medium',
        'fov': 60,
        'pointcloud_density': 'low',
        'outlier_removal': False,
        'deviation': 5,
        'resolution': 20,
        'tile_size': '4096',
        'texture_mesh': False,
        'generate_video': False,
        'generate_report': False,
        'threads': 0,
        'memory_limit': 8
    },
    'Field': {
        'feature_extraction': 'high',
        'camera_lens': 'perspective',
        'quality': 30,
        'dsm': True,
        'dtm': False,
        'orthophoto': True,
        'reconstruction': 'high',
        'fov': 60,
        'pointcloud_density': 'medium',
        'outlier_removal': False,
        'deviation': 5,
        'resolution': 16,
        'tile_size': '2048',
        'texture_mesh': False,
        'generate_video': False,
        'generate_report': True,
        'threads': 0,
        'memory_limit': 8
    },
    'DSM+DTM': {
        'feature_extraction': 'medium',
        'camera_lens': 'auto',
        'quality': 50,
        'dsm': True,
        'dtm': True,
        'pc_classify': True,
        'orthophoto': True,
        'reconstruction': 'high',
        'fov': 60,
        'pointcloud_density': 'medium',
        'outlier_removal': True,
        'deviation': 3,
        'resolution': 24,
        'tile_size': '2048',
        'texture_mesh': True,
        'generate_video': False,
        'generate_report': True,
        'threads': 0,
        'memory_limit': 8
    },
    '3D Model': {
        'feature_extraction': 'high',
        'camera_lens': 'auto',
        'quality': 30,
        'dsm': True,
        'dtm': False,
        'orthophoto': True,
        'reconstruction': 'high',
        'fov': 60,
        'pointcloud_density': 'high',
        'outlier_removal': False,
        'deviation': 5,
        'resolution': 16,
        'tile_size': '2048',
        'texture_mesh': True,
        'generate_video': False,
        'generate_report': True,
        'threads': 0,
        'memory_limit': 12
    }
}

STATUS_CODES = {
    10: 'QUEUED',
    20: 'RUNNING',
    30: 'FAILED',
    40: 'COMPLETED',
    50: 'CANCELED'
}

def get_preset_names():
    """Return list of available preset names."""
    return list(WEBODM_PRESETS.keys()) + ['Custom']

def get_preset_config(preset_name):
    """Get configuration for a specific preset."""
    return WEBODM_PRESETS.get(preset_name, {}).copy()

def get_status_text(status_code):
    """Convert status code to readable text."""
    return STATUS_CODES.get(status_code, f'UNKNOWN({status_code})')
