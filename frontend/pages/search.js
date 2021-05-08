import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import useSWR from "swr";
import {
  checkSentence,
  fetchSearchAPi,
  YOUTUBE_SEARCH,
  YOUTUBE_SEARCH_CHANNELS,
  LBRY_SEARCH,
  LBRY_SEARCH_CHANNELS,
  BITCHUTE_SEARCH,
} from "../utils";
import VideoBoard from "../components/VideoBoard";
export default function search() {
  const router = useRouter();
  let [videoData, setVideoDataState] = useState();

  const fetchSearchVideos = async (searchQuery, setVideoDataState) => {
    console.log(`searching: ${searchQuery}`);
    const checkQuery = checkSentence(searchQuery);

    let allWait = [];
    allWait.push(fetchSearchAPi(YOUTUBE_SEARCH_CHANNELS, searchQuery));
    allWait.push(fetchSearchAPi(LBRY_SEARCH_CHANNELS, searchQuery));
    allWait.push(fetchSearchAPi(YOUTUBE_SEARCH, searchQuery));
    allWait.push(fetchSearchAPi(LBRY_SEARCH, searchQuery));
    allWait.push(fetchSearchAPi(BITCHUTE_SEARCH, searchQuery));
    let allSearch = {};
    allSearch.platform = "search";
    allSearch.ready = false;
    allSearch.content = [];
    for (const waitSub of allWait) {
      const result = await waitSub;
      if (!result || result.ready === false) {
        continue;
      }
      allSearch.content = allSearch.content.concat(result.content);
      setVideoDataState();
      setVideoDataState(allSearch);
    }
    allSearch.ready = true;

    const checkResult = await checkQuery;
    if (checkResult.need_change) {
      allSearch.suggestion = checkResult.result;
    }
    setVideoDataState();
    setVideoDataState(allSearch);
  };

  useEffect(() => {
    const targetUrl = router.asPath;
    if (!targetUrl.includes("search=")) {
      router.push("/popular");
    }
    const searchQuery = targetUrl.split("search=")[1];

    fetchSearchVideos(searchQuery, setVideoDataState);

    return () => {
      setVideoDataState([]);
    };
  }, []);

  return <VideoBoard data={videoData} />;
}
