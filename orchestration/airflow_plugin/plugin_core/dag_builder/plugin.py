"""
Airflow plugin for loading DAGs from the database.
"""
from airflow.plugins_manager import AirflowPlugin
from airflow.models import DagBag

from flows.plugin_core.dag_builder.loader import DAGLoader

class TheFlowsPlugin(AirflowPlugin):
    """Airflow plugin for loading DAGs from the database."""
    
    name = "theflows_plugin"
    hooks = []
    operators = []
    sensors = []
    macros = []
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self.dag_loader = DAGLoader()
    
    def on_load(self):
        """
        Called when the plugin is loaded.
        
        This method is called by Airflow when the plugin is loaded.
        It discovers operator factories and loads DAGs from the database.
        """
        # Discover operator factories
        self.dag_loader.discover_operator_factories("plugins.aws.athena.operators")
        self.dag_loader.discover_operator_factories("plugins.aws.s3.operators")
        
        # Load DAGs
        dags = self.dag_loader.load_dags()
        
        # Add DAGs to the DagBag
        dagbag = DagBag(dag_folder=None, include_examples=False)
        for dag_id, dag in dags.items():
            dagbag.dags[dag_id] = dag 