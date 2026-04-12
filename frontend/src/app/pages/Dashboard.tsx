import { useEffect } from "react";
import { useNavigate } from "react-router";
import { LogOut, MessageSquare, Shield, Lock } from "lucide-react";
import DepartmentCard from "../components/DepartmentCard";
import { Department, RBAC_CONFIG } from "../types/user";
import { logoutUser } from "../services/api";
import { useAuth } from "../components/authContext/AuthContext";

const departments: Department[] = [
  {
    id: "hr",
    name: "Human Resources",
    color: "bg-blue-500",
    icon: "👥",
    allowedRoles: ["hr", "executive"],
    description: "Employee data, payroll, policies, benefits",
  },
  {
    id: "marketing",
    name: "Marketing",
    color: "bg-purple-500",
    icon: "📢",
    allowedRoles: ["marketing", "executive"],
    description: "Campaigns, budgets, ROI",
  },
  {
    id: "finance",
    name: "Finance",
    color: "bg-green-500",
    icon: "💰",
    allowedRoles: ["finance", "executive"],
    description: "Reports, expenses, revenue",
  },
  {
    id: "engineering",
    name: "Engineering",
    color: "bg-orange-500",
    icon: "⚙️",
    allowedRoles: ["engineering", "executive"],
    description: "Architecture, deployments",
  },
  {
    id: "data",
    name: "Data Analytics",
    color: "bg-pink-500",
    icon: "📊",
    allowedRoles: ["data", "executive"],
    description: "Reports, ML models",
  },
];

export default function Dashboard() {
  const navigate = useNavigate();

  // 🔥 Context
  const { user, role, accessToken, logout } = useAuth();

  // 🔒 Protect route
  useEffect(() => {
    if (!user || !accessToken) {
      navigate("/");
    }
  }, [user, accessToken, navigate]);

  // 🚪 Logout
  const handleLogout = async () => {
    try {
      await logoutUser({
        username: user!,
        // token: accessToken!,
      });
    } catch (err) {
      console.error("Logout error:", err);
    }

    logout(); // 🔥 clear context
    navigate("/");
  };

  // ✅ RBAC logic (FIXED)
  const accessibleDepartments = departments.filter((dept) =>
    role ? dept.allowedRoles.includes(role) : false
  );

  const restrictedDepartments = departments.filter((dept) =>
    role ? !dept.allowedRoles.includes(role) : false
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* HEADER */}
      <header className="bg-white shadow-sm border-b-2 border-indigo-500">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <MessageSquare className="w-8 h-8 text-indigo-600" />
            <div>
              <h1 className="text-2xl font-bold">RAG Dashboard</h1>
              <p className="text-sm text-gray-600">RBAC + RAG System</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="font-medium">{user}</p>
              <div className="text-sm text-indigo-600 flex items-center gap-1">
                <Shield className="w-3 h-3" />
                {role && RBAC_CONFIG[role]?.label}
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded-lg"
            >
              <LogOut className="w-4 h-4" /> Logout
            </button>
          </div>
        </div>
      </header>

      {/* MAIN */}
      <main className="max-w-7xl mx-auto px-4 py-10">
        {/* ACCESS INFO */}
        <div className="mb-8 bg-white p-6 rounded-lg shadow border-l-4 border-indigo-500">
          <h2 className="text-xl font-semibold">
            Access Level: {role && RBAC_CONFIG[role]?.accessLevel}
          </h2>

          <p className="text-gray-600 mt-2">
            {role === "executive"
              ? "Full access to all departments"
              : "Access limited to your department"}
          </p>
        </div>

        {/* ACCESSIBLE */}
        <h2 className="text-xl font-semibold mb-4">Available Departments</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
          {accessibleDepartments.map((dept) => (
            <DepartmentCard key={dept.id} department={dept} accessible />
          ))}
        </div>

        {/* RESTRICTED */}
        {restrictedDepartments.length > 0 && (
          <>
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Lock className="w-5 h-5 text-gray-400" />
              Restricted
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {restrictedDepartments.map((dept) => (
                <DepartmentCard key={dept.id} department={dept} accessible={false} />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}