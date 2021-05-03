import dynamic from "next/dynamic";
const JsonEdit = dynamic(
  () => import("../components/JsonEdit"),
  { ssr: false }
);
export default function json() {
  return (
    <div>
      <JsonEdit />
    </div>
  );
}
