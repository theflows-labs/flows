from ..models.dag import DAG
from ..utils.yaml_generator import generate_yaml
from ..config.db import SessionLocal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DAGService:
    @staticmethod
    def get_all_dags():
        db = SessionLocal()
        try:
            return [dag.to_dict() for dag in db.query(DAG).all()]
        except Exception as e:
            logger.error(f"Error getting all DAGs: {str(e)}")
            raise
        finally:
            db.close()

    @staticmethod
    def get_dag(dag_id):
        db = SessionLocal()
        try:
            return db.query(DAG).get(dag_id)
        except Exception as e:
            logger.error(f"Error getting DAG {dag_id}: {str(e)}")
            raise
        finally:
            db.close()

    @staticmethod
    def create_dag(data):
        db = SessionLocal()
        try:
            if not data.get('name'):
                raise ValueError("DAG name is required")
            if not data.get('nodes'):
                raise ValueError("At least one node is required")

            # Convert empty strings to None for date fields
            start_date = None
            if data.get('startDate'):
                try:
                    start_date = datetime.fromisoformat(data['startDate'])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid start_date format: {data['startDate']}, using None")

            dag = DAG(
                name=data['name'],
                description=data.get('description', ''),
                schedule=data.get('schedule') or None,  # Convert empty string to None
                start_date=start_date,
                nodes=data['nodes'],
                edges=data.get('edges', [])
            )
            
            db.add(dag)
            db.commit()
            db.refresh(dag)
            return dag
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating DAG: {str(e)}")
            raise
        finally:
            db.close()

    @staticmethod
    def update_dag(dag_id, data):
        db = SessionLocal()
        try:
            dag = db.query(DAG).get(dag_id)
            if not dag:
                return None

            if 'name' in data:
                dag.name = data['name']
            if 'description' in data:
                dag.description = data['description']
            if 'schedule' in data:
                dag.schedule = data['schedule'] or None  # Convert empty string to None
            if 'startDate' in data:
                try:
                    dag.start_date = datetime.fromisoformat(data['startDate']) if data['startDate'] else None
                except (ValueError, TypeError):
                    logger.warning(f"Invalid start_date format: {data['startDate']}, keeping existing value")
            if 'nodes' in data:
                dag.nodes = data['nodes']
            if 'edges' in data:
                dag.edges = data['edges']

            db.commit()
            db.refresh(dag)
            return dag
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating DAG {dag_id}: {str(e)}")
            raise
        finally:
            db.close()

    @staticmethod
    def delete_dag(dag_id):
        db = SessionLocal()
        try:
            dag = db.query(DAG).get(dag_id)
            if dag:
                db.delete(dag)
                db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting DAG {dag_id}: {str(e)}")
            raise
        finally:
            db.close()

    @staticmethod
    def get_dag_yaml(dag_id):
        db = SessionLocal()
        try:
            dag = db.query(DAG).get(dag_id)
            if not dag:
                return None
            return generate_yaml(dag.to_dict())
        except Exception as e:
            logger.error(f"Error generating YAML for DAG {dag_id}: {str(e)}")
            raise
        finally:
            db.close() 