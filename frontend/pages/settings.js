import { ToastProvider } from "react-toast-notifications";
import dynamic from "next/dynamic";
const Settings = dynamic(() => import("../components/Settings"), {
  ssr: false,
});

export default function settings() {
  return (
    <ToastProvider>
      <Settings />
    </ToastProvider>
  );
}
