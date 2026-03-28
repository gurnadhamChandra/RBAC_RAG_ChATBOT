
export type UserRole =
  | "hr"
  | "marketing"
  | "finance"
  | "engineering"
  | "data"
  | "executive"
  ;

export interface User {
  id: string;
  username: string;
  role: UserRole;
}

export interface Department {
  id: string;
  name: string;
  color: string;
  icon: string;
  allowedRoles: UserRole[];
  description: string;
}

// Role-based access control configuration
export const RBAC_CONFIG = {
  hr: {
    label: "Human Resources",
    accessLevel: "HR Team Access",
    allowedDepartments: ["hr"],
  },
  marketing: {
    label: "Marketing Team",
    accessLevel: "Marketing Team Access",
    allowedDepartments: ["marketing"],
  },
  finance: {
    label: "Finance Team",
    accessLevel: "Finance Team Access",
    allowedDepartments: ["finance"],
  },
  engineering: {
    label: "Engineering Team",
    accessLevel: "Engineering Team Access",
    allowedDepartments: ["engineering"],
  },
  data: {
    label: "Data Analytics Team",
    accessLevel: "Data Team Access",
    allowedDepartments: ["data"],
  },
  executive: {
    label: "C-Level Executive",
    accessLevel: "Full Access (All Departments)",
    allowedDepartments: ["hr", "marketing", "finance", "engineering", "data"],
  },
} as const;