import os
import sys
import threading
import socketserver
import networkx as nx
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QSpinBox, QPushButton, QTextEdit, QListWidget, QMenu, QMessageBox, QComboBox
)
from PyQt5.QtCore import QTimer, Qt, QUrl
import qdarktheme
from pysat.formula import CNF
from construction import SATGraph
from http.server import SimpleHTTPRequestHandler

G = SATGraph()

class SATGen(QWidget):
    def __init__(self):
        super().__init__()
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


class Constructor(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        main_layout = QVBoxLayout(self)
        op_layout = QHBoxLayout()
        self.parent = parent

        # Operation selection
        self.op = QComboBox()
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
        self.op.addItems(self.opcodes.keys())
        self.op.setCurrentIndex(-1)
        self.op.currentIndexChanged.connect(self.add_operation)

        self.op_list = QListWidget()
        self.op_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.op_list.customContextMenuRequested.connect(self.show_context_menu)
        self.operations = []

        op_layout.addWidget(QLabel("Select Operation:"))
        op_layout.addWidget(self.op)
        main_layout.addLayout(op_layout)
        main_layout.addWidget(QLabel("Selected Operations:"))
        main_layout.addWidget(self.op_list)

    def add_operation(self):
        selected_op = self.op.currentText()
        if selected_op:
            self.operations.append(selected_op)
            self.op_list.addItem(selected_op)
            self.rebuild_graph()

    def rebuild_graph(self):
        G.G = nx.Graph()
        for op in self.operations:
            try:
                self.opcodes[op]()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to apply operation '{op}': {e}")
        G.write()
        self.parent.graph_viewer.reload_webview()

    def show_context_menu(self, position):
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        action = menu.exec_(self.op_list.viewport().mapToGlobal(position))
        if action == delete_action:
            self.delete_operation()

    def delete_operation(self):
        selected_items = self.op_list.selectedItems()
        for item in selected_items:
            row = self.op_list.row(item)
            self.op_list.takeItem(row)
            del self.operations[row]
        self.rebuild_graph()


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

        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        self.setLayout(layout)
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

        # Left vertical layout for SAT Generator and Constructor
        left_layout = QVBoxLayout()

        # SAT Generator at the top
        self.sat_gen = SATGen()
        left_layout.addWidget(self.sat_gen)

        # Constructor below SAT Generator
        self.constructor = Constructor(self)
        left_layout.addWidget(self.constructor)

        # Add left layout to main layout
        main_layout.addLayout(left_layout, stretch=1)

        # Graph Viewer on the right
        self.graph_viewer = GraphViewer()
        main_layout.addWidget(self.graph_viewer, stretch=2)

        # Set up the window properties
        self.setWindowTitle("EISAT")
        self.resize(1200, 800)

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