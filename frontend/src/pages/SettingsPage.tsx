import { useAuth } from "@/hooks/useAuth";
import { Card, CardTitle } from "@/components/ui/Card";

export function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h2 className="text-2xl font-bold">Settings</h2>
      <Card>
        <CardTitle>Profile</CardTitle>
        <dl className="mt-4 space-y-2 text-sm">
          <div className="flex justify-between"><dt className="text-slate-500">Email</dt><dd>{user?.email}</dd></div>
          <div className="flex justify-between"><dt className="text-slate-500">Role</dt><dd className="capitalize">{user?.role?.replace(/_/g, " ")}</dd></div>
          <div className="flex justify-between"><dt className="text-slate-500">Branch</dt><dd>{user?.branch}</dd></div>
        </dl>
      </Card>
      <Card>
        <CardTitle>Platform</CardTitle>
        <p className="mt-2 text-sm text-slate-500">
          Credit Risk Intelligence Platform v1.0 — LightGBM + SHAP explainability for emerging markets lending.
        </p>
      </Card>
    </div>
  );
}
