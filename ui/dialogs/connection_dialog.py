# -*- coding: utf-8 -*-
"""Connection settings dialog."""
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)

class ConnectionDialog(QDialog):
    def __init__(self, odm_connection, parent=None):
        super().__init__(parent)
        self.odm = odm_connection
        self.setWindowTitle('ODM Connection Settings')
        self.setModal(True)
        self.setFixedSize(300, 150)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel('URL:'))
        self.url_edit = QLineEdit(self.odm.base_url)
        self.url_edit.setPlaceholderText('http://localhost:3000')
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)

        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel('Token:'))
        self.token_edit = QLineEdit(self.odm.token)
        self.token_edit.setPlaceholderText('Authentication token (optional)')
        token_layout.addWidget(self.token_edit)
        layout.addLayout(token_layout)

        button_layout = QHBoxLayout()
        test_btn = QPushButton('Test')
        test_btn.clicked.connect(self._test_connection)
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self._save_connection)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(test_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _test_connection(self):
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, 'Connection', 'Please enter a URL.')
            return
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            self.url_edit.setText(url)
        token = self.token_edit.text().strip()
        self.odm.set_credentials(url, token)
        if self.odm.test_connection():
            QMessageBox.information(self, 'Connection', f'Successfully connected to {url}!')
        else:
            QMessageBox.critical(self, 'Connection', f'Failed to connect to {url}.\n\nPlease check:\n1. URL is correct\n2. ODM server is running\n3. No firewall blocking')

    def _save_connection(self):
        url = self.url_edit.text().strip()
        token = self.token_edit.text().strip()
        if url and not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        self.odm.set_credentials(url, token)
        self.accept()
