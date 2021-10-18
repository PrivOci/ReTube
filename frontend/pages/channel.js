import { fetchData } from "../utils";
import { useRouter } from "next/router";
import VideoBoard from "../components/VideoBoard";
import useSWR from "swr";
export default function channel() {
  const router = useRouter();
  const targetUrl = router.asPath;
  const { data } = useSWR(targetUrl, fetchData);

  return <VideoBoard data={data}/>;
}
