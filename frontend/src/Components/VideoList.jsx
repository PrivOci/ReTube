import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

import videoBoxes from "./SmallVideoBox";

import fetchVideos, { fetchPopularVideos, fetchSearchResults } from "../utils";

function VideoList({ location }) {
  const [videoData, setVideoDataState] = useState([]);
  const CurrentLocation = useLocation();

  console.log(location);
  let url = CurrentLocation.state
    ? CurrentLocation.state.url
    : location.search.split("url=")[1];
  url = decodeURI(url);

  let search = location.search.split("search=")[1];

  useEffect(() => {
    if (url === "popular") {
      fetchPopularVideos().then((response) => {
        console.log("popular video list updated");
        console.log(response);
        setVideoDataState(response);
      });
    } else if (search) {
      console.log("search term: " + search);
      fetchSearchResults(decodeURI(search)).then((response) => {
        console.log("search results updated");
        setVideoDataState(response);
      });
    } else {
      fetchVideos(url).then((response) => {
        console.log("video list updated");
        setVideoDataState(response);
      });
    }

    return () => {
      setVideoDataState([]);
    };
  }, [url, search]);

  return (
    <div className="grid gap-4 mt-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
      {(!videoData || !videoData.content || !videoData.content.length
        ? Array.from(new Array(3))
        : videoData.content
      ).map((item, index) => videoBoxes(item, index))}
    </div>
  );
}

export default VideoList;
