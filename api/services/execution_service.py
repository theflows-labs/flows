import subprocess
import threading
from datetime import datetime
from ..models.execution import Execution, ExecutionStatus
from ..models.dag import DAG
from ..config.db import SessionLocal
import logging

logger = logging.getLogger(__name__)

class ExecutionService:
    @staticmethod
    def get_all_executions():
        db = SessionLocal()
        try:
            return [execution.to_dict() for execution in db.query(Execution).all()]
        finally:
            db.close()

    @staticmethod
    def get_execution(execution_id):
        db = SessionLocal()
        try:
            return db.query(Execution).filter(Execution.id == execution_id).first()
        finally:
            db.close()

    @staticmethod
    def get_executions_by_dag(dag_id):
        db = SessionLocal()
        try:
            return [execution.to_dict() for execution in db.query(Execution).filter(Execution.dag_id == dag_id).all()]
        finally:
            db.close()

    @staticmethod
    def create_execution(dag_id):
        db = SessionLocal()
        try:
            execution = Execution(dag_id=dag_id)
            db.add(execution)
            db.commit()
            db.refresh(execution)
            return execution
        finally:
            db.close()

    @staticmethod
    def update_execution(execution_id, data):
        db = SessionLocal()
        try:
            execution = db.query(Execution).filter(Execution.id == execution_id).first()
            if not execution:
                return None

            if 'status' in data:
                execution.status = ExecutionStatus(data['status'])
            if 'result' in data:
                execution.result = data['result']
            if 'error' in data:
                execution.error = data['error']
            if 'end_time' in data:
                execution.end_time = data['end_time']

            db.commit()
            db.refresh(execution)
            return execution
        finally:
            db.close()

    @staticmethod
    def delete_execution(execution_id):
        db = SessionLocal()
        try:
            execution = db.query(Execution).filter(Execution.id == execution_id).first()
            if execution:
                db.delete(execution)
                db.commit()
        finally:
            db.close()

    @staticmethod
    def delete_executions_by_dag(dag_id):
        db = SessionLocal()
        try:
            executions = db.query(Execution).filter(Execution.dag_id == dag_id).all()
            for execution in executions:
                db.delete(execution)
            db.commit()
        finally:
            db.close()

    @staticmethod
    def trigger_execution(dag_id):
        db = SessionLocal()
        try:
            # Create execution record
            execution = Execution(dag_id=dag_id)
            db.add(execution)
            db.commit()
            db.refresh(execution)

            # Start execution in background thread
            thread = threading.Thread(
                target=ExecutionService._execute_dag,
                args=(execution.id,)
            )
            thread.start()

            return execution
        finally:
            db.close()

    @staticmethod
    def get_execution_status(execution_id):
        db = SessionLocal()
        try:
            execution = db.query(Execution).filter(Execution.id == execution_id).first()
            if not execution:
                return None
            return execution.to_dict()
        finally:
            db.close()

    @staticmethod
    def _execute_dag(execution_id):
        db = SessionLocal()
        try:
            execution = db.query(Execution).filter(Execution.id == execution_id).first()
            if not execution:
                return

            try:
                # Update status to running
                execution.status = ExecutionStatus.RUNNING
                db.commit()

                # Get DAG details
                dag = db.query(DAG).filter(DAG.id == execution.dag_id).first()
                if not dag:
                    raise ValueError(f"DAG {execution.dag_id} not found")

                # Execute DAG tasks in order
                for node in dag.nodes:
                    # Execute task based on type
                    if node['data']['type'] == 'python':
                        ExecutionService._execute_python_task(node)
                    elif node['data']['type'] == 'bash':
                        ExecutionService._execute_bash_task(node)
                    elif node['data']['type'] == 'sql':
                        ExecutionService._execute_sql_task(node)

                # Update execution status to success
                execution.status = ExecutionStatus.SUCCESS
                execution.end_time = datetime.utcnow()
                db.commit()

            except Exception as e:
                # Update execution status to failed
                execution.status = ExecutionStatus.FAILED
                execution.end_time = datetime.utcnow()
                execution.error = str(e)
                db.commit()
                logger.error(f"Error executing DAG {execution.dag_id}: {str(e)}")

        finally:
            db.close()

    @staticmethod
    def _execute_python_task(node):
        # Execute Python task using subprocess
        config = node['data'].get('config', {})
        cmd = [
            'python',
            '-c',
            f"from {config['python_callable'].split('.')[0]} import {config['python_callable'].split('.')[1]}; {config['python_callable'].split('.')[1]}(*{config.get('op_args', [])}, **{config.get('op_kwargs', {})})"
        ]
        subprocess.run(cmd, check=True)

    @staticmethod
    def _execute_bash_task(node):
        # Execute bash task
        config = node['data'].get('config', {})
        cmd = config.get('bash_command')
        if cmd:
            subprocess.run(cmd, shell=True, check=True)

    @staticmethod
    def _execute_sql_task(node):
        # Execute SQL task
        config = node['data'].get('config', {})
        # TODO: Implement SQL execution logic
        pass 