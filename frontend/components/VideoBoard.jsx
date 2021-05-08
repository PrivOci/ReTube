import React from "react";
import videoBoxes from "./SmallVideoBox";
import Suggestion from "./Suggestion";

function VideoBoard({ data }) {
  return (
    <div>
      <Suggestion data={data} />
      <div className="container px-5 py-5 mx-auto">
        <div className="flex flex-wrap -m-4">
          {(!data || !data.content || !data.content.length
            ? Array.from(new Array(3))
            : data.ready
            ? data.content
            : [null, ...data.content]
          ).map((item, index) => videoBoxes(item, index))}
        </div>
      </div>
    </div>
  );
}

export default VideoBoard;
