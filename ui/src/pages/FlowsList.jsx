import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import useFlowStore from '../stores/flowStore';

const FlowsList = () => {
  const { flows, fetchFlows, deleteFlow, error, loading } = useFlowStore();

  useEffect(() => {
    fetchFlows();
  }, [fetchFlows]);

  const handleDelete = async (flowId) => {
    try {
      await deleteFlow(flowId);
      // Optionally show success message
    } catch (error) {
      // Handle error
      console.error('Failed to delete flow:', error);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Flows</h1>
      <Link to="/flows/new">Create New Flow</Link>
      <div className="flow-list">
        {flows.map((flow) => (
          <div key={flow.flow_id} className="flow-item">
            <h3>{flow.flow_id}</h3>
            <p>{flow.description}</p>
            <div className="flow-actions">
              <Link to={`/flows/${flow.flow_id}`}>Edit</Link>
              <button onClick={() => handleDelete(flow.flow_id)}>Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FlowsList; 