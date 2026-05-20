import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";

export function ReportsPage() {
  const qc = useQueryClient();
  const { data: reports } = useQuery({
    queryKey: ["reports"],
    queryFn: () => api.get("/reports/").then((r) => r.data.results || r.data),
  });

  const generate = useMutation({
    mutationFn: (type: string) => api.post("/reports/", { type }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reports"] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Reports</h2>
        <div className="flex gap-2">
          <Button onClick={() => generate.mutate("portfolio_summary")}>Portfolio Summary</Button>
          <Button variant="secondary" onClick={() => generate.mutate("officer_activity")}>
            Officer Activity
          </Button>
        </div>
      </div>
      <Card>
        <CardTitle>Generated Reports</CardTitle>
        <table className="mt-4 w-full text-sm">
          <thead>
            <tr className="border-b text-left text-slate-500">
              <th className="pb-2">Type</th>
              <th>Status</th>
              <th>Created</th>
              <th>Download</th>
            </tr>
          </thead>
          <tbody>
            {(reports || []).map((r: { id: number; type: string; status: string; created_at: string; file_url?: string }) => (
              <tr key={r.id} className="border-b">
                <td className="py-2 capitalize">{r.type.replace(/_/g, " ")}</td>
                <td>{r.status}</td>
                <td>{new Date(r.created_at).toLocaleString()}</td>
                <td>
                  {r.file_url && (
                    <a href={r.file_url} className="text-emerald-600 hover:underline">Download</a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
