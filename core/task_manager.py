# -*- coding: utf-8 -*-
"""Task management and monitoring."""

from qgis.PyQt.QtCore import QTimer, QObject, pyqtSignal
from qgis.core import Qgis


class TaskManager(QObject):
    """Manages ODM task lifecycle and monitoring."""

    status_changed = pyqtSignal(dict)
    progress_updated = pyqtSignal(str, int)
    task_completed = pyqtSignal(str)
    task_failed = pyqtSignal(str)

    def __init__(self, odm_connection, iface):
        super().__init__()
        self.odm = odm_connection
        self.iface = iface
        self.current_task_id = None
        self.status_timer = None
        self._progress_message = None

    def start_monitoring(self, task_id):
        """Start monitoring a task."""
        self.current_task_id = task_id

        if self.status_timer:
            self.status_timer.stop()

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._check_status)
        self.status_timer.start(3000)
        self._check_status()

    def stop_monitoring(self):
        """Stop monitoring."""
        if self.status_timer:
            self.status_timer.stop()
            self.status_timer = None
        self.current_task_id = None
        self._clear_progress()

    def _check_status(self):
        """Check current task status."""
        if not self.current_task_id:
            return

        task_info = self.odm.get_task_info(self.current_task_id)
        if not task_info:
            return

        self.status_changed.emit(task_info)

        status_field = task_info.get('status', {})
        status_code = status_field.get('code', 0) if isinstance(status_field, dict) else status_field
        progress = task_info.get('progress', 0)
        name = task_info.get('name', 'Unknown')

        if status_code == 20:  # RUNNING
            self._show_progress(name, progress)
        else:
            self._clear_progress()

        if status_code == 40:  # COMPLETED
            self.task_completed.emit(self.current_task_id)
            self.stop_monitoring()
        elif status_code in (30, 50):  # FAILED or CANCELED
            self.task_failed.emit(self.current_task_id)
            self.stop_monitoring()

    def _show_progress(self, name, progress):
        """Show progress in QGIS."""
        msg = f'ODM Processing: {name} - {int(progress)}% complete'
        self.iface.mainWindow().statusBar().showMessage(f'ODM: {name} - {int(progress)}%')

        if not self._progress_message:
            self._progress_message = self.iface.messageBar().createMessage(msg)
            self.iface.messageBar().pushWidget(self._progress_message, Qgis.Info, 0)
        else:
            self._progress_message.setText(msg)

        self.progress_updated.emit(name, progress)

    def _clear_progress(self):
        """Clear progress display."""
        self.iface.mainWindow().statusBar().clearMessage()
        if self._progress_message:
            self.iface.messageBar().popWidget(self._progress_message)
            self._progress_message = None
