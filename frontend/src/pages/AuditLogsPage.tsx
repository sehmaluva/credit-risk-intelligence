import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Card, CardTitle } from "@/components/ui/Card";

export function AuditLogsPage() {
  const { data: logs } = useQuery({
    queryKey: ["audit"],
    queryFn: () => api.get("/audit/logs/").then((r) => r.data.results || r.data),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Audit Logs</h2>
      <Card>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-slate-500">
              <th className="pb-2">Time</th>
              <th>Actor</th>
              <th>Action</th>
              <th>Resource</th>
            </tr>
          </thead>
          <tbody>
            {(logs || []).map((l: { id: number; created_at: string; actor_email?: string; action: string; resource_type: string; resource_id: string }) => (
              <tr key={l.id} className="border-b">
                <td className="py-2">{new Date(l.created_at).toLocaleString()}</td>
                <td>{l.actor_email || "—"}</td>
                <td>{l.action}</td>
                <td>{l.resource_type} #{l.resource_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
