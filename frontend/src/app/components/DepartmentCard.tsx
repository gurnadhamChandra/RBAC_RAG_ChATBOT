import { useNavigate } from "react-router";
import { ArrowRight, Lock } from "lucide-react";
import { Department } from "../types/user";

interface DepartmentCardProps {
  department: Department;
  accessible: boolean;
}

export default function DepartmentCard({ department, accessible }: DepartmentCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (accessible) {
      navigate(`/chat/${department.id}`);
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`bg-white rounded-lg shadow-md transition-all p-6 ${
        accessible 
          ? "hover:shadow-xl cursor-pointer group" 
          : "opacity-60 cursor-not-allowed"
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`${department.color} w-16 h-16 rounded-lg flex items-center justify-center text-3xl ${!accessible && 'grayscale'}`}>
          {department.icon}
        </div>
        {!accessible && (
          <div className="bg-red-100 p-2 rounded-full">
            <Lock className="w-4 h-4 text-red-600" />
          </div>
        )}
      </div>
      <h3 className="text-xl font-semibold text-gray-800 mb-2">
        {department.name}
      </h3>
      <p className="text-gray-600 mb-4 text-sm">
        {department.description}
      </p>
      {accessible ? (
        <div className="flex items-center text-indigo-600 group-hover:gap-2 transition-all">
          <span className="font-medium">Start Chat</span>
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </div>
      ) : (
        <div className="flex items-center text-red-600 gap-2">
          <Lock className="w-4 h-4" />
          <span className="font-medium text-sm">Access Denied (RBAC)</span>
        </div>
      )}
    </div>
  );
}