import { useState } from "react";
import { useNavigate } from "react-router";
import { LogIn, UserPlus, Shield } from "lucide-react";
import { UserRole, RBAC_CONFIG } from "../types/user";
import { loginUser, registerUser } from "../services/api";
import { useAuth } from "../components/authContext/AuthContext";

export default function Auth() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("hr");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isRegister, setIsRegister] = useState(false);

  const { login } = useAuth();  // context
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) return;

    setIsLoading(true);
    setError("");

    try {
      const response = await loginUser({ username, password });

      if (response.message) {
        setError(response.message);
        return;
      }

      if (response?.username) {
        // Storing in Context 
        login({
          user: response.username,
          role: response.role || "hr",
          token: response.access_token
        });

        navigate("/dashboard");
      }
    } catch (err) {
      setError("Network error. Please check your connection.");
    } finally {
      setIsLoading(false);
    }
  };

  
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) return;

    setIsLoading(true);
    setError("");

    try {
      const res = await registerUser({ username, password, role });

      if (res?.message) {
        setError(res.message);
        return;
      }

      alert("✅ Registered successfully! Please login.");
      setIsRegister(false);
      setUsername("");
      setPassword("");
    } catch (err) {
      setError("Network error. Please check your connection.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        
        <div className="flex items-center justify-center mb-8">
          <div className="bg-indigo-600 p-3 rounded-full">
            {isRegister ? (
              <UserPlus className="w-8 h-8 text-white" />
            ) : (
              <LogIn className="w-8 h-8 text-white" />
            )}
          </div>
        </div>

        <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">
          {isRegister ? "Register" : "RAG Chatbot Login"}
        </h1>

        <p className="text-center text-gray-600 mb-8">
          Role-Based Access Control (RBAC)
        </p>

        <form
          onSubmit={isRegister ? handleRegister : handleLogin}
          className="space-y-6"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="Enter your username"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="Enter your password"
              required
            />
          </div>

          {isRegister && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Select Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as UserRole)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                {Object.entries(RBAC_CONFIG).map(([key, config]) => (
                  <option key={key} value={key}>
                    {config.label}
                  </option>
                ))}
              </select>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 disabled:bg-indigo-400"
          >
            {isLoading
              ? "Processing..."
              : isRegister
              ? "Register"
              : "Sign In"}
          </button>
        </form>

        <div className="text-center mt-4">
          {isRegister ? (
            <p className="text-sm">
              Already have an account?{" "}
              <span
                className="text-indigo-600 cursor-pointer font-medium"
                onClick={() => setIsRegister(false)}
              >
                Login
              </span>
            </p>
          ) : (
            <p className="text-sm">
              New user?{" "}
              <span
                className="text-indigo-600 cursor-pointer font-medium"
                onClick={() => {
                  setIsRegister(true);
                  setError("");
                }}
              >
                Register
              </span>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}