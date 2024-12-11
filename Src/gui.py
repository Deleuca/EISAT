import os
import sys
import threading
import socketserver
import networkx as nx
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QSpinBox, QPushButton, QTextEdit,
    QListWidget, QMenu, QMessageBox, QAbstractItemView, QSizePolicy
)
from PyQt5.QtCore import QTimer, Qt, QUrl
import qdarktheme
from pysat.formula import CNF
from construction import SATGraph
from http.server import SimpleHTTPRequestHandler

G = SATGraph()

class SATGen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.cnf = CNF()

        main_layout = QVBoxLayout(self)

        # SAT Generator label
        sat_label = QLabel("SAT Generator")
        sat_label.setAlignment(Qt.AlignCenter)
        sat_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(sat_label)

        # Input controls for clauses and variables
        gen_layout = QHBoxLayout()
        self.num_clause = QSpinBox()
        self.num_clause.setRange(1, 30)
        self.num_clause.setValue(3)
        self.num_clause.setToolTip("Number of Clauses")

        self.num_var = QSpinBox()
        self.num_var.setRange(1, 120)
        self.num_var.setValue(3)
        self.num_var.setToolTip("Number of Variables")

        gen_button = QPushButton("Generate")
        gen_button.clicked.connect(self.generate)

        gen_layout.addWidget(QLabel("Number of Clauses:"))
        gen_layout.addWidget(self.num_clause)
        gen_layout.addWidget(QLabel("Number of Variables:"))
        gen_layout.addWidget(self.num_var)
        gen_layout.addWidget(gen_button)
        main_layout.addLayout(gen_layout)

        # Display area for CNF
        self.view_sat = QTextEdit()
        self.view_sat.setReadOnly(True)
        self.view_sat.setFont(QFont("CMU Bright", 16))
        main_layout.addWidget(self.view_sat)

    def generate(self):
        try:
            G.generate_random_cnf(self.num_clause.value(), self.num_var.value())
            self.cnf = G.cnf
            self.display_cnf()

            # After generating CNF, rebuild the graph
            if self.parent:
                self.parent.constructor.rebuild_graph()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate CNF: {e}")

    def display_cnf(self):
        formatted_clauses = []
        for clause in self.cnf.clauses:
            formatted_clause = " &nbsp;&nbsp;&nbsp; ".join(
                [f" x<sub>{abs(lit)}</sub>" if lit > 0 else f"-x<sub>{abs(lit)}</sub>" for lit in clause]
            )
            formatted_clauses.append(f"{formatted_clause}")
        self.view_sat.setHtml("<br>".join(formatted_clauses))


class SelectedOpsListWidget(QListWidget):
    def __init__(self, parent_constructor):
        super().__init__()
        self.parent_constructor = parent_constructor
        self.setSelectionMode(QListWidget.SingleSelection)
        # Enable accepting external drops and internal reordering
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("background: #404040; color: #FFFFFF;")

    def dragEnterEvent(self, event):
        # If dragging from available ops, we will use CopyAction in dropEvent
        # For internal moves, we can just accept proposed action.
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        source = event.source()
        if source is not None and source != self:
            # External drop (from available ops)
            item = source.currentItem()
            if item:
                # We copy the item from available ops
                self.addItem(item.text())
                event.setDropAction(Qt.CopyAction)
                event.accept()
                self.parent_constructor.rebuild_graph()
        else:
            # Internal reorder: just let the default behavior handle it
            event.acceptProposedAction()
            super().dropEvent(event)
            self.parent_constructor.rebuild_graph()


