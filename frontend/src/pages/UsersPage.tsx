import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { Card, CardTitle } from "@/components/ui/Card";

export function UsersPage() {
  const { data: users } = useQuery({
    queryKey: ["users"],
    queryFn: () => api.get("/users/").then((r) => r.data.results || r.data),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">User Management</h2>
      <Card>
        <CardTitle>Users</CardTitle>
        <table className="mt-4 w-full text-sm">
          <thead>
            <tr className="border-b text-left text-slate-500">
              <th className="pb-2">Email</th>
              <th>Role</th>
              <th>Branch</th>
              <th>Active</th>
            </tr>
          </thead>
          <tbody>
            {(users || []).map((u: { id: number; email: string; role: string; branch: string; is_active: boolean }) => (
              <tr key={u.id} className="border-b">
                <td className="py-2">{u.email}</td>
                <td className="capitalize">{u.role.replace(/_/g, " ")}</td>
                <td>{u.branch}</td>
                <td>{u.is_active ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
