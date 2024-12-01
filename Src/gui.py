import os
from pickletools import opcodes
import http.server
import threading
import socketserver
import networkx as nx
from PyQt5 import *
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
import matplotlib.pyplot as plt
from fontTools.merge import layoutPreMerge
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pysat.formula import CNF
from src.construction import SATGraph
import qdarktheme

G = SATGraph()
class LocalHTTPServer:
    def __init__(self, directory, port=8000):
        self.directory = directory
        self.port = port
        self.server_thread = None
        self.httpd = None

    def start(self):
        # Ensure the directory exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Configure the HTTP server
        handler = http.server.SimpleHTTPRequestHandler
        os.chdir(self.directory)

        # Try to bind to the specified port; use a free one if unavailable
        for port in range(self.port, self.port + 100):
            try:
                self.httpd = socketserver.TCPServer(("", port), handler)
                self.port = port  # Save the port used
                break
            except OSError:
                continue
        else:
            raise RuntimeError("No available ports in the range!")

        # Run the server in a separate thread
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        if self.server_thread:
            self.server_thread.join()


class SATGen(QWidget):
    def __init__(self):
        super().__init__()
        self.cnf = CNF()

        # Main layout
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

        # Add input controls to main layout
        main_layout.addLayout(gen_layout)

        # Display area for CNF
        self.view_sat = QTextEdit()
        self.view_sat.setReadOnly(True)
        self.view_sat.setFont(QFont("CMU Bright", 16))
        main_layout.addWidget(self.view_sat)

    def generate(self):
        # Generate random CNF
        G.generate_random_cnf(self.num_clause.value(), self.num_var.value())
        self.cnf = G.cnf

        # Display the CNF
        self.display_cnf()

    def display_cnf(self):
        # Format CNF clauses for display using HTML
        formatted_clauses = []
        for clause in self.cnf.clauses:
            formatted_clause = " &nbsp;&nbsp;&nbsp; ".join(
                [f" x<sub>{abs(lit)}</sub>" if lit > 0 else f"-x<sub>{abs(lit)}</sub>" for lit in clause]
            )
            formatted_clauses.append(f"{formatted_clause}")

        # Set the formatted HTML in the QTextEdit
        self.view_sat.setHtml("<br>".join(formatted_clauses))

class Constructor(QWidget):
    def __init__(self):
        super().__init__()

        # Layouts
        main_layout = QVBoxLayout(self)
        op_layout = QHBoxLayout()

        # ComboBox for selecting operations
        self.op = QComboBox()
        self.opcodes = {
            "Clause to Clique" : G.clause_to_clique,
            "Clause to Cluster": G.clause_to_cluster,
            "Literal to Node": G.literal_to_node,
            "Literal and Negation to Node": G.literal_and_negation_to_node,
            "Variable to Node": G.variable_to_node,
            "All to All": G.all_to_all,
            "X to X": G.x_to_x,
            "X to Not X": G.x_to_not_x,
            "X to All But X": G.x_to_all_but_x,
            "X to All But Not X": G.x_to_all_but_not_x,
            "Directed All to All": G.dir_all_to_all,
            "Directed X to All": G.dir_x_to_x,
            "Directed X to Not X": G.dir_x_to_not_x,
            "Directed X to All But X": G.dir_x_to_all_but_x,
            "Directed X to All But Not X": G.dir_x_to_all_but_not_x,
        }
        self.op.addItems(self.opcodes.keys())
        self.op.currentIndexChanged.connect(self.add_operation)

        # QListWidget to show added operations
        self.op_list = QListWidget()
        self.op_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.op_list.customContextMenuRequested.connect(self.show_context_menu)

        # Store selected operations in a list
        self.operations = []

        # Generate button to apply operations
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate)

        # Add widgets to the layout
        op_layout.addWidget(QLabel("Select Operation:"))
        op_layout.addWidget(self.op)

        main_layout.addLayout(op_layout)
        main_layout.addWidget(QLabel("Selected Operations:"))
        main_layout.addWidget(self.op_list)
        main_layout.addWidget(self.generate_button)

    def add_operation(self):
        # Get the selected operation
        selected_op = self.op.currentText()
        if selected_op:
            # Add the operation to the list and display it in the QListWidget
            self.operations.append(selected_op)
            self.op_list.addItem(selected_op)

    def show_context_menu(self, position):
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        action = menu.exec_(self.op_list.viewport().mapToGlobal(position))
        if action == delete_action:
            self.delete_operation()

    def delete_operation(self):
        selected_items = self.op_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            row = self.op_list.row(item)
            self.op_list.takeItem(row)
            del self.operations[row]

    def generate(self):
        G.G = nx.Graph()
        for op in self.operations:
            self.opcodes[op]()


class GraphViewer(QWidget):
    def __init__(self, http_port=8000):
        super().__init__()
        self.http_port = http_port
        self.figure = None
        self.canvas = None
        self.init_ui()

    def init_ui(self):
        # Set up the layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def refresh_plot(self):
        # Clear the previous plot if it exists
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.canvas = None

        # Update the graph dynamically from the current state of G.G
        self.figure = self.plot_graph(G.G)
        self.canvas = FigureCanvas(self.figure)

        # Add the canvas to the layout
        self.layout.addWidget(self.canvas)

    def plot_graph(self, graph):
        # Use the provided graph to create the plot
        pos = nx.kamada_kawai_layout(graph)
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(1, 1, 1)
        nx.draw(
            graph,
            pos,
            with_labels=True,
            font_weight='bold',
            node_size=1800,
            node_color='lightgreen',
            font_size=10,
            ax=ax
        )
        return fig

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_plot()

# Run the application
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    window = QMainWindow()
    tab_widget = QTabWidget()
    tab_widget.addTab(SATGen(), "SAT Generator")
    tab_widget.addTab(Constructor(), "Constructor")
    tab_widget.addTab(GraphViewer(), "Graph Viewer")
    window.setCentralWidget(tab_widget)
    window.setWindowTitle("SAT Generator")
    window.resize(500, 400)
    window.show()
    sys.exit(app.exec_())