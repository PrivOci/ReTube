import React from "react";
import { useRouter } from "next/router";

import videoBoxes from "./SmallVideoBox";

import { fetchDataSWR } from "../utils";

import useSWR from "swr";

function VideoBoard() {
  const router = useRouter();

  let targetUrl = router.asPath;
  let search = targetUrl.split("search=")[1];

  const { data, error } = useSWR([targetUrl, search], fetchDataSWR);

  return (
    <div>
      {data && "suggestion" in data ? (
        <h3 className="text-md text-black dark:text-white antialiased sm:subpixel-antialiased">
          {`Do you mean: `}
          <span>
            <a
              href={`VideoBoard?search=${data.suggestion}`}
              alt="search"
              className="hover:underline text-blue-400 hover:text-blue-500"
            >
              {data.suggestion}
            </a>
          </span>
        </h3>
      ) : (
        <span />
      )}
      <div className="container px-5 py-5 mx-auto">
        <div className="flex flex-wrap -m-4">
          {(error || !data || !data.content || !data.content.length
            ? Array.from(new Array(3))
            : data.content
          ).map((item, index) => videoBoxes(item, index))}
        </div>
      </div>
    </div>
  );
}

export default VideoBoard;
