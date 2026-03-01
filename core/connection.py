# -*- coding: utf-8 -*-
"""ODM API connection client."""

import json
import requests
from qgis.PyQt.QtCore import QSettings


class ODMConnection:
    """Client for OpenDroneMap NodeODM API."""

    def __init__(self):
        self.settings = QSettings()
        self.base_url = self.settings.value('odm_frontend/base_url', 'http://localhost:3000')
        self.token = self.settings.value('odm_frontend/token', '')

    def set_credentials(self, base_url, token=''):
        """Save credentials to settings."""
        self.base_url = base_url
        self.token = token
        self.settings.setValue('odm_frontend/base_url', base_url)
        self.settings.setValue('odm_frontend/token', token)

    def test_connection(self):
        """Test connection to ODM server."""
        try:
            base_url = self.base_url.rstrip('/')
            endpoints = ['/info', '/', '/task/list']
            for endpoint in endpoints:
                try:
                    response = requests.get(
                        f'{base_url}{endpoint}',
                        timeout=10
                    )
                    if response.status_code == 200:
                        return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def _get_auth_params(self):
        """Get authentication parameters."""
        params = {}
        if self.token:
            params['token'] = self.token
        return params

    def _get_base_url(self):
        """Get sanitized base URL."""
        return self.base_url.rstrip('/')

    def create_task(self, image_paths, options=None, name=None):
        """Create a new processing task."""
        params = self._get_auth_params()
        base_url = self._get_base_url()

        # Prepare files
        files = []
        file_handles = []
        try:
            for path in image_paths:
                f = open(path, 'rb')
                files.append(('images', f))
                file_handles.append(f)

            # Prepare form data
            data = {}
            if options:
                options_array = [
                    {"name": k, "value": v}
                    for k, v in options.items()
                ]
                data['options'] = json.dumps(options_array)
            if name:
                data['name'] = name

            response = requests.post(
                f'{base_url}/task/new',
                files=files,
                data=data,
                params=params,
                timeout=60
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error creating task: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception creating task: {e}")
            return None
        finally:
            for f in file_handles:
                try:
                    f.close()
                except:
                    pass

    def get_tasks(self):
        """Get list of all tasks with full info."""
        params = self._get_auth_params()
        base_url = self._get_base_url()

        try:
            response = requests.get(
                f'{base_url}/task/list',
                params=params,
                timeout=30
            )
            if response.status_code != 200:
                return []

            task_uuids = response.json()
            tasks_with_info = []

            for task_item in task_uuids:
                uuid = task_item.get('uuid')
                if not uuid:
                    continue

                task_info = self._get_task_info_raw(uuid)
                if task_info:
                    tasks_with_info.append(task_info)
                else:
                    tasks_with_info.append({
                        'uuid': uuid,
                        'name': 'Task',
                        'status': {'code': 0},
                        'progress': 0
                    })

            return tasks_with_info
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []

    def _get_task_info_raw(self, task_id):
        """Get raw task info for internal use."""
        params = self._get_auth_params()
        base_url = self._get_base_url()

        try:
            response = requests.get(
                f'{base_url}/task/{task_id}/info',
                params=params,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def get_task_info(self, task_id):
        """Get task information by ID."""
        return self._get_task_info_raw(task_id)

    def cancel_task(self, task_id):
        """Cancel a running task."""
        params = self._get_auth_params()
        base_url = self._get_base_url()

        try:
            response = requests.post(
                f'{base_url}/task/cancel',
                params=params,
                json={'uuid': task_id},
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get('success', False)
            return False
        except Exception as e:
            print(f"Cancel task exception: {e}")
            return False

    def delete_task(self, task_id):
        """Delete a task."""
        params = self._get_auth_params()
        base_url = self._get_base_url()

        try:
            response = requests.post(
                f'{base_url}/task/remove',
                params=params,
                json={'uuid': task_id},
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get('success', False)
            return False
        except Exception as e:
            print(f"Delete task exception: {e}")
            return False

    def download_results(self, task_id, output_path):
        """Download all results as ZIP."""
        params = self._get_auth_params()
        base_url = self._get_base_url()

        try:
            response = requests.get(
                f'{base_url}/task/{task_id}/download/all.zip',
                params=params,
                timeout=600,
                stream=True
            )
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            return False
        except:
            return False
