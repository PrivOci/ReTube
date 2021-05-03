import React from "react";
import Link from "next/link";
import { useRouter } from "next/router";

import routes from "../routes/routes";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const Sidebar = () => {
  const router = useRouter();

  return (
    <div className="h-screen hidden lg:block my-4 ml-4 shadow-lg relative w-80">
      <div className="sidebar md:shadow transform -translate-x-full md:translate-x-0 transition-transform duration-150 ease-in relative bg-white dark:bg-gray-700 rounded-xl">
        <div className="flex flex-col sm:flex-row sm:justify-around">
          <div className="w-72 h-screen">
            <nav className="mt-10 px-6">
              <ul className="list-reset flex-1 mx-2 z-10">
                {routes.map((route, index) => (
                  <LinkItem
                    linkRoute={route}
                    currentPath = {router.asPath}
                    key={index}
                  />
                ))}
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>
  );
};

let LinkItem = ({ linkRoute, currentPath }) => (
  <li>
    <div
      className={
        "hover:text-gray-800 hover:bg-gray-100 flex items-center p-2 my-6 transition-colors dark:hover:text-white dark:hover:bg-gray-600 duration-200  text-gray-600 dark:text-gray-400 rounded-lg " +
        (linkRoute.path === currentPath
          ? " bg-gray-100 dark:bg-gray-600"
          : "")
      }
    >
      <Link href={linkRoute.path}>
        <a>
          <div>
            <FontAwesomeIcon icon={linkRoute.faIcon} size="lg" fixedWidth />
            <span className="mx-4 text-lg font-normal">{linkRoute.name}</span>
          </div>
        </a>
      </Link>
    </div>
  </li>
);

export default Sidebar;
