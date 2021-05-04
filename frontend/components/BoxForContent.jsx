import React from "react";

const BoxForContent = ({children}) => {
  return (
    <div className="shadow-lg justify-center rounded-2xl p-4 mt-2 bg-white dark:bg-gray-700 w-full text-black dark:text-white">
      {children}
    </div>
  );
};

export default BoxForContent;
