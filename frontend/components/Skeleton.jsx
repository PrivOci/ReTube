import React from "react";

const Skeleton = () => {
  return (
    <div className="each mb-10 m-2">
      <div className="flex space-x-4 animate-pulse">
        <div className="flex-1 py-1 space-y-4">
          <div className="w-full h-40 bg-gray-400 rounded"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-400 rounded"></div>
            <div className="w-5/6 h-4 bg-gray-400 rounded"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Skeleton;
