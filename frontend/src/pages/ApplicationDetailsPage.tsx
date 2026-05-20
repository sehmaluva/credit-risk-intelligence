import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatPercent } from "@/lib/utils";

export function ApplicationDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: app, isLoading } = useQuery({
    queryKey: ["application", id],
    queryFn: () => api.get(`/applications/${id}/`).then((r) => r.data),
  });

  const submit = useMutation({
    mutationFn: () => api.post(`/applications/${id}/submit/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["application", id] }),
  });

  const score = useMutation({
    mutationFn: () => api.post(`/applications/${id}/score/`),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["application", id] });
      navigate(`/applications/${id}/risk`);
    },
  });

  if (isLoading) return <p>Loading...</p>;
  if (!app) return <p>Not found</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">{app.external_id}</h2>
          <p className="text-slate-500">Status: {app.status}</p>
        </div>
        <div className="flex gap-2">
          {app.status === "draft" && (
            <Button onClick={() => submit.mutate()} disabled={submit.isPending}>Submit</Button>
          )}
          {(app.status === "submitted" || app.status === "scored") && (
            <Button onClick={() => score.mutate()} disabled={score.isPending}>
              {score.isPending ? "Scoring..." : "Run Risk Score"}
            </Button>
          )}
          {app.latest_prediction && (
            <Link to={`/applications/${id}/risk`}>
              <Button variant="secondary">View Risk Assessment</Button>
            </Link>
          )}
        </div>
      </div>
      {app.latest_prediction && (
        <Card className="border-emerald-200 bg-emerald-50">
          <div className="flex items-center gap-4">
            <Badge variant={app.latest_prediction.risk_category}>
              {app.latest_prediction.risk_category}
            </Badge>
            <span className="text-lg font-semibold">
              {formatPercent(app.latest_prediction.default_probability)} default probability
            </span>
            <span className="capitalize text-slate-600">
              → {app.latest_prediction.recommendation?.replace(/_/g, " ")}
            </span>
          </div>
        </Card>
      )}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardTitle>Applicant</CardTitle>
          <dl className="mt-4 space-y-2 text-sm">
            <Row label="Gender" value={app.client_gender} />
            <Row label="DOB" value={app.client_dob} />
            <Row label="Sector" value={app.employment_sector} />
            <Row label="Income" value={`$${app.monthly_income_usd}`} />
            <Row label="Province" value={app.province} />
          </dl>
        </Card>
        <Card>
          <CardTitle>Loan</CardTitle>
          <dl className="mt-4 space-y-2 text-sm">
            <Row label="Amount" value={`$${app.amount_usd}`} />
            <Row label="Rate" value={`${app.annual_rate_pct}%`} />
            <Row label="Term" value={`${app.term_months} months`} />
            <Row label="Purpose" value={app.loan_purpose} />
            <Row label="Collateral" value={app.collateral_type} />
          </dl>
        </Card>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <dt className="text-slate-500">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}
