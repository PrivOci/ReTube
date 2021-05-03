import React from "react";
import { useRouter } from "next/router";

import videoBoxes from "./SmallVideoBox";

import {fetchDataSWR } from "../utils";

import useSWR from "swr";

function VideoBoard() {
  const router = useRouter();
  console.log(router);

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

      <div className="grid gap-4 mt-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
        {(error || !data || !data.content || !data.content.length
          ? Array.from(new Array(3))
          : data.content
        ).map((item, index) => videoBoxes(item, index))}
      </div>
    </div>
  );
}

export default VideoBoard;
