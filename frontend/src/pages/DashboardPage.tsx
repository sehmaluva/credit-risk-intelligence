import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { api } from "@/api/client";
import { Card, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatPercent } from "@/lib/utils";

const COLORS = ["#10b981", "#f59e0b", "#f97316", "#ef4444"];

export function DashboardPage() {
  const { data: overview } = useQuery({
    queryKey: ["analytics-overview"],
    queryFn: () => api.get("/analytics/overview/").then((r) => r.data),
  });
  const { data: apps } = useQuery({
    queryKey: ["applications"],
    queryFn: () => api.get("/applications/").then((r) => r.data.results || r.data),
  });

  const riskData = overview
    ? Object.entries(overview.risk_distribution || {}).map(([name, value]) => ({
        name,
        value: value as number,
      }))
    : [];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <p className="text-slate-500">Portfolio overview and recent activity</p>
      </div>
      <div className="grid gap-6 md:grid-cols-4">
        {[
          { label: "Total Applications", value: overview?.total_applications ?? 0 },
          { label: "Scored", value: overview?.scored_applications ?? 0 },
          { label: "Approval Rate", value: formatPercent(overview?.approval_rate ?? 0) },
          { label: "Portfolio Health", value: formatPercent(overview?.portfolio_health_score ?? 0) },
        ].map((kpi) => (
          <Card key={kpi.label}>
            <p className="text-sm text-slate-500">{kpi.label}</p>
            <p className="mt-2 text-3xl font-bold">{kpi.value}</p>
          </Card>
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardTitle>Risk Distribution</CardTitle>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                {riskData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
        <Card>
          <CardTitle>Recent Applications</CardTitle>
          <div className="mt-4 space-y-2">
            {(apps || []).slice(0, 8).map((app: Record<string, unknown>) => (
              <Link
                key={app.id as number}
                to={`/applications/${app.id}`}
                className="flex items-center justify-between rounded-lg border p-3 hover:bg-slate-50"
              >
                <span className="font-medium">{app.external_id as string}</span>
                <div className="flex items-center gap-2">
                  {app.latest_prediction ? (
                    <Badge variant={(app.latest_prediction as { risk_category: string }).risk_category}>
                      {(app.latest_prediction as { risk_category: string }).risk_category}
                    </Badge>
                  ) : null}
                  <span className="text-sm text-slate-500">{app.status as string}</span>
                </div>
              </Link>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
