import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { api } from "@/api/client";
import { Card, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatPercent } from "@/lib/utils";

export function RiskAssessmentPage() {
  const { id } = useParams();

  const { data: app } = useQuery({
    queryKey: ["application", id],
    queryFn: () => api.get(`/applications/${id}/`).then((r) => r.data),
  });

  const predId = app?.latest_prediction?.id;
  const { data: prediction } = useQuery({
    queryKey: ["prediction", predId],
    queryFn: () => api.get(`/predictions/${predId}/`).then((r) => r.data),
    enabled: !!predId,
  });

  const { data: shap } = useQuery({
    queryKey: ["shap", predId],
    queryFn: () => api.get(`/predictions/${predId}/shap/`).then((r) => r.data),
    enabled: !!predId,
  });

  if (!prediction) return <p>Run scoring first from application details.</p>;

  const chartData = (prediction.risk_factors || []).map((f: { feature_name: string; shap_value: number }) => ({
    name: f.feature_name.replace(/_/g, " "),
    value: Math.abs(f.shap_value),
    fill: f.shap_value > 0 ? "#ef4444" : "#10b981",
  }));

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold">Risk Assessment — {app?.external_id}</h2>
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <p className="text-sm text-slate-500">Default Probability</p>
          <p className="mt-2 text-4xl font-bold text-slate-900">
            {formatPercent(prediction.default_probability)}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-slate-500">Risk Category</p>
          <Badge variant={prediction.risk_category} className="mt-2 text-lg">
            {prediction.risk_category}
          </Badge>
        </Card>
        <Card>
          <p className="text-sm text-slate-500">Confidence</p>
          <p className="mt-2 text-4xl font-bold">{(prediction.confidence_score * 100).toFixed(0)}%</p>
        </Card>
      </div>
      <Card>
        <CardTitle>Recommendation</CardTitle>
        <p className="mt-2 text-xl font-semibold capitalize text-emerald-700">
          {prediction.recommendation?.replace(/_/g, " ")}
        </p>
        <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-slate-600">
          {(prediction.recommendation_rationale?.rationale || []).map((r: string, i: number) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </Card>
      <Card>
        <CardTitle>SHAP Feature Importance</CardTitle>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 120 }}>
            <XAxis type="number" />
            <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="value">
              {chartData.map((entry: { fill: string }, i: number) => (
                <Cell key={i} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>
      <Card>
        <CardTitle>Top Risk Factors</CardTitle>
        <table className="mt-4 w-full text-sm">
          <thead>
            <tr className="border-b text-left text-slate-500">
              <th className="pb-2">Feature</th>
              <th>SHAP</th>
              <th>Direction</th>
            </tr>
          </thead>
          <tbody>
            {(prediction.risk_factors || []).map((f: { feature_name: string; shap_value: number; direction: string }) => (
              <tr key={f.feature_name} className="border-b">
                <td className="py-2">{f.feature_name}</td>
                <td>{f.shap_value.toFixed(4)}</td>
                <td className="capitalize">{f.direction.replace(/_/g, " ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
