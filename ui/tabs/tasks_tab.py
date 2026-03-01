# -*- coding: utf-8 -*-
"""Tasks tab for managing ODM tasks."""
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QListWidget, QComboBox,
    QScrollArea, QMessageBox
)
from ...utils.helpers import parse_task_id, get_status_text

class TasksTab(QWidget):
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

        controls_group = QGroupBox('Task Controls')
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(5, 5, 5, 5)
        btn_layout.setSpacing(3)
        self.refresh_btn = QPushButton('🔄 Refresh')
        self.refresh_btn.setMaximumWidth(80)
        self.refresh_btn.clicked.connect(self.load_tasks)
        self.delete_btn = QPushButton('🗑️ Delete')
        self.delete_btn.setMaximumWidth(80)
        self.delete_btn.clicked.connect(self.delete_task)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        controls_group.setLayout(btn_layout)
        layout.addWidget(controls_group)

        tasks_group = QGroupBox('Active Tasks')
        tasks_layout = QVBoxLayout()
        tasks_layout.setContentsMargins(5, 5, 5, 5)
        tasks_layout.setSpacing(3)
        self.tasks_list = QListWidget()
        self.tasks_list.setMaximumHeight(120)
        self.tasks_list.setMinimumHeight(60)
        self.tasks_list.itemClicked.connect(self.select_task)
        tasks_layout.addWidget(self.tasks_list)
        tasks_group.setLayout(tasks_layout)
        layout.addWidget(tasks_group)

        layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def load_tasks(self):
        tasks = self.parent_dialog.odm.get_tasks()
        self.tasks_list.clear()
        results_combo = self.parent_dialog.results_tab.task_combo
        results_combo.clear()
        results_combo.addItem('No task selected', '')
        for task in tasks:
            task_uuid = task.get('uuid', '')
            if not task_uuid:
                continue
            status_info = task.get('status', {})
            status_code = status_info.get('code', 0) if isinstance(status_info, dict) else status_info
            status_text = get_status_text(status_code)
            task_name = task.get('name', 'Task')
            item_text = f"{task_name} (ID: {task_uuid}) - {status_text}"
            self.tasks_list.addItem(item_text)
            combo_text = f"{task_name} - {status_text}"
            results_combo.addItem(combo_text, task_uuid)

    def select_task(self, item):
        task_text = item.text()
        task_id = parse_task_id(task_text)
        if task_id:
            self.parent_dialog.current_project = task_id
            self.delete_btn.setEnabled(True)
            self.parent_dialog.update_task_buttons()
        else:
            QMessageBox.warning(self, 'Parse Error', f'Could not extract task ID from: {task_text}')

    def delete_task(self):
        if not self.parent_dialog.current_project:
            QMessageBox.warning(self, 'Warning', 'No task selected.')
            return
        task_id = self.parent_dialog.current_project
        reply = QMessageBox.question(self, 'Confirm Delete', f'Delete task {task_id}?\n\nThis cannot be undone.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.parent_dialog.odm.delete_task(task_id):
                self.parent_dialog.processing_tab.status_text.append(f'✓ Task {task_id} deleted')
                self.parent_dialog.current_project = None
                self.delete_btn.setEnabled(False)
                self.parent_dialog.processing_tab.stop_btn.setEnabled(False)
                self.parent_dialog.task_manager.stop_monitoring()
                self.load_tasks()
                QMessageBox.information(self, 'Deleted', f'Task {task_id} deleted.')
            else:
                self.parent_dialog.processing_tab.status_text.append(f'✗ Failed to delete {task_id}')
