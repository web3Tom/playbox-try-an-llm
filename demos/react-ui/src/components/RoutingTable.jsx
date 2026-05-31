import { routingRules } from '../data/models'

export default function RoutingTable() {
  return (
    <div className="routing-table-container">
      <table className="routing-table">
        <thead>
          <tr>
            <th>Task</th>
            <th>Model</th>
          </tr>
        </thead>
        <tbody>
          {routingRules.map((rule) => (
            <tr key={rule.id}>
              <td>{rule.task}</td>
              <td className="model-cell">{rule.model}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
