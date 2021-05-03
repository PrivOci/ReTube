import dynamic from "next/dynamic";
const Watch = dynamic(
  () => import("../components/Watch"),
  { ssr: false }
);
export default function watch() {
  return (
    <div>
      <Watch />
    </div>
  );
}