class Constructor(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        main_layout = QVBoxLayout(self)

        # Dictionary of available operations
        self.opcodes = {
            "Clause to Clique": G.clause_to_clique,
            "Clause to Cluster": G.clause_to_cluster,
            "Literal to Node": G.literal_to_node,
            "Literal and Negation to Node": G.literal_and_negation_to_node,
            "Variable to Node": G.variable_to_node,
            "All to All": G.all_to_all,
            "X to X": G.x_to_x,
            "X to Not X": G.x_to_not_x,
            "X to All But X": G.x_to_all_but_x,
            "X to All But Not X": G.x_to_all_but_not_x,
        }

        # Title
        title_label = QLabel("Operations Constructor")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Instructions
        instructions_label = QLabel("Drag operations from 'Available Operations' to 'Selected Operations'.\n"
                                    "You can reorder 'Selected Operations' via drag and drop.\n"
                                    "Each modification rebuilds the graph.")
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet("font-size: 12px;")
        main_layout.addWidget(instructions_label)

        # Layout for operations lists
        ops_layout = QHBoxLayout()

        # Left layout for available ops
        available_layout = QVBoxLayout()
        available_label = QLabel("Available Operations:")
        available_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        available_layout.addWidget(available_label)

        self.available_ops_list = QListWidget()
        self.available_ops_list.setSelectionMode(QListWidget.SingleSelection)
        self.available_ops_list.setDragEnabled(True)
        self.available_ops_list.setDragDropMode(QAbstractItemView.DragOnly)
        self.available_ops_list.setAlternatingRowColors(True)
        self.available_ops_list.setStyleSheet("background: #303030; color: #FFFFFF;")

        # Populate available ops
        for op in self.opcodes.keys():
            self.available_ops_list.addItem(op)

        available_layout.addWidget(self.available_ops_list)

        # Right layout for selected ops
        selected_layout = QVBoxLayout()
        selected_label = QLabel("Selected Operations:")
        selected_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        selected_layout.addWidget(selected_label)

        self.selected_ops_list = SelectedOpsListWidget(self)
        self.selected_ops_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.selected_ops_list.customContextMenuRequested.connect(self.show_context_menu)

        # Connect signals for internal reordering from model
        self.selected_ops_list.model().rowsMoved.connect(self.on_reorder_operations)

        selected_layout.addWidget(self.selected_ops_list)

        ops_layout.addLayout(available_layout)
        ops_layout.addLayout(selected_layout)
        main_layout.addLayout(ops_layout)

        # Store selected operations
        self.operations = []

    def show_context_menu(self, position):
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        action = menu.exec_(self.selected_ops_list.viewport().mapToGlobal(position))
        if action == delete_action:
            self.delete_operation()

    def delete_operation(self):
        selected_items = self.selected_ops_list.selectedItems()
        for item in selected_items:
            row = self.selected_ops_list.row(item)
            self.selected_ops_list.takeItem(row)
        self.rebuild_graph()

    def on_reorder_operations(self):
        # Called after internal move
        self.rebuild_graph()

    def rebuild_graph(self):
        # Clear the graph
        G.G = nx.Graph()

        # Build operations array from the selected_ops_list
        self.operations = []
        for i in range(self.selected_ops_list.count()):
            self.operations.append(self.selected_ops_list.item(i).text())

        # Apply operations in order
        for op in self.operations:
            try:
                self.opcodes[op]()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to apply operation '{op}': {e}")

        # Write and reload the graph
        G.write()
        if self.parent:
            self.parent.graph_viewer.reload_webview()


class GraphViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.httpd = None
        self.server_port = None
        self.start_local_server()

        self.webview = QWebEngineView()
        self.webview.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.webview.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.webview.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.webview.settings().setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        self.webview.setStyleSheet("background-color: #202124;")

        # Make the webview expand with the window
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create the toggle button
        self.toggle_button = QPushButton("Switch to Static View")
        self.toggle_button.setStyleSheet(
            "background-color: #444; color: white; border-radius: 5px; padding: 5px;"
        )
        self.toggle_button.clicked.connect(self.toggle_view)

        # Create the unintimidate button (hidden initially)
        self.unintimidate_button = QPushButton("Unintimidate")
        self.unintimidate_button.setStyleSheet(
            "background-color: #555; color: white; border-radius: 5px; padding: 5px;"
        )
        self.unintimidate_button.clicked.connect(self.toggle_curved_view)
        self.unintimidate_button.hide()

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.unintimidate_button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.setLayout(layout)

        # State variables to track the current view
        self.is_dynamic_view = True
        self.is_curved_view = False

        QTimer.singleShot(1000, self.load_webview)

    def start_local_server(self):
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data'))
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
        os.chdir(data_dir)

        def run_server():
            with socketserver.TCPServer(("localhost", 0), SimpleHTTPRequestHandler) as httpd:
                self.server_port = httpd.server_address[1]
                print(f"Serving at port {self.server_port}")
                self.httpd = httpd
                httpd.serve_forever()

        threading.Thread(target=run_server, daemon=True).start()

    def load_webview(self):
        if self.server_port:
            server_url = f"http://localhost:{self.server_port}/vis.html"
            self.webview.setUrl(QUrl(server_url))
        else:
            QMessageBox.critical(self, "Error", "Failed to load Graph Viewer. Server not started.")

    def toggle_view(self):
        if self.server_port:
            if self.is_dynamic_view:
                server_url = f"http://localhost:{self.server_port}/static-vis.html"
                self.toggle_button.setText("Switch to Dynamic View")
                self.unintimidate_button.show()
                self.is_curved_view = False
                self.unintimidate_button.setText("Unintimidate")
            else:
                server_url = f"http://localhost:{self.server_port}/vis.html"
                self.toggle_button.setText("Switch to Static View")
                self.unintimidate_button.hide()

            self.webview.setUrl(QUrl(server_url))
            self.is_dynamic_view = not self.is_dynamic_view
        else:
            QMessageBox.critical(self, "Error", "Failed to toggle views. Server not started.")

    def toggle_curved_view(self):
        if self.server_port:
            if not self.is_curved_view:
                server_url = f"http://localhost:{self.server_port}/static-vis-curved.html"
                self.unintimidate_button.setText("Intimidate")
            else:
                server_url = f"http://localhost:{self.server_port}/static-vis.html"
                self.unintimidate_button.setText("Unintimidate")

            self.webview.setUrl(QUrl(server_url))
            self.is_curved_view = not self.is_curved_view
        else:
            QMessageBox.critical(self, "Error", "Failed to load curved static view. Server not started.")

    def reload_webview(self):
        self.webview.reload()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main horizontal layout
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # Graph Viewer on the right
        self.graph_viewer = GraphViewer()

        # Left vertical layout for SAT Generator and Constructor
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0,0,0,0)
        left_layout.setSpacing(0)

        # Constructor
        self.constructor = Constructor(self)
        left_layout.addWidget(self.constructor)

        # SAT Generator at the top
        self.sat_gen = SATGen(parent=self)
        # Insert SAT generator at top
        left_layout.insertWidget(0, self.sat_gen)

        # Add left layout to main layout
        left_side_widget = QWidget()
        left_side_widget.setLayout(left_layout)
        left_side_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(left_side_widget, stretch=1)
        main_layout.addWidget(self.graph_viewer, stretch=2)

        # Set up the window properties
        self.setWindowTitle("EISAT")
        self.resize(1800, 1200)

    def closeEvent(self, event):
        graph_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data', 'graph.json'))
        if os.path.exists(graph_json_path):
            os.remove(graph_json_path)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())