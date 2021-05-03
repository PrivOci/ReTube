import React from "react";

const Content = ({ children }) => {
  return (
    <div className="flex flex-col w-full pl-0 md:p-4 md:space-y-4">
      <div className="min-h-full min-w-full max-w-full">{children}</div>
    </div>
  );
};

export default Content;
