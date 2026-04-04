import { Navigate, Route, Routes } from "react-router-dom";
import { AppProvider } from "./context";
import { ShellLayout } from "./ShellLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { DriftPage } from "./pages/DriftPage";
import { QuickTasksPage } from "./pages/QuickTasksPage";
import { VerificationPage } from "./pages/VerificationPage";
import { SettingsPage } from "./pages/SettingsPage";
import { DocsPage } from "./pages/DocsPage";

export default function App() {
  return (
    <AppProvider>
      <ShellLayout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/docs" element={<DocsPage />} />
          <Route path="/drift" element={<DriftPage />} />
          <Route path="/quick-tasks" element={<QuickTasksPage />} />
          <Route path="/verification" element={<VerificationPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </ShellLayout>
    </AppProvider>
  );
}
