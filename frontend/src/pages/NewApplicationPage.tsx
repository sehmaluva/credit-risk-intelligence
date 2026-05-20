import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/api/client";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";

const defaultForm = {
  product_code: 0,
  date_approved: new Date().toISOString().slice(0, 10),
  date_disbursed: new Date().toISOString().slice(0, 10),
  first_payment_due: null,
  maturity_date: null,
  amount_usd: 1000,
  annual_rate_pct: 24,
  term_months: 12,
  payment_frequency: "Monthly",
  loan_purpose: "Working_Capital",
  client_gender: "Male",
  client_dob: "1990-01-01",
  marital_status: "Single",
  num_dependents: 0,
  employment_sector: "Retail_Trade",
  months_at_employer: 12,
  monthly_income_usd: 500,
  existing_obligations: 0,
  collateral_type: "None",
  disbursement_channel: "EcoCash",
  province: "Harare",
};

export function NewApplicationPage() {
  const [form, setForm] = useState(defaultForm);
  const [step, setStep] = useState(0);
  const navigate = useNavigate();

  const update = (k: string, v: string | number) =>
    setForm((f) => ({ ...f, [k]: v }));

  const submit = async () => {
    const { data } = await api.post("/applications/", form);
    navigate(`/applications/${data.id}`);
  };

  const steps = ["Applicant", "Loan Details", "Review"];

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h2 className="text-2xl font-bold">New Loan Application</h2>
      <div className="flex gap-2">
        {steps.map((s, i) => (
          <span
            key={s}
            className={`rounded-full px-3 py-1 text-sm ${i === step ? "bg-emerald-600 text-white" : "bg-slate-200"}`}
          >
            {i + 1}. {s}
          </span>
        ))}
      </div>
      <Card>
        <CardTitle>{steps[step]}</CardTitle>
        {step === 0 && (
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <Field
              label="Gender"
              value={form.client_gender}
              onChange={(v) => update("client_gender", v)}
              options={["Male", "Female"]}
            />
            <Field
              label="Date of Birth"
              type="date"
              value={form.client_dob}
              onChange={(v) => update("client_dob", v)}
            />
            <Field
              label="Marital Status"
              value={form.marital_status}
              onChange={(v) => update("marital_status", v)}
              options={["Single", "Married", "Divorced", "Widowed"]}
            />
            <Field
              label="Dependents"
              type="number"
              value={form.num_dependents}
              onChange={(v) => update("num_dependents", Number(v))}
            />
            <Field
              label="Employment Sector"
              value={form.employment_sector}
              onChange={(v) => update("employment_sector", v)}
            />
            <Field
              label="Months at Employer"
              type="number"
              value={form.months_at_employer}
              onChange={(v) => update("months_at_employer", Number(v))}
            />
            <Field
              label="Monthly Income (USD)"
              type="number"
              value={form.monthly_income_usd}
              onChange={(v) => update("monthly_income_usd", Number(v))}
            />
            <Field
              label="Province"
              value={form.province}
              onChange={(v) => update("province", v)}
            />
          </div>
        )}
        {step === 1 && (
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <Field
              label="Product Code"
              type="number"
              value={form.product_code}
              onChange={(v) => update("product_code", Number(v))}
            />
            <Field
              label="Amount (USD)"
              type="number"
              value={form.amount_usd}
              onChange={(v) => update("amount_usd", Number(v))}
            />
            <Field
              label="Annual Rate %"
              type="number"
              value={form.annual_rate_pct}
              onChange={(v) => update("annual_rate_pct", Number(v))}
            />
            <Field
              label="Term (months)"
              type="number"
              value={form.term_months}
              onChange={(v) => update("term_months", Number(v))}
            />
            <Field
              label="Loan Purpose"
              value={form.loan_purpose}
              onChange={(v) => update("loan_purpose", v)}
            />
            <Field
              label="Collateral"
              value={form.collateral_type}
              onChange={(v) => update("collateral_type", v)}
            />
            <Field
              label="Existing Obligations"
              type="number"
              value={form.existing_obligations}
              onChange={(v) => update("existing_obligations", Number(v))}
            />
            <Field
              label="Disbursement Channel"
              value={form.disbursement_channel}
              onChange={(v) => update("disbursement_channel", v)}
            />
          </div>
        )}
        {step === 2 && (
          <pre className="mt-4 overflow-auto rounded bg-slate-100 p-4 text-xs">
            {JSON.stringify(form, null, 2)}
          </pre>
        )}
        <div className="mt-6 flex justify-between">
          <Button
            variant="ghost"
            disabled={step === 0}
            onClick={() => setStep((s) => s - 1)}
          >
            Back
          </Button>
          {step < 2 ? (
            <Button onClick={() => setStep((s) => s + 1)}>Next</Button>
          ) : (
            <Button onClick={submit}>Create Application</Button>
          )}
        </div>
      </Card>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  options,
}: {
  label: string;
  value: string | number;
  onChange: (v: string) => void;
  type?: string;
  options?: string[];
}) {
  return (
    <div>
      <label className="text-sm font-medium">{label}</label>
      {options ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="mt-1 w-full rounded-lg border px-3 py-2"
        >
          {options.map((o) => (
            <option key={o}>{o}</option>
          ))}
        </select>
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="mt-1 w-full rounded-lg border px-3 py-2"
        />
      )}
    </div>
  );
}
