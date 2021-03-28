import React from "react";
import { useLocation } from "react-router-dom";

import videoBoxes from "./SmallVideoBox";

import fetchVideos, { fetchPopularVideos, fetchSearchResults } from "../utils";

import useSWR from "swr";

const fetchDataSWR = async (url_search) => {
  const { url, search } = JSON.parse(url_search);

  if (url === "popular") {
    return fetchPopularVideos();
  } else if (search) {
    return fetchSearchResults(decodeURI(search));
  } else {
    return fetchVideos(url);
  }
};

function VideoList({ location }) {
  const CurrentLocation = useLocation();

  console.log(location);
  let url = CurrentLocation.state
    ? CurrentLocation.state.url
    : location.search.split("url=")[1];
  url = decodeURI(url);

  let search = location.search.split("search=")[1];

  const { data, error, isValidating, mutate } = useSWR(
    JSON.stringify({ url, search }),
    fetchDataSWR
  );

  return (
    <div className="grid gap-4 mt-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
      {(error || !data || !data.content || !data.content.length
        ? Array.from(new Array(3))
        : data.content
      ).map((item, index) => videoBoxes(item, index))}
    </div>
  );
}

export default VideoList;
