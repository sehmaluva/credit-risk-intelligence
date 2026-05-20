import { useQuery } from "@tanstack/react-query";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { api } from "@/api/client";
import { Card, CardTitle } from "@/components/ui/Card";

export function AnalyticsPage() {
  const { data: trends } = useQuery({
    queryKey: ["analytics-trends"],
    queryFn: () => api.get("/analytics/trends/").then((r) => r.data),
  });
  const { data: defaults } = useQuery({
    queryKey: ["analytics-defaults"],
    queryFn: () => api.get("/analytics/defaults/").then((r) => r.data),
  });

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold">Portfolio Analytics</h2>
      <Card>
        <CardTitle>Prediction Trends</CardTitle>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={trends || []}>
            <XAxis dataKey="day" tick={{ fontSize: 10 }} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="avg_probability" stroke="#10b981" name="Avg Probability" />
            <Line type="monotone" dataKey="count" stroke="#6366f1" name="Volume" />
          </LineChart>
        </ResponsiveContainer>
      </Card>
      <Card>
        <CardTitle>Risk by Province</CardTitle>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={(defaults?.by_province || []).slice(0, 10)}>
            <XAxis dataKey="application__province" tick={{ fontSize: 10 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="avg_probability" fill="#f97316" name="Avg Default Prob" />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}
