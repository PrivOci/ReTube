import React from "react";

const Navbar = () => {
  return (
    <div className="flex flex-col sm:flex-row sm:h-20 px-6 mb-1 rounded-2xl bg-white dark:bg-gray-700 relative z-50">
      <div className="h-20 w-full flex items-center justify-between sm:h-auto">
        <a className="no-underline block h-8" href="subscriptions">
          <h1 className="text-black dark:text-white">ReTube (todo)</h1>
        </a>
      </div>
      <div className="w-full mx-auto mt-2 mb-4 sm:mx-0 sm:mb-0 sm:mt-0 sm:absolute sm:left-1/2 sm:transform sm:-translate-x-1/2 sm:w-1/2 sm:h-full justify-center items-center block sm:flex">
        <form className="relative w-full">
          <div className="w-full h-10 pl-3 pr-2 bg-white border rounded-full flex justify-between items-center relative">
            <input
              type="search"
              name="search"
              id="search"
              placeholder="Search"
              className="appearance-none w-full outline-none focus:outline-none active:outline-none"
            />
            <button
              type="submit"
              formAction="search"
              className="ml-1 outline-none focus:outline-none active:outline-none"
            >
              <svg
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                className="w-6 h-6"
              >
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Navbar;
